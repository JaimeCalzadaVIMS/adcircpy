from datetime import datetime, timedelta
from pathlib import Path
import shutil
import warnings

from adcircpy import AdcircMesh, AdcircRun, Tides
from adcircpy.utilities import download_mesh

DATA_DIRECTORY = Path(__file__).parent.absolute() / 'data'
INPUT_DIRECTORY = DATA_DIRECTORY / 'input' / 'shinnecock'
OUTPUT_DIRECTORY = DATA_DIRECTORY / 'output' / 'example_1'
from adcircpy.forcing.tides import  TidalSource
MESH_DIRECTORY = INPUT_DIRECTORY / 'shinnecock'

# download_mesh(
#     url='https://www.dropbox.com/s/1wk91r67cacf132/NetCDF_shinnecock_inlet.tar.bz2?dl=1',
#     directory=MESH_DIRECTORY,
#     known_hash='99d764541983bfee60d4176af48ed803d427dea61243fa22d3f4003ebcec98f4',
# )

# open mesh file
# mesh = AdcircMesh.open(MESH_DIRECTORY / 'fort.14', crs=4326)
mesh = AdcircMesh.open('./jb20241026_home_mesh.14', crs=4326)
resource=r'E:\pythonProject1\adcircpy\examples\out_tpox_sum.nc'
# initialize tidal forcing and constituents
# tidal_forcing = Tides(TidalSource.TPXO,resource=resource)
tidal_forcing = Tides()
tidal_forcing.use_all()
# tidal_forcing.use_constituent('S1')
# tidal_forcing.use_constituent('S2')
# tidal_forcing.use_constituent('N2')
# tidal_forcing.use_constituent('S2')
# tidal_forcing.use_constituent('K1')
# tidal_forcing.use_constituent('O1')
mesh.add_forcing(tidal_forcing)

# set simulation dates
duration = timedelta(days=30)
start_date = datetime(2024, 5, 1)
end_date = start_date + duration

# instantiate driver object
driver = AdcircRun(mesh, start_date, end_date)

# request outputs
driver.set_elevation_surface_output(sampling_rate=timedelta(minutes=60))
driver.set_velocity_surface_output(sampling_rate=timedelta(minutes=60))

# override default options so the resulting `fort.15` matches the original Shinnecock test case options
driver.timestep = 6.0
driver.DRAMP = 2.0
driver.TOUTGE = 3.8
driver.TOUTGV = 3.8
driver.smagorinsky = False
driver.horizontal_mixing_coefficient = 5.0
driver.gwce_solution_scheme = 'semi-implicit-legacy'
driver.NHAGE=1
if shutil.which('padcirc') is not None:
    driver.run(OUTPUT_DIRECTORY, overwrite=True)
elif shutil.which('adcirc') is not None:
    driver.run(OUTPUT_DIRECTORY, overwrite=True, nproc=1)
else:
    warnings.warn(
        'ADCIRC binaries were not found in PATH. '
        'ADCIRC will not run. Writing files to disk...'
    )
    driver.write(OUTPUT_DIRECTORY, overwrite=True)
