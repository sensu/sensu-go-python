.PHONY: setup
setup:
	test -d venv && python3 -m venv venv
	venv/bin/pip install -U pip wheel twine
	venv/bin/pip install -e .[dev]

.PHONY: dist
dist:
	venv/bin/python setup.py sdist bdist_wheel

.PHONY: publish
publish:
	venv/bin/twine upload dist/*

.PHONY: clean
clean:
	rm -rf dist
