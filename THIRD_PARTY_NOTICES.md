# Third-party notices

## NOAA SURFRAD input

Measured irradiance is derived from the NOAA Global Monitoring Laboratory
Surface Radiation Budget (SURFRAD) network. The bundled processed inputs are
15-minute GHI means with provenance and quality records; the upstream raw
`.dat` files are not bundled. Source URLs, per-file SHA-256 and
transformation steps are retained in:

- `code/results/expansion_measured/weather/provenance.json`
- `code/results/strengthening_weather/T2/quality.json`
- `code/results/strengthening_weather/T3/quality.json`

Upstream sources (checked October 2026) include, for example:

- https://gml.noaa.gov/aftp/data/radiation/surfrad/Boulder_CO/2024/tbl24001.dat
- https://gml.noaa.gov/grad/surfrad/

This project does not assert ownership of the provider's input data or
relicense it under MIT. Use provider data according to its applicable terms
and attribution notices; the software license in this repository covers the
project's own software.

Data/Image provided by NOAA Global Monitoring Laboratory, Boulder, Colorado,
USA (https://gml.noaa.gov).

The bundled 15-minute inputs were processed by the authors and are not official
NOAA processed products. The provider's data-use and attribution conditions are
described at https://gml.noaa.gov/about/disclaimer.html . No NOAA endorsement is
implied.

## Dependencies and typography

NumPy, SciPy, Matplotlib, requests, pandas, tabulate and their dependencies are installed separately and retain
their respective upstream licenses. No third-party library binaries or font
files are bundled. Supplied figure exports retain existing typography;
DejaVu Sans is used for regenerated quantitative panels. Availability of
other fonts on another machine is not guaranteed.
