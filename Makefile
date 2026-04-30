RUN_ARGS ?="config.json"

install:
	uv python install --python3.13
	uv sync --python3.13


ifeq (run, $(firstword $(MAKECMDGOALS)))
  _EXTRA := $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))
  ifneq ($(_EXTRA),)
    RUN_ARGS := $(_EXTRA)
    $(eval $(_EXTRA):;@true)
  endif
endif
run:
	uv run python pac-man.py $(RUN_ARGS)

debug:
	@echo "   Starting debugger..."
	@echo "   Useful commands:"
	@echo "   n (next)       - Execute next line"
	@echo "   s (step)       - Step into function"
	@echo "   c (continue)   - Continue until next breakpoint"
	@echo "   p <var>        - Print variable"
	@echo "   l (list)       - Show source code"
	@echo "   q (quit)       - Quit debugger"
	@echo ""
	uv run python -m pdb pac-man.py $(RUN_ARGS)

lint:
	@uv run flake8 . --extend-exclude=.venv,__pycache__
	@uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@uv run flake8 . --extend-exclude=.venv,__pycache__
	@uv run mypy . --strict

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache
	rm -rf .venv
	rm -rf .vscode
	find . -type d -name output -exec rm -rf {} + 2>/dev/null || true

.PHONY: install  run debug lint lint-strict clean