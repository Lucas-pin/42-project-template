# 42 Project Template

A reusable repository template for 42 projects. It provides a Makefile and GitHub CLI scripts for creating repositories, Projects v2 boards, issues, branches, labels, and pull requests.

## Requirements

- Ubuntu or Debian
- Git
- GitHub CLI
- A GitHub account

## Setup

```bash
make setup-gh
```

This installs or updates `gh` and runs the interactive `gh auth login` flow if needed. If `gh` is already installed, use `make gh-auth` or run `gh auth login` directly. Choose HTTPS or SSH for Git operations during login. Check or switch accounts with `gh auth status` and `gh auth switch`.

`GH_TOKEN` and `GITHUB_TOKEN` are also supported and take precedence over stored credentials. Configure these tokens with the permissions needed for the operations you run; `gh` cannot update an environment token for you. Avoid committing tokens to your repository.

GitHub Projects needs additional permissions. If a project command reports missing permissions and you use a stored `gh` OAuth login, run:

```bash
gh auth refresh --scopes project
```

For an environment token, update or replace the token with one that has the required Projects access instead. `make branch` works locally and does not require GitHub authentication.

List available workflows:

```bash
make help
```

## Workflows

| Command | Purpose |
| --- | --- |
| `make setup-gh` | Install or update GitHub CLI and authenticate |
| `make gh-auth` | Authenticate with GitHub CLI |
| `make repo` | Create a GitHub repository from this template |
| `make project` | Create a Projects v2 board for a user or organization |
| `make issue` | Create an issue interactively using a template |
| `make branch` | Create and switch to a feature branch |
| `make labels` | Create standard repository labels |
| `make pr` | Create a pull request using the PR template |

Run these commands from the root of a GitHub repository. `make repo` creates a repository from `Lucas-pin/42-project-template` and can optionally clone it. The template's files, including its README, are included in the new repository.

`make project` defaults to the authenticated user but also accepts an organization or another user. You need permission to create projects for the selected owner. If linking the project to the current repository, GitHub CLI requires both to have the same owner; linking failures do not undo project creation.

`make issue` uses GitHub CLI's interactive template selection, including a blank issue option. Select labels through its metadata prompt. `make pr` starts its interactive description from `PULL_REQUEST_TEMPLATE.md`, asks for confirmation, and still supports draft PRs. GitHub CLI reads these templates from the repository on GitHub, so template changes must be available on its default branch.
