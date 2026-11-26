import os
from pathlib import Path
import subprocess
import sys


SCRIPTS = Path(__file__).resolve().parent


def read_prompt(message: str, *, preserve_whitespace: bool = False) -> str:
    print(message, end="", flush=True)
    data = bytearray()
    # Do not buffer input meant for the interactive gh and git subprocesses.
    while True:
        char = os.read(sys.stdin.fileno(), 1)
        if not char:
            if not data:
                raise EOFError
            break
        if char == b"\n":
            break
        data.extend(char)
    answer = data.decode(sys.stdin.encoding or "utf-8")
    return answer if preserve_whitespace else answer.strip()


def choose(options: list[str], prompt: str, default: str | None = None) -> str:
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")
    while True:
        answer = read_prompt(prompt)
        if not answer and default is not None:
            return default
        if answer.isdecimal() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Please enter a valid number.")


def select_remote() -> str:
    result = subprocess.run(
        [
            "gh", "api", "user/repos?per_page=100&affiliation=owner,collaborator,organization_member",
            "--paginate", "--jq", ".[].full_name",
        ],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    repositories = sorted(set(result.stdout.splitlines()), key=str.casefold)
    manual = "Enter OWNER/REPO manually"
    selected = choose([*repositories, manual], "GitHub repository: ")
    if selected == manual:
        selected = read_prompt("Repository (OWNER/REPO): ")
        if not selected:
            raise ValueError("Repository is required.")
    result = subprocess.run(
        ["gh", "repo", "view", selected, "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    repository = result.stdout.strip()
    if not repository:
        raise ValueError("GitHub CLI did not return a repository name.")
    return repository


def repository_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return Path(result.stdout.strip()).resolve()


def select_local() -> Path:
    default = os.environ.get("PROJECTS_DIR", str(Path.home() / "42-projects"))
    directory = Path(read_prompt(f"Projects directory [{default}]: ") or default).expanduser()
    if not directory.is_dir():
        raise ValueError(f"Projects directory does not exist: {directory}")
    candidates = set()

    def raise_walk_error(error: OSError) -> None:
        raise error

    for root, dirs, files in os.walk(directory, onerror=raise_walk_error):
        if ".git" in dirs or ".git" in files:
            candidates.add(str(Path(root).resolve()))
        dirs[:] = [name for name in dirs if name != ".git"]
        for name in dirs:
            path = Path(root) / name
            if path.is_symlink() and (path / ".git").exists():
                candidates.add(str(path.resolve()))
    manual = "Enter a repository path manually"
    selected = choose([*sorted(candidates, key=str.casefold), manual], "Local repository: ")
    if selected == manual:
        selected = read_prompt("Repository path: ")
        if not selected:
            raise ValueError("Repository path is required.")
    return repository_root(Path(selected).expanduser())


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"issue", "project", "pr", "branch"}:
        print("Usage: select_repository.py {issue|project|pr|branch}", file=sys.stderr)
        return 2
    action = sys.argv[1]
    try:
        remote = select_remote() if action != "branch" else None
        local = select_local() if action in {"pr", "branch"} else None
        if remote:
            print(f"GitHub repository: {remote}")
        if local:
            print(f"Local repository: {local}")
        if read_prompt(f"Continue with {action}? [y/N]: ").lower() != "y":
            print("Canceled.")
            return 0
        env = os.environ.copy()
        if remote:
            env["GH_REPO"] = remote
        script = {
            "issue": "new_issue.py",
            "project": "new_project.py",
            "pr": "new_pull_request.py",
            "branch": "new-branch.sh",
        }[action]
        interpreter = sys.executable if action in {"issue", "project", "pr"} else "bash"
        subprocess.run([interpreter, str(SCRIPTS / script)], cwd=local, env=env, check=True)
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled.", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit code {error.returncode}.", file=sys.stderr)
        return error.returncode if error.returncode > 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
