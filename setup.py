from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jcclass",
    include_package_data=True,
    keywords="circulations, CTs, WTs, synoptic",
    author="Pedro Herrera-Lormendez",
    author_email="peth31@gmail.com",
    description="Jenkinson and Collison automated gridded classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PedroLormendez/jcclass",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.7",
    setuptools_git_versioning=True,
    setup_requires=["setuptools-git-versioning"],
    install_requires=[
        "numpy>=1.19.5",
        "xarray>=0.16.2",
        "matplotlib>=3.2.0",
        "pyproj",
        "cartopy>=0.17.0",
        "cftime",
        "netCDF4",
        "pytest"
    ],
)
