from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        ],
 )
