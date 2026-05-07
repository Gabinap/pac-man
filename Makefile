RUN_ARGS ?="data/config.json"

CONVERTER := .venv/lib/python3.13/site-packages/gltf/_converter.py

install:
	uv python install
	rm -f uv.lock
	uv add mazegenerator-2.0.1-py3-none-any.whl
	uv sync
	@$(MAKE) patch

patch:
	@python3 scripts/apply_patches.py

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
	rm -rf .vscode
	find . -type d -name output -exec rm -rf {} + 2>/dev/null || true

.PHONY: install patch run debug lint lint-strict clean