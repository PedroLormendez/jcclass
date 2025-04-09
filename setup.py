from setuptools import setup, find_packages

setup(
    name='jcclass',
    description='Jenkinson and Collison automated gridded classification',
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
