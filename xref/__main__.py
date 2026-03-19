"""Interactive WDS/Gaia cross-reference tool."""

import argparse
import sys

from xref.wds import load_wds, lookup_wds
from xref.coordinates import component_coords
from xref.gaia import cone_search
from xref.display import print_results


def main():
    parser = argparse.ArgumentParser(
        description="Cross-reference WDS double star system with Gaia DR3"
    )
    parser.add_argument(
        "identifier",
        help='WDS identifier (10-char WDS ID or "discoverer number")',
    )
    parser.add_argument(
        "--components",
        default="AB",
        help="Two-character components code (default: AB)",
    )
    args = parser.parse_args()

    wds_table = load_wds()
    record = lookup_wds(wds_table, args.identifier, args.components)
    if record is None:
        print(f"No WDS record found for {args.identifier!r} {args.components}")
        sys.exit(1)

    print(f"WDS record found: {record}")

    coords = component_coords(record)
    
    print(f"Calculated coordinates: {coords}")

    results = {}
    for label, coord in coords.items():
        results[label] = cone_search(coord)

    print(f"Results: {results}")
    
    print_results(record, coords, results)


if __name__ == "__main__":
    main()
