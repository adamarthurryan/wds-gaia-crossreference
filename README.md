# WDS/Gaia Cross-Reference

Cross-reference double star systems from the [Washington Double Star Catalog (WDS)](https://www.usno.navy.mil/USNO/astrometry/optical-IR-prod/wds/WDS) against [Gaia DR3](https://www.cosmos.esa.int/web/gaia/dr3) sources.

Given a WDS system identifier, `xref` looks up the system, computes expected coordinates for each component, queries Gaia DR3 via cone search, and prints a table of nearby Gaia sources with separation, magnitude, and temperature.

## Install

Requires Python 3.10+.

```bash
pip install -e .
```

This installs the `xref` command along with dependencies: `astropy`, `astroquery`, and `wds-astropy-table`.

The WDS data file (`data/wdsweb_summ2.txt`) must be downloaded manually and added to the folder.

## Usage

```
xref <identifier> [--components AB]
```

**identifier** — one of:
- 10-character WDS ID, e.g. `00057+4549`
- Discoverer code + number string, e.g. `STF   24`

**--components** — two-character component pair to look up (default: `AB`)

### Examples

Look up Albireo (beta Cygni) by WDS ID:

```bash
xref "19307+2758"
```

Look up a specific component pair:

```bash
xref "00057+4549" --components AB
```

Look up by discoverer designation:

```bash
xref "STF   24"
```

## Output

For each component (A, B, ...) the tool prints a table of Gaia DR3 sources sorted by angular separation from the expected WDS position:

```
WDS 19307+2758  BUP 299  comp=AB

  Mag A=3.2  Mag B=5.1  SpType=K3II

--- Component A  (293.18000, +27.97000) ---
  #              source_id   sep(arcsec)   g_mag  delta_mag  teff_gspphot
  1   4318465066277450112          0.412    3.18       0.02          4300
  ...
```

Columns:
- `sep(arcsec)` — angular distance between the Gaia source and the expected WDS component position
- `g_mag` — Gaia G-band magnitude
- `delta_mag` — difference between Gaia G mag and WDS catalog magnitude
- `teff_gspphot` — effective temperature from Gaia GSP-Phot (K)
