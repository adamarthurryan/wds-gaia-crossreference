"""Output formatting for WDS/Gaia cross-reference results."""

import astropy.units as u
from xref.coordinates import gaia_coords_j2000


def print_results(record, coords, gaia_results: dict):
    """Print a summary of Gaia sources found for each WDS component."""
    wds_id = str(record[0]).strip()
    disc = str(record[1]).strip()
    comp = str(record[2]).strip()
    mag_a = record["pri_mag"] if "pri_mag" in record.colnames else record["mag1"] if "mag1" in record.colnames else record[10]
    mag_b = record["sec_mag"] if "sec_mag" in record.colnames else record["mag2"] if "mag2" in record.colnames else record[11]
    sptype = str(record["spectral"]).strip() if "spectral" in record.colnames else str(record["sp_type"]).strip() if "sp_type" in record.colnames else str(record[12]).strip()

    print(f"\nWDS {wds_id}  {disc}  comp={comp}")
    print(f"  Mag A={mag_a}  Mag B={mag_b}  SpType={sptype}\n")

    wds_mags = {"A": float(mag_a) if mag_a else None, "B": float(mag_b) if mag_b else None}

    for label, sources in gaia_results.items():
        coord = coords[label]
        wds_mag = wds_mags.get(label)
        print(f"--- Component {label}  ({coord.ra.deg:.5f}, {coord.dec.deg:.5f}) ---")

        if sources is None or len(sources) == 0:
            print("  No Gaia sources found.\n")
            continue

        # Compute angular separations — propagate Gaia J2016 → J2000 to match WDS epoch
        gaia_coords = gaia_coords_j2000(sources)
        seps = coord.separation(gaia_coords).to(u.arcsec)

        print(f"  {'#':>3}  {'source_id':>20}  {'sep(arcsec)':>12}  {'g_mag':>6}  {'delta_mag':>9}  {'teff_gspphot':>12}")
        for i, (src, sep) in enumerate(sorted(zip(sources, seps), key=lambda x: x[1]), 1):
            g_mag = src["phot_g_mean_mag"] if "phot_g_mean_mag" in sources.colnames else float("nan")
            delta_mag = (float(g_mag) - wds_mag) if (wds_mag and g_mag) else float("nan")
            teff = src["teff_gspphot"] if "teff_gspphot" in sources.colnames else float("nan")
            print(f"  {i:>3}  {src['source_id']:>20}  {sep.value:>12.3f}  {float(g_mag):>6.2f}  {delta_mag:>9.2f}  {float(teff):>12.0f}")
        print()
