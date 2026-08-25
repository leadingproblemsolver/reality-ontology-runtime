PYTHON ?= python

.PHONY: test demo verify

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

demo:
	PYTHONPATH=src $(PYTHON) -m reality_ontology.cli --db .runtime/reality.db demo

verify:
	PYTHONPATH=src $(PYTHON) -m reality_ontology.cli --db .runtime/reality.db verify-invariants
