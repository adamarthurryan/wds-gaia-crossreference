"""Coordinate utilities for WDS/Gaia cross-reference."""

import astropy.units as u
from astropy.coordinates import SkyCoord


def primary_coord(record) -> SkyCoord:
    """Parse the arcsecond-precision 2000 coordinate from a WDS record."""
    # Column 113-130: 'RA Hdec' format, e.g. '001347.8+454933'
    coord_str = str(record["j2000"]).strip() if "j2000" in record.colnames else None

    if coord_str and len(coord_str) >= 15:
        ra_str = coord_str[:9]   # HHMMSSs.s
        dec_str = coord_str[9:]  # +DDMMSS
        ra_h = int(ra_str[0:2])
        ra_m = int(ra_str[2:4])
        ra_s = float(ra_str[4:])
        sign = -1 if dec_str[0] == "-" else 1
        dec_d = int(dec_str[1:3])
        dec_m = int(dec_str[3:5])
        dec_s = int(dec_str[5:7])
        ra_deg = 15 * (ra_h + ra_m / 60 + ra_s / 3600)
        dec_deg = sign * (dec_d + dec_m / 60 + dec_s / 3600)
        return SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame="icrs")

    # Fall back to arcminute coordinate (WDS id)
    wds_id = str(record["id"]).strip()
    ra_hm = wds_id[:5]   # HHMMm
    dec_dm = wds_id[5:]  # +/-DDmm
    ra_h = int(ra_hm[0:2])
    ra_m = float(ra_hm[2:]) / 10
    sign = -1 if dec_dm[0] == "-" else 1
    dec_d = int(dec_dm[1:3])
    dec_m = float(dec_dm[3:]) / 10
    ra_deg = 15 * (ra_h + ra_m / 60)
    dec_deg = sign * (dec_d + dec_m / 60)
    return SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame="icrs")


def component_coords(record) -> dict:
    """Return {component_label: SkyCoord} for primary (A) and secondary (B).

    Uses last position angle and separation from the WDS record.
    """
    primary = primary_coord(record)

    pa_deg = float(record["last_pa"])
    sep_arcsec = float(record["last_sep"])

    # Derive secondary position: offset from primary along PA
    # PA is measured east of north; directional_offset_by handles spherical geometry
    secondary = primary.directional_offset_by(pa_deg * u.deg, sep_arcsec * u.arcsec)

    return {"A": primary, "B": secondary}
