from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    version='12',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        ],
 )
