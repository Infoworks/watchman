pushd $DOC_HOME
sphinx-apidoc -o tasks ../watchman/tasks -f -M
sphinx-apidoc -o flows ../watchman/flows -f -M
make clean html
popd