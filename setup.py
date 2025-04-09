from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

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
    zip_safe=False,
    python_requires='>=3.7',
    keywords='circulations, CTs, WTs, synoptic',
    install_requires=[
        'numpy>=1.19.5',
        'xarray>=0.16.2',
        'matplotlib>=3.2.0',
        'pyproj',
        'cartopy>=0.17.0',
        'cftime',
        'netCDF4',
    ],
)
