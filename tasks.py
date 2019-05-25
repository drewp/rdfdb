from invoke import task

import sys
sys.path.append('/my/proj/release')
from release import local_release

@task
def release(ctx):
    local_release(ctx)

@task
def mypy(ctx):
    ctx.run('docker build -f Dockerfile.build -t rdfdb_build:latest .')
    ctx.run('docker run --rm -it -v `pwd`:/opt rdfdb_build:latest'
            ' /bin/sh /opt/run_mypy.sh',
            pty=True)

@task
def test(ctx):
    ctx.run('docker build -f Dockerfile.build -t rdfdb_build:latest .')
    ctx.run('docker run --rm -it -v `pwd`:/opt rdfdb_build:latest'
            ' nose2 -v rdfdb.currentstategraphapi_test rdfdb.graphfile_test',
            pty=True)
