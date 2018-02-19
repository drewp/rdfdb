from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    version='9',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        ],
 )
