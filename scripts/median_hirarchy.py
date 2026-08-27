#!/usr/bin/env python3

import csv
import io
import os
import sqlite3
import time
import zstandard as zstd


# ============================================================
# FILES
# ============================================================

CLASSYFIRE_NAMES = "classyfire_with_names.tsv"

CLASSYFIRE_ZST = (
    "classyfire_dedup_inchikey_smiles.enriched.tsv.zst"
)

PUBCHEM_XLOGP = "pubchem_xlogp.tsv"

DATABASE = "classyfire_xlogp.sqlite"

OUTPUT_FILE = "classyfire_xlogp_medians.tsv"


# ============================================================
# SETTINGS
# ============================================================

BATCH_SIZE = 10_000

LEVELS = [
    "kingdom",
    "superclass",
    "class",
    "subclass",
    "direct_parent",
]


# ============================================================
# SQLITE
# ============================================================

def connect_database():

    conn = sqlite3.connect(DATABASE)

    # Important for large datasets
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=FILE")
    conn.execute("PRAGMA cache_size=-200000")
    conn.execute("PRAGMA mmap_size=1073741824")

    return conn


# ============================================================
# STEP 1
# READ ONLY THE REQUIRED INCHIKEYS
# ============================================================

def get_required_inchikeys():

    print("=" * 70)
    print("STEP 1: Reading required InChIKeys")
    print("=" * 70)

    conn = connect_database()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS requested_inchikey (
            inchikey TEXT PRIMARY KEY
        )
    """)

    batch = []

    count = 0

    with open(
        CLASSYFIRE_NAMES,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter="\t"
        )

        if "inchikey" not in reader.fieldnames:
            raise RuntimeError(
                "classyfire_with_names.tsv does not contain "
                "'inchikey'"
            )

        for row in reader:

            key = row["inchikey"]

            if not key:
                continue

            batch.append((key,))

            count += 1

            if len(batch) >= BATCH_SIZE:

                conn.executemany(
                    """
                    INSERT OR IGNORE INTO requested_inchikey
                    VALUES (?)
                    """,
                    batch
                )

                conn.commit()

                batch.clear()

        if batch:

            conn.executemany(
                """
                INSERT OR IGNORE INTO requested_inchikey
                VALUES (?)
                """,
                batch
            )

            conn.commit()

    n = conn.execute(
        "SELECT COUNT(*) FROM requested_inchikey"
    ).fetchone()[0]

    print(
        f"Unique requested InChIKeys: {n:,}"
    )

    conn.close()


# ============================================================
# STEP 2
# STREAM THE 2.1 GB ZST
#
# Create only:
#
# inchikey -> CID
#
# for requested molecules.
# ============================================================

def build_inchikey_cid_mapping():

    print()
    print("=" * 70)
    print("STEP 2: Streaming ZST → InChIKey → CID")
    print("=" * 70)

    conn = connect_database()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inchikey_cid (
            inchikey TEXT PRIMARY KEY,
            cid TEXT
        )
    """)

    # --------------------------------------------------------
    # Number of keys we need
    # --------------------------------------------------------

    target = conn.execute(
        "SELECT COUNT(*) FROM requested_inchikey"
    ).fetchone()[0]

    print(
        f"Need to find {target:,} InChIKeys"
    )

    found = conn.execute(
        "SELECT COUNT(*) FROM inchikey_cid"
    ).fetchone()[0]

    print(
        f"Already mapped: {found:,}"
    )

    # --------------------------------------------------------
    # Load requested keys into a Python set.
    #
    # This is the ONLY potentially large in-memory object.
    # If this itself is too large, I give a SQLite-only
    # variant below.
    # --------------------------------------------------------

    requested = set()

    for row in conn.execute(
        "SELECT inchikey FROM requested_inchikey"
    ):

        requested.add(row[0])

    print(
        f"Loaded lookup keys: {len(requested):,}"
    )

    # Remove already mapped keys

    for row in conn.execute(
        "SELECT inchikey FROM inchikey_cid"
    ):

        requested.discard(row[0])

    print(
        f"Still need: {len(requested):,}"
    )

    if not requested:

        conn.close()
        return

    # --------------------------------------------------------
    # Stream ZST
    # --------------------------------------------------------

    start = time.time()

    matches = 0
    scanned = 0

    batch = []

    with open(
        CLASSYFIRE_ZST,
        "rb"
    ) as compressed:

        dctx = zstd.ZstdDecompressor()

        with dctx.stream_reader(
            compressed
        ) as reader:

            text = io.TextIOWrapper(
                reader,
                encoding="utf-8",
                errors="replace",
                newline=""
            )

            reader_tsv = csv.DictReader(
                text,
                delimiter="\t"
            )

            for row in reader_tsv:

                scanned += 1

                key = row["inchikey"]

                if key not in requested:
                    continue

                cid = row["cid"]

                if not cid:
                    continue

                batch.append(
                    (key, cid)
                )

                requested.remove(key)

                matches += 1

                if len(batch) >= BATCH_SIZE:

                    conn.executemany(
                        """
                        INSERT OR REPLACE
                        INTO inchikey_cid
                        VALUES (?, ?)
                        """,
                        batch
                    )

                    conn.commit()

                    batch.clear()

                if scanned % 5_000_000 == 0:

                    elapsed = time.time() - start

                    print(
                        f"Scanned {scanned:,} | "
                        f"found {matches:,} | "
                        f"remaining {len(requested):,} | "
                        f"{elapsed / 60:.1f} min"
                    )

                # ------------------------------------------------
                # If everything has been found, stop reading.
                # ------------------------------------------------

                if not requested:

                    print(
                        "All requested InChIKeys found."
                    )

                    break

    if batch:

        conn.executemany(
            """
            INSERT OR REPLACE
            INTO inchikey_cid
            VALUES (?, ?)
            """,
            batch
        )

        conn.commit()

    final_count = conn.execute(
        "SELECT COUNT(*) FROM inchikey_cid"
    ).fetchone()[0]

    print(
        f"Total InChIKey → CID mappings: "
        f"{final_count:,}"
    )

    conn.close()


