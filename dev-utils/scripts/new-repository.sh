#!/usr/bin/env bash
set -euo pipefail

read -r -p "Repository name: " repo_name
[[ -n "${repo_name//[[:space:]]/}" ]] || { echo "Repository name is required." >&2; exit 1; }

read -r -p "Visibility (public/private) [public]: " visibility
visibility="${visibility:-public}"
[[ "$visibility" == "public" || "$visibility" == "private" ]] || { echo "Visibility must be public or private." >&2; exit 1; }

read -r -p "Description: " description

args=("$repo_name" "--$visibility" --template "Lucas-pin/42-project-template")
[[ -n "$description" ]] && args+=("--description" "$description")

echo "Creating $repo_name from Lucas-pin/42-project-template..."
repo_url="$(env -u GH_TOKEN gh repo create "${args[@]}")"
echo "$repo_url"

read -r -p "Clone the new repository now? [Y/n]: " clone_repo
if [[ ! "$clone_repo" =~ ^[nN]$ ]]; then
    env -u GH_TOKEN gh repo clone "${repo_url#https://github.com/}"
fi
