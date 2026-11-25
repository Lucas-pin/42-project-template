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

List available workflows:

```bash
make help
```

## Workflows

| Command | Purpose |
| --- | --- |
| `make setup-gh` | Install or update GitHub CLI and authenticate |
| `make repo` | Create a GitHub repository from this template |
| `make project` | Create a Projects v2 board |
| `make issue` | Create an issue interactively |
| `make branch` | Create and switch to a feature branch |
| `make labels` | Create standard repository labels |
| `make pr` | Create a pull request |

Run these commands from the root of a GitHub repository. `make repo` creates a repository from `Lucas-pin/42-project-template` and can optionally clone it. The template's files, including its README, are included in the new repository.
