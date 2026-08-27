#!/usr/bin/env python3

"""
Batch retrieve PubChem XLogP values from CIDs contained in a
large Zstandard-compressed TSV file.

Input:
    classyfire_dedup_inchikey_smiles.enriched.tsv.zst

Expected columns:
    inchikey
    cid
    zinc_id
    smiles
    chemont_tree_json
    chemont_other_json

Output:
    pubchem_xlogp.tsv

Output columns:
    cid
    xlogp
    status

Requirements:
    pip install zstandard requests
"""

import csv
import io
import os
import sys
import time
import requests
import zstandard as zstd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_ZST = "classyfire_dedup_inchikey_smiles.enriched.tsv.zst"

OUTPUT_FILE = "pubchem_xlogp.tsv"

# Number of CIDs sent to PubChem in one POST request.
#
# 100 is conservative and reliable.
# You can try 200-500 if your connection is stable.
BATCH_SIZE = 100

# PubChem requests should not exceed 5 requests/second.
# 0.25 sec between requests = maximum theoretical 4 req/sec.
REQUEST_DELAY = 0.30

# Number of retries after HTTP/network failure
MAX_RETRIES = 5

# Timeout for each request
REQUEST_TIMEOUT = 60

# Progress reporting
PROGRESS_EVERY = 100_000


PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/cid/property/XLogP/CSV"
)


# ============================================================
# LOAD PREVIOUS RESULTS
# ============================================================

