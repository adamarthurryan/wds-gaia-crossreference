"""Gaia DR3 cone search utilities."""

import astropy.units as u
from astroquery.gaia import Gaia

SEARCH_RADIUS = 30 * u.arcsec

Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
Gaia.ROW_LIMIT = 20


def cone_search(coord, radius=SEARCH_RADIUS):
    """Return an Astropy table of Gaia DR3 sources within radius of coord."""
    job = Gaia.cone_search_async(coord, radius=radius)
    return job.get_results()
