import subprocess
import sys
from dataclasses import dataclass

from select_repository import choose, read_prompt


@dataclass(frozen=True)
class SourceBranch:
    name: str
    remote: bool = False


def command_output(*args: str) -> str:
    result = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE)
    return result.stdout.strip()


def source_branches() -> tuple[list[SourceBranch], str]:
    current = command_output("git", "branch", "--show-current")
    local = command_output("git", "for-each-ref", "--format=%(refname:strip=2)", "refs/heads").splitlines()
    remote_refs = command_output(
        "git", "for-each-ref", "--format=%(refname)%09%(symref)", "refs/remotes"
    ).splitlines()
    branches = [SourceBranch(name) for name in local]
    for line in remote_refs:
        ref, _, symbolic = line.partition("\t")
        if symbolic or not ref.startswith("refs/remotes/"):
            continue
        name = ref.removeprefix("refs/remotes/")
        if "/" in name and name.split("/", 1)[1] not in local:
            branches.append(SourceBranch(name, remote=True))
    if not branches:
        raise ValueError("No local or remote branches are available in this clone.")
    return branches, current


def select_source() -> tuple[SourceBranch, str]:
    branches, current = source_branches()
    labels = [
        f"{branch.name} ({'remote' if branch.remote else 'local'}"
        f"{', current' if not branch.remote and branch.name == current else ''})"
        for branch in branches
    ]
    default = next(
        (label for branch, label in zip(branches, labels) if not branch.remote and branch.name == current),
        None,
    )
    prompt = "Source branch [current]: " if default else "Source branch: "
    selection = choose(labels, prompt, default)
    return branches[labels.index(selection)], current


def select_base() -> tuple[str, str]:
    repo = command_output("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    default = command_output("gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name")
    branches = command_output(
        "gh", "api", "repos/{owner}/{repo}/branches?per_page=100",
        "--paginate", "--jq", ".[].name",
    ).splitlines()
    if not repo or not default or default not in branches:
        raise ValueError("Could not retrieve the target repository and its default branch.")
    branches = [default, *sorted(set(branches) - {default}, key=str.casefold)]
    labels = [f"{branch} (default)" if branch == default else branch for branch in branches]
    selection = choose(labels, "Target branch [default]: ", labels[0])
    return repo, branches[labels.index(selection)]


def switch_source(branch: SourceBranch, current: str) -> None:
    if not branch.remote and branch.name == current:
        return
    if command_output("git", "status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Commit or stash local changes before switching the source branch.")
    args = ["git", "switch", "--no-overwrite-ignore"]
    if branch.remote:
        name = branch.name.split("/", 1)[1]
        args.extend(["--track", "-c", name, "--", f"refs/remotes/{branch.name}"])
    else:
        args.extend(["--", branch.name])
    subprocess.run(args, check=True)


def main() -> int:
    try:
        source, current = select_source()
        repo, base = select_base()
        draft = read_prompt("Create pull request draft? [y/N]: ").lower() == "y"
        switch_source(source, current)
        args = ["gh", "pr", "create", "--base", base, "--template", "PULL_REQUEST_TEMPLATE.md"]
        if draft:
            args.append("--draft")
        print(f"Creating pull request in {repo} from {source.name} to {base}...", flush=True)
        subprocess.run(args, check=True)
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled.", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
