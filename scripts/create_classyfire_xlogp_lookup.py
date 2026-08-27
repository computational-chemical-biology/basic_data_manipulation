#!/usr/bin/env python3

import csv
from pprint import pformat


INPUT_FILE = "classyfire_xlogp_medians.tsv"
OUTPUT_FILE = "classyfire_xlogp_lookup.py"


def main():

    lookup = {}

    print(f"Reading: {INPUT_FILE}")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(
            f,
            delimiter="\t"
        )

        required_columns = {
            "level",
            "node_name",
            "median_xlogp",
            "n_compounds",
        }

        if not required_columns.issubset(reader.fieldnames):

            raise ValueError(
                "Input file must contain columns: "
                "level, node_name, median_xlogp, n_compounds"
            )

        n_rows = 0

        for row in reader:

            level = row["level"].strip()
            node_name = row["node_name"].strip()

            if not level or not node_name:
                continue

            try:
                median_xlogp = float(row["median_xlogp"])
                n_compounds = int(row["n_compounds"])

            except (ValueError, TypeError):

                print(f"Skipping invalid row: {row}")
                continue

            if level not in lookup:
                lookup[level] = {}

            lookup[level][node_name] = {
                "median_xlogp": median_xlogp,
                "n_compounds": n_compounds,
            }

            n_rows += 1

    print(f"Loaded {n_rows:,} hierarchy nodes")

    # --------------------------------------------------------
    # Generate valid Python module
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as f:

        # IMPORTANT:
        # Use actual newline characters here.
        f.write('''"""
Precomputed ClassyFire/ChemOnt median XLogP lookup.

Generated from: classyfire_xlogp_medians.tsv
"""

# Structure:
# XLOGP[level][node_name] = {
#     "median_xlogp": float,
#     "n_compounds": int
# }

''')

        f.write("XLOGP = ")

        f.write(
            pformat(
                lookup,
                width=120,
                sort_dicts=False,
            )
        )

        f.write("\n\n")

        f.write('''
def get_xlogp(
    kingdom=None,
    superclass=None,
    chem_class=None,
    subclass=None,
    direct_parent=None,
):
    """
    Return information for the most specific supplied
    ClassyFire/ChemOnt node.

    Priority:
        direct_parent
        subclass
        class
        superclass
        kingdom
    """

    candidates = [
        ("direct_parent", direct_parent),
        ("subclass", subclass),
        ("class", chem_class),
        ("superclass", superclass),
        ("kingdom", kingdom),
    ]

    for level, node_name in candidates:

        if node_name:

            result = XLOGP.get(
                level,
                {}
            ).get(node_name)

            if result is not None:
                return result

    return None


def get_median_xlogp(**kwargs):
    """
    Return only the median XLogP.

    Returns None if no matching ClassyFire node is found.
    """

    result = get_xlogp(**kwargs)

    if result is None:
        return None

    return result["median_xlogp"]
''')

    print(f"Created valid Python module: {OUTPUT_FILE}")

    print("\nNodes by level:")

    for level, nodes in lookup.items():
        print(f"  {level}: {len(nodes):,}")


if __name__ == "__main__":
    main()
