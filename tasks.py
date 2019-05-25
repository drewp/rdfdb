from invoke import task

import sys
sys.path.append('/my/proj/release')
from release import local_release

@task
def release(ctx):
    local_release(ctx)

@task
def mypy(ctx):
    ctx.run('docker build -f Dockerfile.mypy -t rdfdb_mypy:latest .')
    ctx.run('docker run --rm -it -v `pwd`:/opt rdfdb_mypy:latest'
            ' /bin/sh /opt/run_mypy.sh',
            pty=True)
