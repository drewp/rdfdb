from setuptools import setup, find_packages
 
setup(
    name='rdfdb',
    use_incremental=True,
    setup_requires=['incremental'],
    packages=find_packages(),
    install_requires=[
        'incremental',
        'rdflib',
        'cyclone',
        'mock',
        'treq',
        ],
 )
