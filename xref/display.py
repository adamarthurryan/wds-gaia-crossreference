"""Output formatting for WDS/Gaia cross-reference results."""

import math
import astropy.units as u
from xref.coordinates import gaia_coords_j2000

SOLUTION_THRESHOLD = 1.5  # arcseconds


def _get_col(row, *names, default=float("nan")):
    """Return the first matching column value from a table row."""
    colnames = row.colnames if hasattr(row, "colnames") else []
    for name in names:
        if name in colnames:
            return row[name]
    return default


def _find_best_match(sources, coord):
    """Return (best_source, separation_arcsec) sorted by separation, or (None, None)."""
    if sources is None or len(sources) == 0:
        return None, None
    gaia_c = gaia_coords_j2000(sources)
    seps = coord.separation(gaia_c).to(u.arcsec)
    pairs = sorted(zip(sources, seps), key=lambda x: x[1])
    best_src, best_sep = pairs[0]
    return best_src, best_sep


def print_results(record, coords, gaia_results: dict):
    """Print a summary of Gaia sources found for each WDS component."""
    wds_id = str(record[0]).strip()
    disc = str(record[1]).strip()
    comp = str(record[2]).strip()
    mag_a = _get_col(record, "pri_mag", "mag1")
    mag_b = _get_col(record, "sec_mag", "mag2")
    sptype = str(_get_col(record, "spectral", "sp_type", default="")).strip()

    print(f"\nWDS {wds_id}  {disc}  comp={comp}")
    print(f"  Mag A={mag_a}  Mag B={mag_b}  SpType={sptype}\n")

    wds_mags = {}
    for label in ("A", "B"):
        val = mag_a if label == "A" else mag_b
        try:
            wds_mags[label] = float(val)
        except (TypeError, ValueError):
            wds_mags[label] = None

    solutions = {}  # label -> (source, sep)

    for label, sources in gaia_results.items():
        coord = coords[label]
        wds_mag = wds_mags.get(label)
        print(f"--- Component {label}  ({coord.ra.deg:.5f}, {coord.dec.deg:.5f}) ---")

        if sources is None or len(sources) == 0:
            print("  No Gaia sources found.\n")
            continue

        # Compute angular separations — propagate Gaia J2016 → J2000 to match WDS epoch
        gaia_c = gaia_coords_j2000(sources)
        seps = coord.separation(gaia_c).to(u.arcsec)
        pairs = sorted(zip(sources, seps), key=lambda x: x[1])

        print(f"  {'#':>3}  {'source_id':>20}  {'sep(arcsec)':>12}  {'g_mag':>6}  {'delta_mag':>9}  {'teff_gspphot':>12}")
        for i, (src, sep) in enumerate(pairs, 1):
            g_mag = _get_col(src, "phot_g_mean_mag")
            try:
                delta_mag = float(g_mag) - wds_mag if wds_mag is not None else float("nan")
            except (TypeError, ValueError):
                delta_mag = float("nan")
            teff = _get_col(src, "teff_gspphot")
            marker = " *" if sep.value < SOLUTION_THRESHOLD and i == 1 else ""
            print(f"  {i:>3}  {src['source_id']:>20}  {sep.value:>12.3f}  {float(g_mag):>6.2f}  {delta_mag:>9.2f}  {float(teff):>12.0f}{marker}")

        best_src, best_sep = pairs[0]
        if best_sep.value < SOLUTION_THRESHOLD:
            solutions[label] = (best_src, best_sep)
        print()

    # If all components have a solution, print summary table
    if solutions and all(label in solutions for label in gaia_results):
        _print_solution_table(solutions, wds_mags)


def _fmt(val, fmt=".3f"):
    """Format a value, returning '---' if masked/nan."""
    try:
        f = float(val)
        if math.isnan(f):
            return "---"
        return format(f, fmt)
    except (TypeError, ValueError):
        return "---"


def _print_solution_table(solutions, wds_mags):
    """Print a compact summary table for the matched Gaia sources."""
    # (gaia_key or special, header, width, fmt_spec)
    cols = [
        ("source_id",       "source_id",   19, "s"),
        ("sep",             'sep(")',        7, ".3f"),
        ("phot_g_mean_mag", "G",             6, ".2f"),
        ("bp_rp",           "BP-RP",         6, ".2f"),
        ("parallax",        "plx(mas)",      9, ".3f"),
        ("parallax_error",  "plx_err",       7, ".3f"),
        ("pmra",            "pmRA",          8, ".2f"),
        ("pmdec",           "pmDec",         8, ".2f"),
        ("radial_velocity", "RV(km/s)",      9, ".2f"),
        ("teff_gspphot",    "Teff",          6, ".0f"),
    ]

    sep_str = "  "
    header_parts = ["comp"]
    for _, title, width, _ in cols:
        header_parts.append(f"{title:>{width}}")
    header = sep_str + sep_str.join(header_parts)

    print("\n=== Gaia Solutions ===")
    print(header)
    print(sep_str + "-" * (len(header) - len(sep_str)))

    for label, (src, sep) in sorted(solutions.items()):
        row_parts = [f"{label:>4}"]
        for key, _, width, fmt in cols:
            if key == "source_id":
                val = f"{str(src['source_id']):>{width}}"
            elif key == "sep":
                val = f"{sep.value:>{width}.3f}"
            else:
                val = f"{_fmt(_get_col(src, key), fmt):>{width}}"
            row_parts.append(val)
        print(sep_str + sep_str.join(row_parts))
    print()
