.PHONY: install test lint clean build publish

install:
	pip install -e .

test:
	pytest

lint:
	pre-commit run --all-files

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

run:
	python -m src.cli analyze --repo-path=. --pr-number=1 --repo-name=yourusername/repo

local:
	python -m src.cli local --repo-path=. 