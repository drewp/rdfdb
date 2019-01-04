from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    version='0.7.0',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        'rdflib-jsonld',
        'service_identity',
        ],
    entry_points={
        'console_scripts': ['rdfdb=rdfdb.service:main'],
    },
 )
