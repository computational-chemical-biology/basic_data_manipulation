#!/usr/bin/env python3

import csv
import json
import zstandard as zstd
from pathlib import Path
import time


# ============================================================
# CONFIGURATION
# ============================================================

CHEMONT_DICTIONARY = "chemont_dictionary.tsv"

INPUT_ZST = "classyfire_dedup_inchikey_smiles.enriched.tsv.zst"

OUTPUT_TSV = "classyfire_with_names.tsv"

# Set to True if you want progress information
SHOW_PROGRESS = True

# Print progress every N rows
PROGRESS_EVERY = 1_000_000


# ============================================================
# 1. LOAD CHEMONT DICTIONARY
# ============================================================

def load_chemont_dictionary(filename):
    """
    Load the ChemOnt dictionary into:

        numeric_id -> class name

    The dictionary is small enough to keep in memory.
    """

    print(f"Loading ChemOnt dictionary: {filename}")

    id_to_name = {}

    with open(filename, "r", encoding="utf-8-sig", newline="") as f:

        reader = csv.DictReader(f, delimiter="\t")

        print("Dictionary columns:")
        print(reader.fieldnames)

        # ----------------------------------------------------
        # Find the ID column
        # ----------------------------------------------------

        possible_id_columns = [
            "numeric_id",
            "id",
            "chemont_id",
            "ChemOnt ID",
            "chemontid",
        ]

        possible_name_columns = [
            "name",
            "Name",
            "label",
            "Label",
        ]

        id_column = next(
            (c for c in possible_id_columns if c in reader.fieldnames),
            None
        )

        name_column = next(
            (c for c in possible_name_columns if c in reader.fieldnames),
            None
        )

        if id_column is None:
            raise ValueError(
                f"Could not identify the ChemOnt ID column.\n"
                f"Available columns: {reader.fieldnames}"
            )

        if name_column is None:
            raise ValueError(
                f"Could not identify the ChemOnt name column.\n"
                f"Available columns: {reader.fieldnames}"
            )

        print(f"Using ID column:   {id_column}")
        print(f"Using name column: {name_column}")

        # ----------------------------------------------------
        # Read dictionary
        # ----------------------------------------------------

        for row in reader:

            raw_id = row[id_column]
            name = row[name_column]

            if not raw_id:
                continue

            try:
                numeric_id = int(raw_id)
            except ValueError:
                continue

            id_to_name[numeric_id] = name

    print(f"Loaded {len(id_to_name):,} ChemOnt terms")

    return id_to_name


# ============================================================
# 2. CONVERT TREE IDS TO NAMES
# ============================================================

def decode_tree(tree_json, id_to_name):
    """
    Convert:

        [kingdom, superclass, class, subclass, direct_parent]

    into five names.
    """

    try:
        tree = json.loads(tree_json)

    except (json.JSONDecodeError, TypeError):
        return "", "", "", "", ""

    # --------------------------------------------------------
    # The Zenodo v2 format is:
    #
    # [kingdom, superclass, class, subclass, direct_parent]
    # --------------------------------------------------------

    if not isinstance(tree, list) or len(tree) != 5:
        return "", "", "", "", ""

    kingdom_id = tree[0]
    superclass_id = tree[1]
    class_id = tree[2]
    subclass_id = tree[3]
    direct_parent_id = tree[4]

    return (
        id_to_name.get(kingdom_id, ""),
        id_to_name.get(superclass_id, ""),
        id_to_name.get(class_id, ""),
        id_to_name.get(subclass_id, ""),
        id_to_name.get(direct_parent_id, ""),
    )


# ============================================================
# 3. STREAM THE 2.1 GB ZST FILE
# ============================================================

def process_file(input_zst, output_tsv, id_to_name):

    print()
    print("Processing:")
    print(f"  Input : {input_zst}")
    print(f"  Output: {output_tsv}")
    print()

    start_time = time.time()

    rows = 0
    errors = 0

    # --------------------------------------------------------
    # Open compressed Zstandard file
    # --------------------------------------------------------

    with open(input_zst, "rb") as compressed:

        dctx = zstd.ZstdDecompressor()

        # stream_reader does NOT decompress the entire file
        # into RAM.
        with dctx.stream_reader(compressed) as reader:

            # Text wrapper converts bytes -> text
            import io

            text_stream = io.TextIOWrapper(
                reader,
                encoding="utf-8",
                errors="replace",
                newline=""
            )

            # ------------------------------------------------
            # Read TSV
            # ------------------------------------------------

            csv_reader = csv.DictReader(
                text_stream,
                delimiter="\t"
            )

            print("Input columns:")
            print(csv_reader.fieldnames)
            print()

            # ------------------------------------------------
            # Check required columns
            # ------------------------------------------------

            required = {
                "inchikey",
                "smiles",
                "chemont_tree_json",
            }

            missing = required - set(csv_reader.fieldnames)

            if missing:
                raise ValueError(
                    f"Missing required columns: {missing}"
                )

            # ------------------------------------------------
            # Output
            # ------------------------------------------------

            with open(
                output_tsv,
                "w",
                encoding="utf-8",
                newline=""
            ) as out:

                writer = csv.writer(
                    out,
                    delimiter="\t",
                    quoting=csv.QUOTE_MINIMAL
                )

                # Header
                writer.writerow([
                    "inchikey",
                    "smiles",
                    "kingdom",
                    "superclass",
                    "class",
                    "subclass",
                    "direct_parent",
                ])

                # ------------------------------------------------
                # Process rows
                # ------------------------------------------------

                for row in csv_reader:

                    rows += 1

                    inchikey = row["inchikey"]
                    smiles = row["smiles"]
                    tree_json = row["chemont_tree_json"]

                    try:

                        (
                            kingdom,
                            superclass,
                            chem_class,
                            subclass,
                            direct_parent,
                        ) = decode_tree(
                            tree_json,
                            id_to_name
                        )

                        writer.writerow([
                            inchikey,
                            smiles,
                            kingdom,
                            superclass,
                            chem_class,
                            subclass,
                            direct_parent,
                        ])

                    except Exception:
                        errors += 1

                        writer.writerow([
                            inchikey,
                            smiles,
                            "",
                            "",
                            "",
                            "",
                            "",
                        ])

                    # ------------------------------------------------
                    # Progress
                    # ------------------------------------------------

                    if SHOW_PROGRESS and rows % PROGRESS_EVERY == 0:

                        elapsed = time.time() - start_time

                        rate = rows / elapsed if elapsed else 0

                        print(
                            f"{rows:,} rows | "
                            f"{rate:,.0f} rows/s | "
                            f"errors={errors:,}"
                        )

    elapsed = time.time() - start_time

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"Rows processed : {rows:,}")
    print(f"Errors         : {errors:,}")
    print(f"Time           : {elapsed / 3600:.2f} hours")
    print(f"Output         : {output_tsv}")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    id_to_name = load_chemont_dictionary(
        CHEMONT_DICTIONARY
    )

    process_file(
        INPUT_ZST,
        OUTPUT_TSV,
        id_to_name
    )
