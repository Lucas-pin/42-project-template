import subprocess
import sys
from dataclasses import dataclass

from project_layout import LAYOUTS, prompt_view_layout
from select_repository import read_prompt


@dataclass(frozen=True)
class CreatedProject:
    number: int
    url: str
    id: str


def gh_output(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args], check=True, text=True, stdout=subprocess.PIPE
    )
    return result.stdout.strip()


def selected_repository() -> tuple[str, str, str]:
    repo = gh_output("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("Could not determine the selected repository.")
    return repo, parts[0], parts[1]


def create_project(owner: str, title: str) -> CreatedProject:
    try:
        response = gh_output(
            "project", "create", "--owner", owner, "--title", title,
            "--format", "json", "--jq", ".number, .url, .id",
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f"Could not confirm project creation; it may already exist: {error}"
        ) from error
    fields = response.splitlines()
    if (
        len(fields) != 3 or not fields[0].isascii() or not fields[0].isdecimal()
        or int(fields[0]) < 1 or not fields[1].startswith(("https://", "http://"))
        or not fields[2] or fields[2] == "null"
    ):
        raise ValueError(
            "The project may have been created, but its number, URL or ID "
            f"was missing from the response: {response}"
        )
    return CreatedProject(int(fields[0]), fields[1], fields[2])


def link_project(project: CreatedProject, owner: str, repo_name: str) -> None:
    try:
        subprocess.run(
            ["gh", "project", "link", str(project.number), "--owner", owner, "--repo", repo_name],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f"Could not link {project.url}; the project was already created: {error}"
        ) from error


def first_view_id(project: CreatedProject) -> str:
    try:
        view_id = gh_output(
            "api", "graphql",
            "-f", "query=query($id: ID!) { node(id: $id) { ... on ProjectV2 { views(first: 1) { nodes { id } } } } }",
            "-f", f"id={project.id}", "--jq", ".data.node.views.nodes[0].id // empty",
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f"Could not retrieve the first view of {project.url}. "
            f"The project is already created and linked: {error}"
        ) from error
    if not view_id or view_id == "null":
        raise ValueError(f"No view found for {project.url}. The project is already created and linked.")
    return view_id


def set_view_layout(project: CreatedProject, view_id: str, layout: str) -> None:
    try:
        updated_layout = gh_output(
            "api", "graphql",
            "-f", "query=mutation($viewId: ID!, $layout: ProjectV2ViewLayout!) { "
            "updateProjectV2View(input: {viewId: $viewId, layout: $layout}) { projectV2View { layout } } }",
            "-f", f"viewId={view_id}", "-f", f"layout={LAYOUTS[layout]}",
            "--jq", ".data.updateProjectV2View.projectV2View.layout",
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError(
            f"Could not set the {layout} view for {project.url}. "
            f"The project is already created and linked: {error}"
        ) from error
    if updated_layout != LAYOUTS[layout]:
        raise ValueError(
            f"GitHub did not confirm the {layout} view for {project.url}. "
            "The project is already created and linked."
        )


def main() -> int:
    try:
        repo, owner, repo_name = selected_repository()
        title = read_prompt("Project title: ", preserve_whitespace=True)
        if not title.strip():
            raise ValueError("Project title is required.")
        layout = prompt_view_layout()
        print(f"Creating a project for {repo} under {owner} with a {layout} view...", flush=True)
        project = create_project(owner, title)
        print(f"Project created: {project.url}", flush=True)
        link_project(project, owner, repo_name)
        print(f"Project linked to {repo}", flush=True)
        set_view_layout(project, first_view_id(project), layout)
        print(f"Project view set to {layout}.")
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled.", file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
