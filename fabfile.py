from subprocess import check_call, check_output, CalledProcessError

def release():
    try:
        check_call(['darcs', 'wh', 'rdfdb/patch.py'])
        raise SystemExit("\n^^ record these changes first")
    except CalledProcessError: # nothing new
        pass
    ver = check_output(['env/bin/bump', '-qm', 'setup.py']).strip()
    check_call(['darcs', 'rec', '--all', '--name', "version %s" % ver, '.'])
    check_call(['python', 'setup.py', 'sdist'])
    check_call(['cp', 'dist/rdfdb-%s.tar.gz' % ver, '/my/site/projects/rdfdb/'])
