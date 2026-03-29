"""Interactive WDS/Gaia cross-reference tool."""

import argparse
import sys

from xref.wds import load_wds, lookup_wds
from xref.coordinates import component_coords
from xref.gaia import cone_search
from xref.display import print_results
from xref.image import plot_field
from xref import cache


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
    parser.add_argument(
        "--image",
        metavar="FILE",
        nargs="?",
        const="",
        default=None,
        help="Download and display a DSS field image with overlays. "
             "Optionally provide a file path to save instead of displaying.",
    )
    args = parser.parse_args()

    identifier = args.identifier.strip().upper().replace(' ', '')
    components = args.components.upper()

    cached = cache.load(identifier, components)
    if cached is not None:
        print("(loaded from cache)")
        record, coords, results = cached
    else:
        wds_table = load_wds()
        record = lookup_wds(wds_table, args.identifier, args.components)
        if record is None:
            print(f"No WDS record found for {args.identifier!r} {args.components}")
            sys.exit(1)

        coords = component_coords(record)

        results = {}
        for label, coord in coords.items():
            results[label] = cone_search(coord)

        cache.save(args.identifier, args.components, record, coords, results)

    print_results(record, coords, results)

    if args.image is not None:
        output = args.image if args.image else None
        plot_field(record, coords, results, output=output)


if __name__ == "__main__":
    main()
