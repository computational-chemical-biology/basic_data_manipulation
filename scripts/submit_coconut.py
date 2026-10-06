#!/usr/bin/env python3

"""
Test submission of caramboxin to COCONUT.

COCONUT entry:
    CNP0146602.1

Reference:
    Garcia-Cairasco et al. (2013)
    "Elucidating the Neurotoxicity of the Star Fruit"
    DOI: 10.1002/anie.201305382

The script:
1. Logs into COCONUT
2. Obtains a Bearer token
3. Constructs the report submission
4. By default, only prints the payload
5. Use --submit to actually submit it

Environment variables:
    COCONUT_EMAIL
    COCONUT_PASSWORD

Example:

    export COCONUT_EMAIL="your@email.com"
    export COCONUT_PASSWORD="your-password"

    python submit_coconut.py

To actually submit:

    python submit_coconut.py --submit
"""

import argparse
import json
import os
import sys

import requests


BASE_URL = "https://coconut.naturalproducts.net"

LOGIN_URL = f"{BASE_URL}/api/auth/login"

# The endpoint reported to accept submissions
SUBMIT_URL = f"{BASE_URL}/api/reports/mutate"


# ---------------------------------------------------------------------
# Compound information
# ---------------------------------------------------------------------

COCONUT_ID = "CNP0146602.1"

NAME = "Caramboxin"

CANONICAL_SMILES = (
    "COC1=CC(=C(C(=C1)O)C(=O)O)"
    "C[C@@H](C(=O)O)N"
)

DOI = "10.1002/anie.201305382"

ARTICLE_TITLE = "Elucidating the Neurotoxicity of the Star Fruit"

ARTICLE_URL = (
    "https://doi.org/10.1002/anie.201305382"
)

PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/compound/134728497"
)

ORGANISM = "Averrhoa carambola"


# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------

def login(email, password):
    """Authenticate against COCONUT and return the access token."""

    payload = {
        "email": email,
        "password": password,
    }

    response = requests.post(
        LOGIN_URL,
        json=payload,
        timeout=30,
    )

    print(f"Login HTTP status: {response.status_code}")

    if not response.ok:
        print("Login failed:")
        print(response.text)
        response.raise_for_status()

    data = response.json()

    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            "Login succeeded but no access_token was returned:\n"
            + json.dumps(data, indent=2)
        )

    return token


# ---------------------------------------------------------------------
# Submission payload
# ---------------------------------------------------------------------

def build_payload():
    """
    Build the COCONUT report submission.

    Only the fields required for a minimal submission are necessary:
        title
        canonical_smiles
        DOI
    """

    payload = {
        "mutate": [
            {
                "operation": "create",

                "attributes": {

                    "title": ARTICLE_TITLE,

                    "evidence": (
                        "Caramboxin was reported as the neurotoxic "
                        "compound responsible for the neurotoxicity "
                        "associated with ingestion of star fruit "
                        "(Averrhoa carambola)."
                    ),

                    "comment": (
                        "Test submission corresponding to the existing "
                        f"COCONUT compound {COCONUT_ID}."
                    ),

                    "suggested_changes": {

                        "new_molecule_data": {

                            "canonical_smiles": CANONICAL_SMILES,

                            "name": NAME,

                            "link": PUBCHEM_URL,

                            "structural_comments": (
                                "Caramboxin is a phenylalanine-like "
                                "natural product reported from "
                                "Averrhoa carambola and associated "
                                "with star-fruit neurotoxicity."
                            ),

                            "references": [
                                {
                                    "doi": DOI,

                                    "organisms": [
                                        {
                                            "name": ORGANISM
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                },

                "relations": []
            }
        ]
    }

    return payload


# ---------------------------------------------------------------------
# Submit
# ---------------------------------------------------------------------

def submit_report(token, payload):
    """Submit the report to COCONUT."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(
        SUBMIT_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    print()
    print("=" * 70)
    print("SUBMISSION RESPONSE")
    print("=" * 70)

    print(f"HTTP status: {response.status_code}")

    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except ValueError:
        print(response.text)

    response.raise_for_status()

    return response


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Submit a natural-product report to COCONUT."
    )

    parser.add_argument(
        "--submit",
        action="store_true",
        help="Actually submit the report. Without this flag, "
             "the script performs a dry run."
    )

    args = parser.parse_args()

    payload = build_payload()

    # ---------------------------------------------------------------
    # Always show what is going to be submitted
    # ---------------------------------------------------------------

    print("=" * 70)
    print("COCONUT SUBMISSION")
    print("=" * 70)

    print(f"Existing COCONUT ID : {COCONUT_ID}")
    print(f"Compound            : {NAME}")
    print(f"DOI                 : {DOI}")
    print(f"SMILES              : {CANONICAL_SMILES}")
    print()

    print("Payload:")
    print(json.dumps(payload, indent=2))

    # ---------------------------------------------------------------
    # Dry run
    # ---------------------------------------------------------------

    if not args.submit:
        print()
        print("=" * 70)
        print("DRY RUN")
        print("=" * 70)
        print()
        print("Nothing was submitted.")
        print()
        print("To actually submit:")
        print()
        print("    python submit_coconut.py --submit")
        print()

        return

    # ---------------------------------------------------------------
    # Credentials
    # ---------------------------------------------------------------

    email = os.environ.get("COCONUT_EMAIL")
    password = os.environ.get("COCONUT_PASSWORD")

    if not email or not password:
        print()
        print("ERROR: COCONUT_EMAIL and COCONUT_PASSWORD must be set.")
        print()
        print("Example:")
        print()
        print('    export COCONUT_EMAIL="your@email.com"')
        print('    export COCONUT_PASSWORD="your-password"')
        print()
        sys.exit(1)

    # ---------------------------------------------------------------
    # Login
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("AUTHENTICATION")
    print("=" * 70)

    token = login(email, password)

    print("Authentication successful.")
    print("Bearer token obtained.")

    # ---------------------------------------------------------------
    # Submit
    # ---------------------------------------------------------------

    print()
    print("=" * 70)
    print("SUBMITTING TO COCONUT")
    print("=" * 70)

    submit_report(token, payload)


if __name__ == "__main__":
    main()
