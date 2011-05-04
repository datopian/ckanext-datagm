from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-datagm',
	version=version,
	description="Customisations of CKAN for DataGM",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Seb Bacon',
	author_email='seb.bacon@gmail.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.datagm'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	datagm=ckanext.datagm.plugin:DataGMPlugin

        [ckan.forms]
        datagm_package_form = ckanext.datagm.package_form:get_datagm_fieldset
	""",
)
