#!/usr/bin/env bash
set -euo pipefail

install_dir="$HOME/.local/bin"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

case "$(uname -m)" in
    x86_64) gh_arch="amd64" ;;
    aarch64|arm64) gh_arch="arm64" ;;
    *) echo "Unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

version="$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest |
    sed -n 's/.*"tag_name": "v\([^"]*\)".*/\1/p' | head -n 1)"

[[ -n "$version" ]] || { echo "Could not determine the latest GitHub CLI version." >&2; exit 1; }

archive="gh_${version}_linux_${gh_arch}.tar.gz"
curl -fsSL -o "$tmp_dir/$archive" \
    "https://github.com/cli/cli/releases/download/v${version}/$archive"
tar -xzf "$tmp_dir/$archive" -C "$tmp_dir"
mkdir -p "$install_dir"
install -Dm755 "$tmp_dir/gh_${version}_linux_${gh_arch}/bin/gh" "$install_dir/gh"
echo "GitHub CLI $version installed in $install_dir/gh"
