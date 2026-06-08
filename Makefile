.PHONY: lint test build verify

lint:
	python2 -m py_compile royalmail.py

test:
	python2 -m unittest discover -s tests

build: lint

verify: lint test build
