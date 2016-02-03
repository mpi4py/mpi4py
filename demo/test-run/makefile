.PHONY: default
default: build test clean

PYTHON = python

.PHONY: build
build:
	mkdir -p run-directory/
	cp run-script.py run-directory/__main__.py
	zip -qj run-zipfile.zip run-directory/__main__.py

.PHONY: test
test:
	${PYTHON} test_run.py -v

.PHONY: clean
clean:
	${RM} -r run-directory run-zipfile.zip
