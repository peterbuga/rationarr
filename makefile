
.PHONY: venv
## Creates a virtual environment
venv:
	python3 -m venv venv && \
	. ./venv/bin/activate && \
	python -m pip install pip-tools && \
	python -m pip install --upgrade pip setuptools && \
	python -m pip install wheel twine


.PHONY: install
## Install for production
install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[all]"


.PHONY: install-dev
## Install for development
install-dev: install
	python -m pip install -e ".[dev]" 
# \
# && cd tests-end-to-end && npm install && cd - \
# && pre-commit install

## Run checks (ruff + test)
check:
	isort --check .
	black --check .
	ruff check .
# cd ./tests-end-to-end && npm run prettier-check && cd -
# python -m pytest -m "not integration" --cov=src --cov-report=html:coverage tests/

## Run all tests including the long integration tests
check-all-tests:
	python -m pytest --run-skip-ci


.PHONY: style
## Apply Python Styling on the codebase
style:
	isort .
	black .
	ruff check .


.PHONY: clean
## Cleaning files
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	find . | grep -E ".trash" | xargs rm -rf
	rm -f .coverage

.PHONY: build
## Build package
build:
	if [ -d "dist" ]; then rm dist/*; fi
	python -m build

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) == Darwin && echo '--no-init --raw-control-chars')
