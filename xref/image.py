"""DSS image download and overlay for WDS/Gaia cross-reference."""

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from astroquery.skyview import SkyView


def plot_field(record, coords, gaia_results, fov=None, output=None):
    """Download a DSS image and overlay WDS component and Gaia source positions.

    Parameters
    ----------
    record : astropy table row
        WDS record for the system.
    coords : dict
        Mapping of component label (e.g. "A", "B") to SkyCoord.
    gaia_results : dict
        Mapping of component label to astropy table of Gaia sources.
    fov : Quantity, optional
        Angular field of view.  Defaults to 4× the widest component
        separation, with a minimum of 2 arcmin.
    output : str, optional
        File path to save the figure.  If None the plot is shown interactively.
    """
    center = coords["A"]

    if fov is None:
        other_coords = [c for lbl, c in coords.items() if lbl != "A"]
        if other_coords:
            max_sep = max(center.separation(c).to(u.arcsec).value for c in other_coords)
        else:
            max_sep = 30
        fov = max(max_sep * 4, 120) * u.arcsec

    # Download DSS image
    images = SkyView.get_images(
        position=center,
        survey=["DSS"],
        radius=fov / 2,
        pixels=600,
    )

    if not images:
        print("Could not download DSS image.")
        return

    hdu = images[0][0]
    wcs = WCS(hdu.header)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection=wcs)

    vmin = np.percentile(hdu.data, 5)
    vmax = np.percentile(hdu.data, 98)
    ax.imshow(hdu.data, origin="lower", cmap="gray", vmin=vmin, vmax=vmax)

    ax.set_xlabel("RA")
    ax.set_ylabel("Dec")
    wds_id = str(record[0]).strip()
    disc = str(record[1]).strip()
    ax.set_title(f"WDS {wds_id}  {disc}")

    # Overlay WDS component positions (squares, labelled A B C …)
    for label, coord in coords.items():
        px, py = wcs.all_world2pix([[coord.ra.deg, coord.dec.deg]], 0)[0]
        ax.plot(px, py, marker="s", ms=14, mfc="none", mec="cyan", mew=1.5, zorder=3)
        ax.annotate(
            label, (px, py),
            xytext=(7, 7), textcoords="offset points",
            color="cyan", fontsize=11, fontweight="bold", zorder=4,
        )

    # Overlay Gaia source positions (circles, numbered 1 2 3 … per component)
    for label, sources in gaia_results.items():
        if sources is None or len(sources) == 0:
            continue
        comp_coord = coords[label]
        gaia_coords = SkyCoord(ra=sources["ra"], dec=sources["dec"], unit=u.deg)
        seps = comp_coord.separation(gaia_coords).to(u.arcsec)
        sorted_pairs = sorted(zip(sources, seps), key=lambda x: x[1])
        for i, (src, _) in enumerate(sorted_pairs, 1):
            src_coord = SkyCoord(ra=src["ra"], dec=src["dec"], unit=u.deg)
            px, py = wcs.all_world2pix([[src_coord.ra.deg, src_coord.dec.deg]], 0)[0]
            ax.plot(px, py, marker="o", ms=12, mfc="none", mec="yellow", mew=1.5, zorder=3)
            ax.annotate(
                f"{label}{i}", (px, py),
                xytext=(5, 5), textcoords="offset points",
                color="yellow", fontsize=9, zorder=4,
            )

    wds_handle = mpatches.Patch(color="cyan", label="WDS components (A, B, …)")
    gaia_handle = mpatches.Patch(color="yellow", label="Gaia sources (A1, A2, …)")
    ax.legend(handles=[wds_handle, gaia_handle], loc="upper right", fontsize=9)

    plt.tight_layout()

    if output:
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"Image saved to {output}")
    else:
        plt.show()
