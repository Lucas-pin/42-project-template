import subprocess
import sys

from select_repository import read_prompt


TEMPLATE = "Lucas-pin/42-project-template"


def create_repository(name: str, visibility: str, description: str) -> str:
    args = ["gh", "repo", "create", name, f"--{visibility}", "--template", TEMPLATE]
    if description:
        args.extend(["--description", description])
    print(f"Creating {name} from {TEMPLATE}...", flush=True)
    result = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE)
    url = result.stdout.strip()
    if not url:
        raise ValueError("GitHub CLI did not return a repository URL; check GitHub before retrying.")
    print(url)
    return url


def main() -> int:
    url = None
    try:
        name = read_prompt("Repository name: ", preserve_whitespace=True)
        if not name.strip():
            raise ValueError("Repository name is required.")
        visibility = read_prompt("Visibility (public/private) [public]: ", preserve_whitespace=True) or "public"
        if visibility not in {"public", "private"}:
            raise ValueError("Visibility must be public or private.")
        description = read_prompt("Description: ", preserve_whitespace=True)
        url = create_repository(name, visibility, description)
        if read_prompt("Clone the new repository now? [Y/n]: ", preserve_whitespace=True).lower() != "n":
            subprocess.run(["gh", "repo", "clone", url.removeprefix("https://github.com/")], check=True)
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled." + (f" Repository already created: {url}" if url else ""), file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        if url:
            print(f"Repository already created: {url}. Check the clone before retrying.", file=sys.stderr)
        elif isinstance(error, subprocess.CalledProcessError):
            print("Repository creation may have failed after creating it; check GitHub before retrying.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
