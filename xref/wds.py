"""Load and query the WDS catalog."""

from pathlib import Path
import re
import astropy.table
from wds_astropy_table import parse_wdsweb

WDS_DATA = Path(__file__).parent.parent / "data" / "wdsweb_summ2.txt"


def load_wds(path=WDS_DATA):
    """Load WDS data into an Astropy table using wds-astropy-table."""
    return parse_wdsweb(str(path))


def lookup_wds(table, identifier: str, components: str = "AB"):
    """Return the WDS row matching identifier and components, or None.

    identifier may be:
      - a 10-character WDS ID (e.g. '00057+4549')
      - an observer code + number string (e.g. 'STF 24')
    """
    
    identifier = identifier.strip().upper().replace(' ', '')
    components = components.upper()

    mask = None

    # identifier is a 10-character WDS ID
    if re.fullmatch(r'\d{5}[+-]\d{4}', identifier):
        mask = table['id'] == identifier

    # identifier is a discoverer code
    else:
        mask = table['discoverer_normalized'] == identifier
    
    # nothing found
    candidates = table[mask]
    if len(candidates) == 0 :
        return None

    # flag if these are the AB components
    comp_ab = False
    if (components == 'AB'):
        comp_ab = True

    comp_mask = ((candidates['components'] == components) | (comp_ab and (candidates['components']=="")))
    matched = candidates[comp_mask]
    
    if len(matched) == 0 :
        return None
    
    if len(matched) > 1 :
        print(f"Warning: more than one record found for {identifier} {components}")
    
    return matched[0]
