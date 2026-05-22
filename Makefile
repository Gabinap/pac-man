PYTHON_VERSION := $(shell cat .python-version)
RUN_ARGS       ?= "data/config.json"

# Bypass pyenv shims: locate the actual uv binary
_UV_DIRECT := $(wildcard $(HOME)/.local/bin/uv $(HOME)/.cargo/bin/uv /usr/local/bin/uv)
UV := $(if $(_UV_DIRECT),$(firstword $(_UV_DIRECT)),\
      $(shell find $(HOME)/.pyenv/versions -maxdepth 3 -name uv -type f 2>/dev/null | head -1))

ifeq ($(UV),)
$(error uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh)
endif

install:
	$(UV) python install $(PYTHON_VERSION)
	$(UV) sync --frozen
	@$(MAKE) patch

patch:
	@$(UV) run python tools/apply_patches.py
	@$(MAKE) clean-model-cache

clean-model-cache:
	@rm -f ~/.cache/panda3d/*.bam ~/.cache/panda3d/index-*.boo 2>/dev/null || true
	@echo "Panda3D model cache cleared"

ifeq (run, $(firstword $(MAKECMDGOALS)))
  _EXTRA := $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))
  ifneq ($(_EXTRA),)
    RUN_ARGS := $(_EXTRA)
    $(eval $(_EXTRA):;@true)
  endif
endif
run:
	rm -f ~/.cache/panda3d/ophanim_angel.boo \
	~/.cache/panda3d/tuna_fish.boo \
	~/.cache/panda3d/index_name.txt 2>/dev/null
	$(UV) run python pac-man.py $(RUN_ARGS)

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
	$(UV) run python -m pdb pac-man.py $(RUN_ARGS)

lint:
	@$(UV) run flake8 . --extend-exclude=.venv,__pycache__
	@$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(UV) run flake8 . --extend-exclude=.venv,__pycache__
	@$(UV) run mypy . --strict

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache
	rm -rf .vscode
	find . -type d -name output -exec rm -rf {} + 2>/dev/null || true

.PHONY: install patch clean-model-cache run debug lint lint-strict clean
