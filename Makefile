.DEFAULT_GOAL := help
.PHONY: help setup-gh gh-auth check-gh repo project issue pr branch labels template-info

export PATH := $(HOME)/.local/bin:$(PATH)

help:
	@echo "make setup-gh    -> install/update GitHub CLI and authenticate"
	@echo "make gh-auth     -> authenticate with GitHub CLI"
	@echo "make repo        -> create a new GitHub repository"
	@echo "make project     -> create a GitHub Projects v2 board"
	@echo "make issue       -> create an issue interactively"
	@echo "make pr          -> create a pull request"
	@echo "make branch      -> create and switch to a feature branch"
	@echo "make labels      -> create a standard set of repository labels"
	@echo "make template-info -> print repository template guidance"

setup-gh:
	@bash dev-utils/scripts/setup-gh.sh
	PATH="$(HOME)/.local/bin:$$PATH" $(MAKE) gh-auth

gh-auth:
	@command -v gh >/dev/null || { echo "gh is missing; run 'make setup-gh'." >&2; exit 1; }
	@if gh auth status --active >/dev/null 2>&1; then \
		echo "gh is already authenticated."; \
	else \
		gh auth login; \
	fi

check-gh:
	@command -v gh >/dev/null || { echo "gh is missing; run 'make setup-gh'." >&2; exit 1; }
	@if status="$$(gh auth status --active 2>&1)"; then :; else \
		printf '%s\n' "$$status" >&2; \
		echo "Check your gh credentials or run 'make gh-auth'." >&2; \
		exit 1; \
	fi

repo: check-gh
	@bash dev-utils/scripts/new-repository.sh

project: check-gh
	@bash dev-utils/scripts/new-project.sh || { \
		echo "If project permissions are missing, see the authentication instructions in README.md." >&2; \
		exit 1; \
	}

issue: check-gh
	@bash dev-utils/scripts/new-issue.sh

pr: check-gh
	@bash dev-utils/scripts/new-pull-request.sh

branch:
	@bash dev-utils/scripts/new-branch.sh

labels: check-gh
	@python3 dev-utils/scripts/setup_labels.py

template-info:
	@cat TEMPLATE.md
