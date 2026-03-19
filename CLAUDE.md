A python program to create a table of cross references between the Washington Double Star Catalog (WDS) and the Gaia DR3.

The WDS data will be imported into an Astropy table using the wds-astropy-table package from pypi. The raw WDS data table will be included in this folder as data/wdsweb_summ2.txt.

The format of the wdsweb_summ2.txt database is summarized in docs/wdsweb_format.txt. The Astropy table produced by wds-astropy-table uses the same columns and data format.

The program ("xref") will run in interactive mode:
 - user supplies a WDS identifier, either as a 10 character "wds id" string or an observer name and number string, along with an optional two character components code (components are AB by default)
 - xref will retrieve the WDS record corresponding to the specified system and components
 - xref will translate the WDS coordinates for the system primary to the coordinates used for Gaia
 - xref will determine the coordinates of each of the target components, using the proper angle and separation information from WDS
 - xref will perform a cone search on Gaia (using the astroquery package) around each of the target component coordinates
 - xref will output a summary of the Gaia sources found for each component, highlighting values such as: distance of each source in Gaia from the target component coordinate derived from WDS, magnitude difference of each source in Gaia vs target magnitude in WDS, spectral type of each source in Gaia and of target in WDS
 - xref will also download a DSS image of the area around the target system, overlaying it with: the location of each Gaia source (numbered 1, 2, 3, etc), the expected location of each WDS component (labeled A, B, C, etc), using a different marker symbol for the Gaia sources and WDS sources

For this iteration, xref is just outputting the data found from Gaia.
