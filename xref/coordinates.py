"""Coordinate utilities for WDS/Gaia cross-reference."""

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

_GAIA_EPOCH = Time('J2016.0')
_WDS_EPOCH  = Time('J2000.0')


def gaia_coords_j2000(sources) -> SkyCoord:
    """Return a SkyCoord array for Gaia sources propagated back to J2000.

    Gaia DR3 positions are at J2016.0.  This applies the catalogued proper
    motions to bring them to J2000.0 for comparison with WDS coordinates.
    Sources with missing proper motions are treated as having zero proper motion.
    """
    pmra  = np.where(np.isfinite(sources["pmra"]),  sources["pmra"],  0.0)
    pmdec = np.where(np.isfinite(sources["pmdec"]), sources["pmdec"], 0.0)

    coords_j2016 = SkyCoord(
        ra=sources["ra"] ,
        dec=sources["dec"],
        pm_ra_cosdec=pmra  * u.mas / u.yr,
        pm_dec=pmdec * u.mas / u.yr,
        obstime=_GAIA_EPOCH,
        frame="icrs",
    )
    return coords_j2016.apply_space_motion(new_obstime=_WDS_EPOCH)

def parse_coord_j2000_string(s) -> SkyCoord:
    """Parse the arcsecond-precision 2000 coordinate from a WDS record.
    Format HHMMSSs.s+DDMMSS
    """

    rs = s[:9]
    ds = s[9:]

    formatted_coord_string = rs[0:2]+'h'+rs[2:4]+'m'+rs[4:]+'s' + ' ' + ds[0:3]+'d'+ds[3:5]+'m'+ds[5:]+'s'
    return SkyCoord(formatted_coord_string, unit=(u.hourangle, u.deg), obstime=Time('J2000.0'))

def parse_coord_id_string(s) -> SkyCoord:
    """Parse the arcminute-precision coordinate from a WDS identifier string.
    Format HHMMm+/-DDmm where the trailing digit is tenths of arcminutes.
    """

    rs = s[:5]   # HHMMm
    ds = s[5:]   # +/-DDmm

    formatted_coord_string = rs[0:2]+'h'+rs[2:]+'m ' + ds[0:3]+'d'+ds[3:]+'m'
    return SkyCoord(formatted_coord_string, unit=(u.hourangle, u.deg))


def primary_coord(record) -> SkyCoord:
    """Parse the arcsecond-precision 2000 coordinate from a WDS record."""
    
    coord_str = str(record["j2000"]) if "j2000" in record.colnames else None
 
    if coord_str and len(coord_str) >= 15:
        return parse_coord_j2000_string(coord_str)

    else:
        return parse_coord_id_string(record['id'])


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
