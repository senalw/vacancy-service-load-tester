
venv:
	python3 -m venv venv
	./venv/bin/python3 -m pip install --upgrade pip

.PHONY: install
install: venv
	./venv/bin/pip3 install -r requirements.txt

.PHONY: setup
setup: install
	$(MAKE) generate-proto

.PHONY: clean-proto
clean-proto:
	rm -rf src/studio/magicmedia/api/v1/


.PHONY: generate-proto
generate-proto:
	./tools/go/buf generate

.PHONY: lint-proto
lint-proto:
	./tools/go/buf lint

.PHONY: lint-py
lint-py:
	./venv/bin/flake8 .

.PHONY: lint
lint:
	$(MAKE) lint-py

.PHONY: setup-style
setup-style: setup
	./venv/bin/pip3 install --no-cache-dir -r requirements-style.txt
	./venv/bin/pre-commit install --hook-type pre-commit --hook-type pre-push

.PHONY: check-format
check-format: # Check which files will be reformatted
	./venv/bin/black --check .

.PHONY: format
format: # Format files
	./venv/bin/black .
