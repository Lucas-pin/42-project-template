import subprocess
import sys


LABELS = (
    ("bug", "d73a4a", "Incorrect behavior"),
    ("enhancement", "a2eeef", "New feature or improvement"),
    ("documentation", "0075ca", "Documentation changes"),
    ("testing", "c5def5", "Tests or quality checks"),
    ("refactor", "fbca04", "Internal code improvement"),
)


def main() -> int:
    try:
        subprocess.run(["gh", "repo", "view"], stdout=subprocess.DEVNULL, check=True)
        result = subprocess.run(
            [
                "gh",
                "api",
                "repos/{owner}/{repo}/labels?per_page=100",
                "--paginate",
                "--jq",
                ".[].name",
            ],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        existing_labels = set(result.stdout.splitlines())
        for name, color, description in LABELS:
            if name in existing_labels:
                print(f"Label already exists: {name}", flush=True)
            else:
                subprocess.run(
                    [
                        "gh",
                        "label",
                        "create",
                        name,
                        "--color",
                        color,
                        "--description",
                        description,
                    ],
                    check=True,
                )
    except FileNotFoundError:
        print("gh is missing; run 'make setup-gh'.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"GitHub CLI command failed with exit code {error.returncode}.", file=sys.stderr)
        return error.returncode if error.returncode > 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
