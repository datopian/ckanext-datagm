from setuptools import setup, find_packages

version = '0.1'

setup(
    name='ckanext-datagm',
    version=version,
    description="Customisations of CKAN for DataGM",
    long_description="""\
    """,
    classifiers=[],
    keywords='',
    author='Seb Bacon',
    author_email='seb.bacon@gmail.com',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    entry_points='''
        [ckan.plugins]
        datagm=ckanext.datagm.plugin:DataGMPlugin

        [ckan.forms]
        datagm_package_form = ckanext.datagm.package_form:get_datagm_fieldset
    ''',
)
