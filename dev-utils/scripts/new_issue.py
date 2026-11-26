import errno
import fcntl
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import termios
from urllib.parse import urlsplit

from create_project_view import Project, choose_project, get_json, parse_project
from select_repository import default_projects_directory, read_prompt


PROJECTS_QUERY = """
query($owner: String!, $name: String!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    projectsV2(first: 100, after: $endCursor) {
      nodes { id number title url closed }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

ADD_ITEM_QUERY = """
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item { id }
  }
}
"""


def issue_url(output: str, repository: str) -> str | None:
    lines = output.splitlines()
    if not lines:
        return None
    url = lines[-1].strip()
    parsed = urlsplit(url)
    parts = parsed.path.strip("/").split("/")
    if (
        parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment
        or len(parts) != 4 or "/".join(parts[:2]).casefold() != repository.casefold()
        or parts[2] != "issues" or not parts[3].isascii() or not parts[3].isdecimal()
        or int(parts[3]) < 1
    ):
        return None
    return url


def create_issue(repository: str) -> str:
    # gh requires stdout to be a terminal for its interactive issue prompts.
    master, slave = os.openpty()
    try:
        if sys.stdout.isatty():
            size = os.get_terminal_size(sys.stdout.fileno())
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", size.lines, size.columns, 0, 0))
        process = subprocess.Popen(["gh", "issue", "create"], stdout=slave)
    except (OSError, KeyboardInterrupt):
        os.close(master)
        raise
    finally:
        os.close(slave)
    output = bytearray()
    try:
        while True:
            try:
                chunk = os.read(master, 4096)
            except OSError as error:
                if error.errno == errno.EIO:
                    break
                raise
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            output.extend(chunk)
    except (OSError, KeyboardInterrupt):
        process.terminate()
        process.wait()
        raise
    finally:
        os.close(master)
    result = process.wait()
    url = issue_url(output.decode("utf-8", errors="replace"), repository)
    if result:
        detail = f" Issue already created: {url}" if url else " Check GitHub before retrying."
        raise RuntimeError(f"GitHub CLI exited with code {result}.{detail}")
    if not url:
        raise RuntimeError("Could not confirm issue creation. Check GitHub before retrying.")
    return url


def linked_projects(repository: str) -> list[Project]:
    owner, name = repository.split("/", 1)
    projects = []
    cursor = None
    seen_cursors = set()
    while True:
        args = [
            "api", "graphql", "-f", f"query={PROJECTS_QUERY}",
            "-f", f"owner={owner}", "-f", f"name={name}",
        ]
        if cursor:
            args.extend(["-f", f"endCursor={cursor}"])
        data = get_json(args)
        if not isinstance(data, dict):
            raise ValueError("Invalid linked projects response.")
        payload = data.get("data")
        repo_data = payload.get("repository") if isinstance(payload, dict) else None
        if not isinstance(repo_data, dict) or not isinstance(repo_data.get("projectsV2"), dict):
            raise ValueError("Could not retrieve linked projects.")
        connection = repo_data["projectsV2"]
        nodes = connection.get("nodes")
        page = connection.get("pageInfo")
        if not isinstance(nodes, list) or not isinstance(page, dict) or type(page.get("hasNextPage")) is not bool:
            raise ValueError("Invalid linked projects response.")
        for node in nodes:
            if not isinstance(node, dict) or type(node.get("closed")) is not bool:
                raise ValueError("Invalid linked project.")
            if not node["closed"]:
                projects.append(parse_project(node))
        if not page["hasNextPage"]:
            return projects
        cursor = page.get("endCursor")
        if not isinstance(cursor, str) or not cursor or cursor in seen_cursors:
            raise ValueError("Invalid linked projects pagination cursor.")
        seen_cursors.add(cursor)


def select_linked_project(projects: list[Project]) -> Project:
    labels = [f"#{project.number} - {project.title} ({project.url})" for project in projects]
    return projects[labels.index(choose_project(labels))]


def add_to_project(url: str, project: Project) -> None:
    issue = get_json(["issue", "view", url, "--json", "id"])
    if not isinstance(issue, dict) or not isinstance(issue.get("id"), str) or not issue["id"]:
        raise ValueError("Could not determine the issue ID.")
    response = get_json([
        "api", "graphql", "-f", f"query={ADD_ITEM_QUERY}",
        "-f", f"projectId={project.id}", "-f", f"contentId={issue['id']}",
    ])
    if not isinstance(response, dict):
        raise ValueError("GitHub did not confirm the project item.")
    data = response.get("data")
    mutation = data.get("addProjectV2ItemById") if isinstance(data, dict) else None
    item = mutation.get("item") if isinstance(mutation, dict) else None
    if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
        raise ValueError("GitHub did not confirm the project item.")
    print(f"Issue added to {project.url}")


def create_linked_branch(url: str) -> str:
    name = read_prompt("Branch name: ")
    if not name:
        raise ValueError("Branch name is required.")
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(["gh", "issue", "develop", url, "--name", name], cwd=directory, check=True)
    print(f"Linked remote branch: {name}")
    return name


def clone_branch(repository: str, branch: str) -> None:
    default = default_projects_directory()
    directory = Path(read_prompt(f"Clone directory [{default}]: ") or default).expanduser()
    folder = read_prompt(f"Clone folder name [{repository.split('/')[-1]}]: ") or repository.split("/")[-1]
    if folder in {".", ".."} or Path(folder).name != folder:
        raise ValueError("Clone folder name must be a single directory name.")
    target = directory / folder
    if os.path.lexists(target):
        raise ValueError(f"Clone destination already exists: {target}")
    directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(["gh", "repo", "clone", repository, str(target), "--", "--branch", branch], check=True)
    print(f"Repository cloned with branch {branch}: {target}")


def main() -> int:
    repository = os.environ.get("GH_REPO", "")
    if len(repository.split("/")) != 2 or not all(repository.split("/")):
        print("Error: a selected GitHub repository is required.", file=sys.stderr)
        return 1
    url = None
    try:
        url = create_issue(repository)
        if read_prompt("Add this issue to a linked project? [y/N]: ").lower() == "y":
            projects = linked_projects(repository)
            if projects:
                add_to_project(url, select_linked_project(projects))
            else:
                print("No open projects are linked to this repository.")
        if read_prompt("Create a linked remote branch? [y/N]: ").lower() == "y":
            branch = create_linked_branch(url)
            if read_prompt("Clone the repository and check out this branch? [y/N]: ").lower() == "y":
                clone_branch(repository, branch)
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled." + (f" Issue already created: {url}" if url else ""), file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, termios.error) as error:
        print(f"Error: {error}", file=sys.stderr)
        if url:
            print(f"Issue already created: {url}. Check GitHub and any clone before retrying.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
