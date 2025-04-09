from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='jcclass',
    description='Jenkinson and Collison automated gridded classification',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pedro Herrera-Lormendez',
    author_email='peth31@gmail.com',
    url='https://github.com/PedroLormendez/jcclass',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.5',
        'xarray>=0.16.2',
        'matplotlib>=3.2.0',
        'pyproj',
        'cartopy>=0.17.0',
        'cftime',
        'netCDF4'
    ],
)
