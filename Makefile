.PHONY: setup test demo reset
setup:
	python -m pip install -e '.[dev]'

test:
	pytest

demo:
	python -m reality_ontology.cli --db .runtime/reality.db demo

reset:
	rm -rf .runtime
