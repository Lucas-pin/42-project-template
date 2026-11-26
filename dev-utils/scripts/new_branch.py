import subprocess
import sys

from select_repository import read_prompt


def main() -> int:
    try:
        branch = read_prompt("Branch name: ", preserve_whitespace=True)
        if not branch.strip():
            raise ValueError("Branch name is required.")
        subprocess.run(["git", "switch", "-c", branch], check=True)
        print(f"Switched to branch {branch}")
    except (EOFError, KeyboardInterrupt):
        print("\nCanceled.", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
