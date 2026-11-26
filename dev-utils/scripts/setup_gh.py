import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tarfile
import tempfile
from urllib.request import Request, urlopen


RELEASE_URL = "https://api.github.com/repos/cli/cli/releases/latest"


def architecture() -> str:
    if platform.system() != "Linux":
        raise ValueError("GitHub CLI installation is supported only on Linux.")
    machine = platform.machine()
    architectures = {"x86_64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    if machine not in architectures:
        raise ValueError(f"Unsupported architecture: {machine}")
    return architectures[machine]


def latest_version() -> str:
    request = Request(RELEASE_URL, headers={"User-Agent": "42-project-template", "Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=30) as response:
        release = json.load(response)
    tag = release.get("tag_name") if isinstance(release, dict) else None
    if not isinstance(tag, str) or not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag):
        raise ValueError("Could not determine the latest GitHub CLI version.")
    return tag[1:]


def download_archive(version: str, arch: str, destination: Path) -> str:
    name = f"gh_{version}_linux_{arch}"
    url = f"https://github.com/cli/cli/releases/download/v{version}/{name}.tar.gz"
    request = Request(url, headers={"User-Agent": "42-project-template"})
    with urlopen(request, timeout=60) as response, destination.open("wb") as archive:
        shutil.copyfileobj(response, archive)
    return name


def install_binary(archive_path: Path, archive_name: str, install_dir: Path) -> Path:
    temp_path = None
    target = install_dir / "gh"
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            member = archive.getmember(f"{archive_name}/bin/gh")
            if not member.isfile():
                raise ValueError("The GitHub CLI archive does not contain a regular gh binary.")
            binary = archive.extractfile(member)
            if binary is None:
                raise ValueError("Could not read the GitHub CLI binary from the archive.")
            install_dir.mkdir(parents=True, exist_ok=True)
            with binary, tempfile.NamedTemporaryFile(dir=install_dir, delete=False) as temporary:
                temp_path = Path(temporary.name)
                shutil.copyfileobj(binary, temporary)
                temporary.flush()
                os.fchmod(temporary.fileno(), 0o755)
        os.replace(temp_path, target)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return target


def main() -> int:
    try:
        arch = architecture()
        version = latest_version()
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "gh.tar.gz"
            name = download_archive(version, arch, archive)
            target = install_binary(archive, name, Path.home() / ".local" / "bin")
        print(f"GitHub CLI {version} installed in {target}")
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
