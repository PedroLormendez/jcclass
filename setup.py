from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
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
    setup_requires=[
        "setuptools-git-versioning",
        "numpy"
    ],
    setuptools_git_versioning={
        "enabled": True,
        "version_file": "jcclass/version.py",
        "dev_template": "{tag}.post{ccount}",
        "dirty_template": "{tag}.post{ccount}+dirty"
    },
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
