# 42 Project Template

**Less GitHub setup, more time to build.**

42 Project Template aims to make the everyday work around 42 projects easier: creating repositories, organizing tasks and collaborating through GitHub, using familiar `make` commands.

> **Work in progress:** this project is in beta. The workflow scripts have been migrated from shell to Python, but features may change and most have not yet been extensively tested.

This is a collaborative project: try it, use it for your projects, report problems and open a pull request with a fix, improvement or new feature. Whether you're learning or already comfortable with GitHub, contributions are welcome!

## How it works

Run `make` from this **central toolbox** to manage multiple projects. Issues and boards start by selecting a GitHub repository; branches start by selecting a local clone. Pull requests select both the GitHub target and a local clone. Each workflow shows the selection and asks for confirmation.

`make labels` still operates on the repository containing the Makefile. `make repo` creates a repository from this template, so the new repository also receives the toolbox files. Centralizing the remaining workflows and separating toolbox files from generated projects are planned.

For local clones, the default directory is `~/42-projects`. Set `PROJECTS_DIR` to change it, for example `export PROJECTS_DIR="$HOME/projects"`. Local repository selection requires an existing directory and searches it and its subdirectories for Git repositories and worktrees. It does not traverse symlinked directories. The issue workflow can also create a new clone in the default or a custom directory.

### Get started

You need Git, a GitHub account, GitHub CLI and Python 3.10 or later. The `make setup-gh` installer targets Linux x86_64 and ARM64.

```bash
git clone https://github.com/Lucas-pin/42-project-template.git
cd 42-project-template
make setup-gh
make help
```

`make setup-gh` downloads the latest `gh` into `~/.local/bin/gh` and starts authentication if needed. If you already have `gh`, use `make gh-auth` or `gh auth login` instead. You can choose HTTPS or SSH for Git operations; use `gh auth status` or `gh auth switch` to inspect or change accounts.

The Python migration uses only the standard library, with Python 3.10 compatibility for 42 computers. A Poetry environment and a newer minimum version are possibilities for the future.

## What's available?

All workflows are **beta**. “Tested” below means focused automated tests with a simulated `gh`, not extensive testing against GitHub.

| Command | What it does | Implementation | Test status |
| --- | --- | --- | --- |
| `make setup-gh` | Install or update GitHub CLI and authenticate | Python / Make | Beta: limited testing |
| `make gh-auth` | Authenticate with GitHub CLI | Make | Beta: limited testing |
| `make repo` | Create a repository from this template | Python | Tested: simulated workflow |
| `make project` | Select a GitHub repository and create a Projects board | Python | Tested: simulated workflow |
| `make view-project` | Add a view to an existing project | Python | Tested: simulated workflow |
| `make issue` | Create an issue and optionally add it to a project, create a branch and clone | Python | Tested: simulated workflow |
| `make branch` | Select a local clone and create a branch | Python | Tested: local Git |
| `make labels` | Create a standard set of labels | Python | Beta: limited testing |
| `make pr` | Select a GitHub repository, clone and branches to create a PR | Python | Tested: simulated workflow |

### Repository and board

- **`make repo`:** prompts for the name, visibility and description, creates the repository from `Lucas-pin/42-project-template`, then offers to clone it under `PROJECTS_DIR` (default: `~/42-projects`). The directory is created if needed. The template's README, Makefile and scripts are included.
- **`make project`:** selects a repository, creates a Projects v2 project under its user or organization and links it automatically. Choose the initial view: **Board** (default), **Table** or **Roadmap**. You need permission to create and link the project; if linking or setting the view fails, the project is not deleted.
- **`make view-project`:** choose a user or organization (defaults to your account), select a project with the arrow keys and Enter, and add a named Board, Table or Roadmap view. Press `q` to cancel. The menu shows up to 1,000 open projects; you can also enter a project number manually. Without an interactive terminal, select the menu position, not the GitHub project number. Existing views remain unchanged.

Each layout presents the same project items differently:

- **Board:** kanban-style columns, useful for tracking status.
- **Table:** a spreadsheet-like view of items and their fields.
- **Roadmap:** a timeline for scheduling work with dates or iterations.

You can change a view or add others later. Linking a repository makes the project accessible from its Projects tab; it does **not** automatically add the repository's issues or PRs as project items.

Learn more in GitHub's documentation: [creating a project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project), [changing view layouts](https://docs.github.com/en/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/changing-the-layout-of-a-view), [linking a repository](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-your-project/adding-your-project-to-a-repository), and [adding items](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/adding-items-to-your-project).

Projects require additional permissions. For a stored `gh` OAuth login, grant them with `gh auth refresh --scopes project` if needed. Environment tokens must be updated separately.

### Issues, branches and pull requests

- **`make issue`:** opens GitHub CLI's interactive flow, including templates and labels. After creating the issue, optionally add it to an open Project v2 linked to that repository. You can also create a named remote branch linked to the issue and optionally clone the repository with that branch checked out. Choose a clone directory and folder name; existing destinations are not overwritten. If a later step fails, the issue and any completed remote changes remain in GitHub.
- **`make branch`:** creates and switches to a branch locally; it does not require GitHub authentication or publish the branch.
- **`make pr`:** select the target GitHub repository and a relevant local clone, then select the source branch from local and tracked remote branches and the target branch from GitHub. Enter accepts the current source and the repository's default target. Switching source branches requires a clean working tree; remote selections create a local tracking branch. The selected branch remains checked out even if PR creation fails. Choose whether the PR should be a draft. GitHub CLI uses the PR template and may also prompt to push the source branch.

The GitHub repository menu lists repositories accessible to the authenticated user and includes manual `OWNER/REPO` entry. Listing and validation failures stop the workflow; no changes are made before confirmation.

GitHub CLI reads issue and PR templates from the repository on GitHub, so template changes must be available on its default branch.

### Labels and authentication

- **`make labels`:** creates `bug`, `enhancement`, `documentation`, `testing` and `refactor`, skipping labels that already exist.
- **Authentication:** `gh` also supports `GH_TOKEN` and `GITHUB_TOKEN`, which take precedence over stored credentials. Ensure the token has the permissions needed for your operations; never commit it to a repository.

## Where we're heading

1. **Python migration:** completed for workflow scripts; continue adding focused tests.
2. **Central repository selection:** implemented for issues, boards, PRs and local branches; extend it to the remaining workflows.
3. **Guided project setup:** create and clone a repository, set up labels and optionally add a board.
4. **Issue → branch → PR:** create a linked remote branch and optionally clone it; reuse an existing clone and prepare a PR referencing the issue in a future step. Ordinary branches remain local until pushed.
5. **Status and collaboration:** list issues and PRs, inspect branch status, open resources and support assignments.
6. **42 checks and automation:** offer optional Norminette, build and test checks, plus parameters for repeatable workflows.

## Contributing

Try a workflow, open an issue to share feedback, or submit a pull request. Small fixes, documentation improvements, tests and new ideas all help.

Run the Python tests and the simulated repository creation test with:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
bash tests/new-repository.sh
```

Please describe what you changed and how you tested it in your pull request.
