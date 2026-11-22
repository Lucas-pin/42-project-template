.DEFAULT_GOAL := help
.PHONY: help setup-gh gh-auth check-gh repo project issue pr branch labels template-info

export PATH := $(HOME)/.local/bin:$(PATH)

help:
	@echo "make setup-gh    -> install/update GitHub CLI and authenticate"
	@echo "make gh-auth     -> authenticate and verify repository/project scopes"
	@echo "make repo        -> create a new GitHub repository"
	@echo "make project     -> create a GitHub Projects v2 board"
	@echo "make issue       -> create an issue interactively"
	@echo "make pr          -> create a pull request"
	@echo "make branch      -> create and switch to a feature branch"
	@echo "make labels      -> create a standard set of repository labels"
	@echo "make template-info -> print repository template guidance"

setup-gh:
	@./dev-utils/scripts/setup-gh.sh
	PATH="$(HOME)/.local/bin:$$PATH" $(MAKE) gh-auth

gh-auth:
	@if ! gh auth status >/dev/null 2>&1; then \
		echo "Authenticating gh with repo, project, and workflow scopes..."; \
		gh auth login --scopes repo,project,workflow; \
	else \
		status="$$(gh auth status 2>&1)"; \
		if ! printf '%s\n' "$$status" | grep "Token scopes" | grep -q "'repo'" \
			|| ! printf '%s\n' "$$status" | grep "Token scopes" | grep -q "'project'" \
			|| ! printf '%s\n' "$$status" | grep "Token scopes" | grep -q "'workflow'"; then \
			echo "Updating gh scopes to repo,project,workflow..."; \
			gh auth refresh --scopes repo,project,workflow; \
		else \
			echo "gh is already authenticated with the required scopes."; \
		fi; \
	fi

check-gh:
	@command -v gh >/dev/null || { echo "gh is missing; run 'make setup-gh'."; exit 1; }
	@gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated; run 'make setup-gh'."; exit 1; }
	@status="$$(gh auth status 2>&1)"; \
	for scope in repo project workflow; do \
		printf '%s\n' "$$status" | grep "Token scopes" | grep -q "'$$scope'" \
			|| { echo "Missing the $$scope scope; run 'make setup-gh'."; exit 1; }; \
	done

repo: check-gh
	@./dev-utils/scripts/new-repository.sh

project: check-gh
	@./dev-utils/scripts/new-project.sh

issue: check-gh
	@./dev-utils/scripts/new-issue.sh

pr: check-gh
	@./dev-utils/scripts/new-pull-request.sh

branch: check-gh
	@./dev-utils/scripts/new-branch.sh

labels: check-gh
	@./dev-utils/scripts/setup-labels.sh

template-info:
	@cat TEMPLATE.md
