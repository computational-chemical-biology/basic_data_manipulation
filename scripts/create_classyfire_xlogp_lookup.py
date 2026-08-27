#!/usr/bin/env python3

import csv
from pprint import pformat


INPUT_FILE = "classyfire_xlogp_medians.tsv"
OUTPUT_FILE = "classyfire_xlogp_lookup.py"


def main():

    # --------------------------------------------------------
    # Nested lookup dictionary
    # --------------------------------------------------------

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

        if not required_columns.issubset(
            reader.fieldnames
        ):

            raise ValueError(
                "Input file must contain columns:\n"
                + "\n".join(
                    sorted(required_columns)
                )
            )

        n_rows = 0

        for row in reader:

            level = row["level"].strip()
            node_name = row["node_name"].strip()

            if not level or not node_name:
                continue

            try:
                median_xlogp = float(
                    row["median_xlogp"]
                )

                n_compounds = int(
                    row["n_compounds"]
                )

            except (
                ValueError,
                TypeError,
            ):

                print(
                    f"Skipping invalid row: "
                    f"{row}"
                )

                continue

            if level not in lookup:

                lookup[level] = {}

            lookup[level][node_name] = {
                "median_xlogp": median_xlogp,
                "n_compounds": n_compounds,
            }

            n_rows += 1

    print(
        f"Loaded {n_rows:,} hierarchy nodes"
    )

    # --------------------------------------------------------
    # Generate Python module
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            '"""\\n'
            'Precomputed ClassyFire/ChemOnt '
            'median XLogP lookup.\\n'
            '\\n'
            f'Generated from: {INPUT_FILE}\\n'
            '"""\\n\\n'
        )

        f.write(
            "# Structure:\\n"
            "# XLOGP[level][node_name] = {\\n"
            "#     'median_xlogp': float,\\n"
            "#     'n_compounds': int\\n"
            "# }\\n\\n"
        )

        f.write(
            "XLOGP = "
        )

        f.write(
            pformat(
                lookup,
                width=120,
                sort_dicts=False,
            )
        )

        f.write("\n\n")

        # ----------------------------------------------------
        # Add a convenient lookup function
        # ----------------------------------------------------

        f.write(
            '''
def get_xlogp(
    kingdom=None,
    superclass=None,
    chem_class=None,
    subclass=None,
    direct_parent=None,
):
    """
    Return the median XLogP for the most specific
    supplied ClassyFire/ChemOnt node.

    Priority:
        direct_parent
        subclass
        class
        superclass
        kingdom

    Returns:
        dict with:
            median_xlogp
            n_compounds

        or None if no match is found.
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
    Return only the median XLogP value.

    Returns None if no node is found.
    """

    result = get_xlogp(**kwargs)

    if result is None:
        return None

    return result["median_xlogp"]
'''
        )

    print(
        f"Created: {OUTPUT_FILE}"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()

    for level, nodes in lookup.items():

        print(
            f"{level:15s}: "
            f"{len(nodes):,} nodes"
        )


if __name__ == "__main__":
    main()
