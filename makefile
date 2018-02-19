release:
	darcs wh && { echo "\n^^ record these changes first"; exit 1; } || true
	env/bin/python -m incremental.update rdfdb --dev
	$(eval VER:=$(shell env/bin/python -c 'import rdfdb; print(rdfdb.__version__.short())'))
	darcs rec --all --name "version $(VER)" .
	python setup.py sdist
	cp dist/rdfdb-$(VER).tgz /my/site/projects/rdfdb/
