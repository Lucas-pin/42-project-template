# 42 Project Template

**Less GitHub setup, more time to build.**

42 Project Template aims to make the everyday work around 42 projects easier: creating repositories, organizing tasks and collaborating through GitHub, using familiar `make` commands.

> **Work in progress:** this project is in beta and is gradually moving from shell scripts to Python. Features may change, and most have not yet been extensively tested.

This is a collaborative project: try it, use it for your projects, report problems and open a pull request with a fix, improvement or new feature. Whether you're learning or already comfortable with GitHub, contributions are welcome!

## How it works

The goal is to have one **central toolbox** to manage multiple projects. In the future, you'll be able to select a GitHub repository or a local clone before running a workflow.

**Today, that selection is not implemented.** Run commands from the root of the repository you want to manage, using its copy of this Makefile and scripts. `make repo` currently creates a repository from this template, so the new repository also receives the toolbox files. Separating the toolbox from project files is planned.

### Get started

You need Git, a GitHub account, GitHub CLI and Python 3.10 or later for the migrated workflows. The `make setup-gh` installer targets Linux x86_64 and ARM64.

```bash
git clone https://github.com/Lucas-pin/42-project-template.git
cd 42-project-template
make setup-gh
make help
```

`make setup-gh` installs or updates `gh` and starts authentication if needed. If you already have `gh`, use `make gh-auth` or `gh auth login` instead. You can choose HTTPS or SSH for Git operations; use `gh auth status` or `gh auth switch` to inspect or change accounts.

The Python migration uses only the standard library, with Python 3.10 compatibility for 42 computers. A Poetry environment and a newer minimum version are possibilities for the future.

## What's available?

All workflows are **beta**. “Tested” below means focused automated tests with a simulated `gh`, not extensive testing against GitHub.

| Command | What it does | Implementation | Test status |
| --- | --- | --- | --- |
| `make setup-gh` | Install or update GitHub CLI and authenticate | Shell / Make | Beta: limited testing |
| `make gh-auth` | Authenticate with GitHub CLI | Make | Beta: limited testing |
| `make repo` | Create a repository from this template | Shell | Tested: simulated workflow |
| `make project` | Create a GitHub Projects board | Shell | Beta: limited testing |
| `make issue` | Create an issue using GitHub CLI | Shell | Beta: limited testing |
| `make branch` | Create and switch to a local branch | Shell | Beta: limited testing |
| `make labels` | Create a standard set of labels | Python | Beta: limited testing |
| `make pr` | Create a pull request from the current branch | Shell | Beta: limited testing |

### Repository and board

- **`make repo`:** prompts for the name, visibility and description, creates the repository from `Lucas-pin/42-project-template`, then offers to clone it. The template's README, Makefile and scripts are included.
- **`make project`:** creates a personal or organization-owned Projects v2 board and offers to link it to the current repository. You need permission to create the board; `gh` requires the board and repository to have the same owner when linking. A failed link does not undo board creation.

Projects require additional permissions. For a stored `gh` OAuth login, grant them with `gh auth refresh --scopes project` if needed. Environment tokens must be updated separately.

### Issues, branches and pull requests

- **`make issue`:** opens GitHub CLI's interactive flow, where you can select an issue template or start blank and add labels through the metadata prompt.
- **`make branch`:** creates and switches to a branch locally; it does not require GitHub authentication or publish the branch.
- **`make pr`:** prompts for the base branch and whether the PR should be a draft, then uses the PR template in GitHub CLI's interactive flow. `gh` may also prompt to push the current branch.

GitHub CLI reads issue and PR templates from the repository on GitHub, so template changes must be available on its default branch.

### Labels and authentication

- **`make labels`:** creates `bug`, `enhancement`, `documentation`, `testing` and `refactor`, skipping labels that already exist.
- **Authentication:** `gh` also supports `GH_TOKEN` and `GITHUB_TOKEN`, which take precedence over stored credentials. Ensure the token has the permissions needed for your operations; never commit it to a repository.

## Where we're heading

1. **Migrate to Python:** move workflows incrementally, keep the current commands and add focused tests.
2. **Central repository selection:** choose a GitHub repository for remote workflows or a local clone for branches; confirm the target before changes.
3. **Guided project setup:** create and clone a repository, set up labels and optionally add a board.
4. **Issue → branch → PR:** optionally create a linked remote branch, reuse or create a clone and prepare a PR referencing the issue. Ordinary branches remain local until pushed.
5. **Status and collaboration:** list issues and PRs, inspect branch status, open resources and support assignments.
6. **42 checks and automation:** offer optional Norminette, build and test checks, plus parameters for repeatable workflows.

For a new clone in the linked-issue flow, the planned experience is to choose the configured default location or a custom path, name the clone folder and check out the branch.

## Contributing

Try a workflow, open an issue to share feedback, or submit a pull request. Small fixes, documentation improvements, tests and new ideas all help.

The repository includes a simulated test for repository creation:

```bash
bash tests/new-repository.sh
```

Please describe what you changed and how you tested it in your pull request.
