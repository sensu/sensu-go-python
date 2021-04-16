.PHONY: setup
setup:
	pip install -U pip wheel twine
	pip install -e .[dev]

.PHONY: format
format:
	black src/sensu_go tests

.PHONY: lint
lint:
	black --check --diff src/sensu_go tests
	flake8 src/sensu_go tests
	mypy --strict src/sensu_go

.PHONY: unit
unit:
	pytest --import-mode=importlib tests/unit

.PHONY: dist
dist:
	python setup.py sdist bdist_wheel

.PHONY: publish
publish: clean dist
	twine check dist/*
	twine upload dist/*

.PHONY: clean
clean:
	rm -rf dist build
	find src/sensu_go -name __pycache__ -type d | xargs rm -rf