# ============================================================
# STEP 3
# LOAD PUBCHEM XLOGP INTO SQLITE
# ============================================================

def load_xlogp():

    print()
    print("=" * 70)
    print("STEP 3: Loading PubChem XLogP")
    print("=" * 70)

    conn = connect_database()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS xlogp (
            cid TEXT PRIMARY KEY,
            xlogp REAL
        )
    """)

    existing = conn.execute(
        "SELECT COUNT(*) FROM xlogp"
    ).fetchone()[0]

    if existing:

        print(
            f"XLogP database already contains "
            f"{existing:,} records"
        )

        conn.close()
        return

    batch = []

    count = 0

    with open(
        PUBCHEM_XLOGP,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter="\t"
        )

        for row in reader:

            cid = row["cid"]
            value = row["xlogp"]

            if not cid or not value:
                continue

            try:
                value = float(value)

            except ValueError:
                continue

            batch.append(
                (cid, value)
            )

            count += 1

            if len(batch) >= BATCH_SIZE:

                conn.executemany(
                    """
                    INSERT OR REPLACE
                    INTO xlogp
                    VALUES (?, ?)
                    """,
                    batch
                )

                conn.commit()

                batch.clear()

                if count % 1_000_000 == 0:

                    print(
                        f"Loaded {count:,} XLogP records"
                    )

        if batch:

            conn.executemany(
                """
                INSERT OR REPLACE
                INTO xlogp
                VALUES (?, ?)
                """,
                batch
            )

            conn.commit()

    print(
        f"Total XLogP records: {count:,}"
    )

    # Index for CID join

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_xlogp_cid "
        "ON xlogp(cid)"
    )

    conn.commit()

    conn.close()


# ============================================================
# STEP 4
# STREAM CLASSYFIRE NAMES AND CREATE NODE VALUES
# ============================================================

def build_node_values():

    print()
    print("=" * 70)
    print("STEP 4: Building node → XLogP table")
    print("=" * 70)

    conn = connect_database()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS node_value (
            level TEXT NOT NULL,
            node_name TEXT NOT NULL,
            xlogp REAL NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Check whether this step was already completed
    # --------------------------------------------------------

    existing = conn.execute(
        "SELECT COUNT(*) FROM node_value"
    ).fetchone()[0]

    if existing:

        print(
            f"node_value already contains "
            f"{existing:,} records"
        )

        conn.close()
        return

    # --------------------------------------------------------
    # We create a temporary table containing only the
    # ClassyFire information needed for each CID.
    #
    # It is still disk-backed.
    # --------------------------------------------------------

    conn.execute("""
        CREATE TABLE compound_nodes (
            cid TEXT,
            kingdom TEXT,
            superclass TEXT,
            class TEXT,
            subclass TEXT,
            direct_parent TEXT
        )
    """)

    batch = []

    count = 0

    with open(
        CLASSYFIRE_NAMES,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter="\t"
        )

        for row in reader:

            key = row["inchikey"]

            # ------------------------------------------------
            # Get CID from SQLite
            # ------------------------------------------------

            result = conn.execute(
                """
                SELECT cid
                FROM inchikey_cid
                WHERE inchikey = ?
                """,
                (key,)
            ).fetchone()

            if result is None:
                continue

            cid = result[0]

            batch.append(
                (
                    cid,
                    row["kingdom"],
                    row["superclass"],
                    row["class"],
                    row["subclass"],
                    row["direct_parent"],
                )
            )

            count += 1

            if len(batch) >= BATCH_SIZE:

                conn.executemany(
                    """
                    INSERT INTO compound_nodes
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    batch
                )

                conn.commit()

                batch.clear()

                if count % 1_000_000 == 0:

                    print(
                        f"Mapped ClassyFire records: "
                        f"{count:,}"
                    )

        if batch:

            conn.executemany(
                """
                INSERT INTO compound_nodes
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                batch
            )

            conn.commit()

    print(
        f"ClassyFire records with CID: "
        f"{count:,}"
    )

    # --------------------------------------------------------
    # Index CID
    # --------------------------------------------------------

    print("Creating CID index...")

    conn.execute(
        """
        CREATE INDEX idx_compound_nodes_cid
        ON compound_nodes(cid)
        """
    )

    conn.commit()

    # --------------------------------------------------------
    # Convert the five hierarchy columns into a long table.
    #
    # This creates:
    #
    # level | node_name | xlogp
    #
    # --------------------------------------------------------

    print("Creating node-value table...")

    conn.execute("""
        INSERT INTO node_value
        SELECT
            'kingdom',
            kingdom,
            x.xlogp
        FROM compound_nodes c
        JOIN xlogp x
            ON c.cid = x.cid
        WHERE kingdom IS NOT NULL
          AND kingdom != ''

        UNION ALL

        SELECT
            'superclass',
            superclass,
            x.xlogp
        FROM compound_nodes c
        JOIN xlogp x
            ON c.cid = x.cid
        WHERE superclass IS NOT NULL
          AND superclass != ''

        UNION ALL

        SELECT
            'class',
            class,
            x.xlogp
        FROM compound_nodes c
        JOIN xlogp x
            ON c.cid = x.cid
        WHERE class IS NOT NULL
          AND class != ''

        UNION ALL

        SELECT
            'subclass',
            subclass,
            x.xlogp
        FROM compound_nodes c
        JOIN xlogp x
            ON c.cid = x.cid
        WHERE subclass IS NOT NULL
          AND subclass != ''

        UNION ALL

        SELECT
            'direct_parent',
            direct_parent,
            x.xlogp
        FROM compound_nodes c
        JOIN xlogp x
            ON c.cid = x.cid
        WHERE direct_parent IS NOT NULL
          AND direct_parent != ''
    """)

    conn.commit()

    n = conn.execute(
        "SELECT COUNT(*) FROM node_value"
    ).fetchone()[0]

    print(
        f"Node-value records: {n:,}"
    )

    conn.close()


# ============================================================
# STEP 5
# EXACT MEDIANS
# ============================================================

def calculate_medians():

    print()
    print("=" * 70)
    print("STEP 5: Calculating exact medians")
    print("=" * 70)

    conn = connect_database()

    # --------------------------------------------------------
    # Index to make node grouping/order efficient
    # --------------------------------------------------------

    print("Creating node index...")

    conn.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_node_value
        ON node_value(level, node_name, xlogp)
    """)

    conn.commit()

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # SQLite does not have MEDIAN() by default.
    #
    # We use ROW_NUMBER() + COUNT() to find the middle
    # value(s).
    #
    # SQLite may use temporary disk files rather than RAM
    # because temp_store=FILE.
    # --------------------------------------------------------

    query = """
    WITH ordered AS (

        SELECT
            level,
            node_name,
            xlogp,

            ROW_NUMBER() OVER (
                PARTITION BY level, node_name
                ORDER BY xlogp
            ) AS rn,

            COUNT(*) OVER (
                PARTITION BY level, node_name
            ) AS n

        FROM node_value
    )

    SELECT
        level,
        node_name,
        AVG(xlogp) AS median_xlogp,
        MAX(n) AS n_compounds

    FROM ordered

    WHERE
        rn = (n + 1) / 2
        OR
        rn = (n + 2) / 2

    GROUP BY
        level,
        node_name

    ORDER BY
        CASE level
            WHEN 'kingdom' THEN 1
            WHEN 'superclass' THEN 2
            WHEN 'class' THEN 3
            WHEN 'subclass' THEN 4
            WHEN 'direct_parent' THEN 5
        END,
        node_name
    """

    # --------------------------------------------------------
    # Write directly to TSV.
    #
    # We do NOT load the results into pandas.
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.writer(
            f,
            delimiter="\t"
        )

        writer.writerow([
            "level",
            "node_name",
            "median_xlogp",
            "n_compounds",
        ])

        count = 0

        for row in conn.execute(query):

            writer.writerow([
                row[0],
                row[1],
                f"{row[2]:.6g}",
                row[3],
            ])

            count += 1

            if count % 10_000 == 0:

                print(
                    f"Nodes written: "
                    f"{count:,}"
                )

    conn.close()

    print()
    print(
        f"Saved {count:,} hierarchy nodes"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    start = time.time()

    get_required_inchikeys()

    build_inchikey_cid_mapping()

    load_xlogp()

    build_node_values()

    calculate_medians()

    elapsed = time.time() - start

    print()
    print("=" * 70)
    print("FINISHED")
    print("=" * 70)

    print(
        f"Total time: {elapsed / 3600:.2f} hours"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )
