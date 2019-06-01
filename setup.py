from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    version='0.19.0',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        'rdflib-jsonld',
        'service_identity',
        "autobahn",
        'scales', # use git+http://github.com/drewp/scales.git@master#egg=scales
        ],
    url='https://projects.bigasterisk.com/rdfdb/rdfdb-0.19.0.tar.gz',
    author='Drew Perttula',
    author_email='drewp@bigasterisk.com',
    entry_points={
      'console_scripts': ['rdfdb=rdfdb.service:main'],
    },
 )
