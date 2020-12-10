.PHONY: setup
setup:
	test -d venv && python3 -m venv venv
	venv/bin/pip install -U pip wheel twine
	venv/bin/pip install -e .[dev]

.PHONY: format
format:
	venv/bin/black -l 79 src/sensu_go tests

.PHONY: lint
lint:
	venv/bin/black --check --diff -l 79 src/sensu_go tests
	venv/bin/flake8 src/sensu_go
	venv/bin/mypy --strict src/sensu_go

.PHONY: unit
unit:
	venv/bin/pytest --import-mode=importlib tests/unit

.PHONY: dist
dist:
	venv/bin/python setup.py sdist bdist_wheel

.PHONY: publish
publish:
	venv/bin/twine upload dist/*

.PHONY: clean
clean:
	rm -rf dist
