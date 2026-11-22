#!/usr/bin/env bash
set -euo pipefail

read -r -p "Repository name: " repo_name
[[ -n "${repo_name//[[:space:]]/}" ]] || { echo "Repository name is required." >&2; exit 1; }

read -r -p "Visibility (public/private) [public]: " visibility
visibility="${visibility:-public}"
[[ "$visibility" == "public" || "$visibility" == "private" ]] || { echo "Visibility must be public or private." >&2; exit 1; }

read -r -p "Description: " description

args=("$repo_name" "--$visibility")
[[ -n "$description" ]] && args+=("--description" "$description")

read -r -p "Initialize with a README? [Y/n]: " add_readme
if [[ ! "$add_readme" =~ ^[nN]$ ]]; then
    args+=("--add-readme")
fi

echo "Creating $repo_name..."
env -u GH_TOKEN gh repo create "${args[@]}"
echo "Creating with template sources: https://github.com/$(env -u GH_TOKEN gh api user --jq .login)/$repo_name"

read -r -p "Clone the new repository now? [Y/n]: " clone_repo
if [[ ! "$clone_repo" =~ ^[nN]$ ]]; then
    owner="$(env -u GH_TOKEN gh api user --jq .login)"
    env -u GH_TOKEN gh repo clone "$owner/$repo_name"
fi
