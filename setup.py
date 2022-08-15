from setuptools import find_packages, setup

'''
@Author: Pedro Herrera-Lormendez
Run the following code in your conda environment to make the package available
$python setup.py
'''

vfile = {}
exec(open('jc_class/version.py').read(), vfile)

with open('README.md', 'r') as fh:
	long_description = fh.read()

#with open('jc_class/requirements.txt', 'r') as fh:
#	install_requires = fh.read()


setup(
	name='jc_classification',
	include_package_data = True,
	keywords='circulations, CTs, WTs, synoptic',
	author = 'Pedro Herrera-Lormendez',
	author_email='peth31@gmail.com',
	description = 'Jenkinson and Collison automated gridded classification',
	long_description = long_description,
    long_description_content_type='text/markdown',	
	url = 'https://github.com/PedroLormendez/JC-Classification',
	license = 'MIT',
	packages =['jc_class'],
	zip_safe = False,
	python_requires='>=3.6',
	version_config ={
		'version_callback' : vfile['__version__'],
		'dev_template'  : '{tag}.posst{ccount}',
		'dirty_template': '{tag}.post{ccount}'
		},
	setup_requires = ['setuptools-git-versioning', 'numpy'],
	install_requires = [
						'numpy>=1.19.2',
						'xarray>=0.16.2',
						'matplotlib>=3.2.0',
						'cartopy>=0.17.0',
						'cftime',
						'netCDF4'
	]
	)