def load_existing_results(filename):
    """
    Load CIDs already processed.

    This makes the program resumable.
    """

    processed = set()

    if not os.path.exists(filename):
        return processed

    print(f"Reading existing results: {filename}")

    with open(
        filename,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            cid = row.get("cid")

            if cid:
                processed.add(cid)

    print(
        f"Already processed: {len(processed):,} CIDs"
    )

    return processed


# ============================================================
# PUBCHEM REQUEST
# ============================================================

def query_pubchem_xlogp(cids, session):
    """
    Query PubChem for a batch of CIDs.

    Uses POST because large CID lists should not be placed
    into the URL.

    Returns:

        {
            "1": 0.35,
            "2": 1.23,
            ...
        }

    """

    cid_string = ",".join(cids)

    data = {
        "cid": cid_string
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.post(
                PUBCHEM_URL,
                data=data,
                timeout=REQUEST_TIMEOUT
            )

            # ------------------------------------------------
            # Success
            # ------------------------------------------------

            if response.status_code == 200:

                results = {}

                text = response.text

                reader = csv.DictReader(
                    io.StringIO(text)
                )

                for row in reader:

                    cid = row.get("CID")

                    if not cid:
                        continue

                    xlogp = row.get("XLogP")

                    if xlogp is None:
                        continue

                    # PubChem may return an empty value
                    if xlogp == "":
                        results[cid] = None
                        continue

                    try:
                        results[cid] = float(xlogp)

                    except ValueError:
                        results[cid] = None

                return results

            # ------------------------------------------------
            # Rate limiting
            # ------------------------------------------------

            if response.status_code == 429:

                wait = 2 ** attempt

                print(
                    f"HTTP 429 - rate limited. "
                    f"Waiting {wait}s..."
                )

                time.sleep(wait)

                continue

            # ------------------------------------------------
            # Server errors
            # ------------------------------------------------

            if response.status_code >= 500:

                wait = 2 ** attempt

                print(
                    f"HTTP {response.status_code}. "
                    f"Retry {attempt}/{MAX_RETRIES} "
                    f"in {wait}s..."
                )

                time.sleep(wait)

                continue

            # ------------------------------------------------
            # Other HTTP error
            # ------------------------------------------------

            print(
                f"HTTP error {response.status_code}: "
                f"{response.text[:300]}"
            )

            return {}

        except requests.RequestException as e:

            wait = 2 ** attempt

            print(
                f"Network error: {e}\n"
                f"Retry {attempt}/{MAX_RETRIES} "
                f"in {wait}s..."
            )

            time.sleep(wait)

    print(
        f"FAILED after {MAX_RETRIES} attempts "
        f"for {len(cids)} CIDs"
    )

    return {}


# ============================================================
# STREAM CID FROM ZST
# ============================================================

def stream_cids(filename):
    """
    Stream CID values from the 2.1 GB ZST file.

    Does not decompress the whole file.
    """

    with open(filename, "rb") as compressed:

        dctx = zstd.ZstdDecompressor()

        with dctx.stream_reader(compressed) as reader:

            text_stream = io.TextIOWrapper(
                reader,
                encoding="utf-8",
                errors="replace",
                newline=""
            )

            reader_tsv = csv.DictReader(
                text_stream,
                delimiter="\t"
            )

            print("Input columns:")
            print(reader_tsv.fieldnames)
            print()

            if "cid" not in reader_tsv.fieldnames:

                raise ValueError(
                    "The input file does not contain a "
                    "'cid' column."
                )

            for row in reader_tsv:

                cid = row["cid"]

                if not cid:
                    continue

                # ------------------------------------------------
                # Some files may contain non-numeric values
                # ------------------------------------------------

                try:
                    int(cid)

                except ValueError:
                    continue

                yield cid


# ============================================================
# BATCH GENERATOR
# ============================================================

def batches(iterator, batch_size):

    batch = []

    for item in iterator:

        batch.append(item)

        if len(batch) >= batch_size:

            yield batch

            batch = []

    if batch:

        yield batch


# ============================================================
# MAIN PROCESSING
# ============================================================

def main():

    start_time = time.time()

    print("=" * 70)
    print("PubChem XLogP batch retrieval")
    print("=" * 70)

    print(f"Input : {INPUT_ZST}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Batch : {BATCH_SIZE}")
    print()

    # --------------------------------------------------------
    # Existing results
    # --------------------------------------------------------

    processed = load_existing_results(
        OUTPUT_FILE
    )

    # --------------------------------------------------------
    # Open output
    # --------------------------------------------------------

    output_exists = os.path.exists(OUTPUT_FILE)

    output = open(
        OUTPUT_FILE,
        "a",
        encoding="utf-8",
        newline=""
    )

    writer = csv.writer(
        output,
        delimiter="\t"
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    if not output_exists:

        writer.writerow([
            "cid",
            "xlogp",
            "status"
        ])

        output.flush()

    # --------------------------------------------------------
    # HTTP session
    # --------------------------------------------------------

    session = requests.Session()

    session.headers.update({
        "User-Agent":
            "PubChem-XLogP-Batch/1.0 "
            "(research; contact: your_email@example.com)"
    })

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total_unique = 0
    total_queries = 0
    total_found = 0
    total_missing = 0

    # --------------------------------------------------------
    # Stream CIDs
    # --------------------------------------------------------

    cid_stream = stream_cids(INPUT_ZST)

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We remove duplicates while streaming.
    #
    # The set can become large if there are tens of millions
    # of unique CIDs. If memory becomes an issue, we can
    # replace this with an SQLite disk-based cache.
    # --------------------------------------------------------

    seen = set()

    def unique_unprocessed_cids():

        for cid in cid_stream:

            if cid in seen:
                continue

            seen.add(cid)

            if cid in processed:
                continue

            yield cid

    # --------------------------------------------------------
    # Process batches
    # --------------------------------------------------------

    for batch in batches(
        unique_unprocessed_cids(),
        BATCH_SIZE
    ):

        total_unique += len(batch)

        total_queries += 1

        # ----------------------------------------------------
        # Query PubChem
        # ----------------------------------------------------

        results = query_pubchem_xlogp(
            batch,
            session
        )

        # ----------------------------------------------------
        # Write every CID in the batch
        #
        # Even if XLogP is missing.
        # This prevents repeatedly querying missing CIDs
        # when the program is resumed.
        # ----------------------------------------------------

        for cid in batch:

            if cid in results:

                xlogp = results[cid]

                if xlogp is None:

                    writer.writerow([
                        cid,
                        "",
                        "no_xlogp"
                    ])

                    total_missing += 1

                else:

                    writer.writerow([
                        cid,
                        xlogp,
                        "found"
                    ])

                    total_found += 1

            else:

                writer.writerow([
                    cid,
                    "",
                    "not_returned"
                ])

                total_missing += 1

        # ----------------------------------------------------
        # Flush immediately
        # ----------------------------------------------------

        output.flush()

        # ----------------------------------------------------
        # Rate limiting
        # ----------------------------------------------------

        time.sleep(REQUEST_DELAY)

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        processed_now = (
            total_found +
            total_missing
        )

        if processed_now % PROGRESS_EVERY < BATCH_SIZE:

            elapsed = time.time() - start_time

            rate = (
                processed_now / elapsed
                if elapsed > 0
                else 0
            )

            print(
                f"Processed: {processed_now:,} | "
                f"Found: {total_found:,} | "
                f"Missing: {total_missing:,} | "
                f"Rate: {rate:,.1f} CID/s"
            )

    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------

    output.close()
    session.close()

    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("FINISHED")
    print("=" * 70)

    print(
        f"New CIDs processed : "
        f"{total_unique:,}"
    )

    print(
        f"XLogP found        : "
        f"{total_found:,}"
    )

    print(
        f"XLogP unavailable   : "
        f"{total_missing:,}"
    )

    print(
        f"PubChem requests   : "
        f"{total_queries:,}"
    )

    print(
        f"Elapsed time       : "
        f"{elapsed / 3600:.2f} hours"
    )

    print()
    print(
        f"Results saved to: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
