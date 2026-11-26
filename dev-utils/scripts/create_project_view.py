import json
import os
import select
import subprocess
import sys
import termios
import tty
import unicodedata
from dataclasses import dataclass

from select_repository import choose, read_prompt


@dataclass(frozen=True)
class Project:
    id: str
    number: int
    title: str
    url: str


def parse_project(data: object) -> Project:
    if not isinstance(data, dict):
        raise ValueError("Invalid project response from GitHub CLI.")
    project_id = data.get("id")
    number = data.get("number")
    title = data.get("title")
    url = data.get("url")
    if not (
        isinstance(project_id, str) and project_id
        and type(number) is int and number > 0
        and isinstance(title, str) and title
        and isinstance(url, str) and url.startswith(("https://", "http://"))
    ):
        raise ValueError("Incomplete project response from GitHub CLI.")
    return Project(project_id, number, title, url)


def get_json(args: list[str]) -> object:
    result = subprocess.run(
        ["gh", *args], check=True, text=True, stdout=subprocess.PIPE
    )
    return json.loads(result.stdout)


def choose_project(options: list[str]) -> str:
    if not (sys.stdin.isatty() and sys.stdout.isatty()) or os.environ.get("TERM", "") in {"", "dumb"}:
        print("Select a menu position, not the GitHub project number.")
        return choose(options, "Menu position: ")

    def fit_line(text: str, width: int) -> str:
        result = []
        used = 0
        for char in text:
            if unicodedata.category(char).startswith("C"):
                continue
            char_width = 0 if unicodedata.combining(char) else 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
            if used + char_width > width:
                break
            result.append(char)
            used += char_width
        return "".join(result)

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)
    selected = 0
    top = 0
    previous_lines = 0
    try:
        tty.setcbreak(fd)
        while True:
            size = os.get_terminal_size(sys.stdout.fileno())
            if size.lines < 4 or size.columns < 4:
                raise ValueError("Terminal is too small for the project selector.")
            visible = min(len(options), size.lines - 3)
            top = max(0, min(top, selected, len(options) - visible))
            if selected >= top + visible:
                top = selected - visible + 1
            lines = [f"Select a project (Up/Down, Enter; q to cancel) [{selected + 1}/{len(options)}]:"]
            lines.extend(
                ("> " if index == selected else "  ") + options[index]
                for index in range(top, min(top + visible, len(options)))
            )
            if previous_lines:
                sys.stdout.write(f"\x1b[{previous_lines}A")
            for line in lines:
                sys.stdout.write("\r\x1b[2K" + fit_line(line, size.columns - 1) + "\n")
            for _ in range(previous_lines - len(lines)):
                sys.stdout.write("\r\x1b[2K\n")
            previous_lines = max(previous_lines, len(lines))
            sys.stdout.flush()

            key = os.read(fd, 1)
            if not key:
                raise EOFError
            if key == b"\x1b":
                sequence = b""
                for _ in range(2):
                    if not select.select([fd], [], [], 0.2)[0]:
                        break
                    sequence += os.read(fd, 1)
                if sequence in (b"[A", b"OA"):
                    selected = max(0, selected - 1)
                elif sequence in (b"[B", b"OB"):
                    selected = min(len(options) - 1, selected + 1)
                elif not sequence:
                    raise KeyboardInterrupt
            elif key in (b"\n", b"\r"):
                break
            elif key == b"q":
                raise KeyboardInterrupt
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    print(f"Selected project: {options[selected]}")
    return options[selected]


def select_project(owner: str) -> Project:
    data = get_json(["project", "list", "--owner", owner, "--limit", "1000", "--format", "json"])
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError("Invalid project list from GitHub CLI.")
    projects = [parse_project(project) for project in data["projects"]]
    labels = [f"#{project.number} - {project.title}" for project in projects]
    manual = "Enter a project number manually"
    selected = choose_project([*labels, manual])
    if selected != manual:
        return projects[labels.index(selected)]
    number = read_prompt("Project number: ")
    if not number.isascii() or not number.isdecimal() or int(number) < 1:
        raise ValueError("Project number must be a positive integer.")
    return parse_project(get_json([
        "project", "view", number, "--owner", owner, "--format", "json"
    ]))


def main() -> int:
    try:
        owner = read_prompt("Project owner (user or organization) [@me]: ") or "@me"
        project = select_project(owner)
        name = read_prompt("View name: ")
        if not name:
            raise ValueError("View name is required.")
        layouts = {"board": "BOARD_LAYOUT", "table": "TABLE_LAYOUT", "roadmap": "ROADMAP_LAYOUT"}
        while True:
            layout = (read_prompt("View layout (board/table/roadmap) [board]: ") or "board").lower()
            if layout in layouts:
                break
            print("Choose board, table, or roadmap.")

        print(f"Project: {project.title} (#{project.number}) - {project.url}")
        print(f"New view: {name} ({layout})")
        if read_prompt("Create this view? [y/N]: ").lower() != "y":
            print("Canceled.")
            return 0

        try:
            data = get_json([
                "api", "graphql",
                "-f", "query=mutation($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) { "
                "createProjectV2View(input: {projectId: $projectId, name: $name, layout: $layout}) "
                "{ projectV2View { id name layout project { id } } } }",
                "-f", f"projectId={project.id}",
                "-f", f"name={name}",
                "-f", f"layout={layouts[layout]}",
                "--jq", ".data.createProjectV2View.projectV2View",
            ])
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            print(f"Could not confirm view creation. Check {project.url} before retrying.", file=sys.stderr)
            return 1
        if (
            not isinstance(data, dict)
            or not data.get("id")
            or data.get("name") != name
            or data.get("layout") != layouts[layout]
            or not isinstance(data.get("project"), dict)
            or data["project"].get("id") != project.id
        ):
            raise ValueError(f"GitHub did not confirm the view. Check {project.url} before retrying.")
        print(f"View created in {project.url}")
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled.", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.CalledProcessError, termios.error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
