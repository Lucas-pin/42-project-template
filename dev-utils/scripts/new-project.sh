#!/usr/bin/env bash
set -euo pipefail

read -r -p "Project title: " title
[[ -n "${title//[[:space:]]/}" ]] || { echo "Project title is required." >&2; exit 1; }

default_owner="$(gh api user --jq .login)"
read -r -p "Project owner (user or organization) [$default_owner]: " owner
owner="${owner:-$default_owner}"
[[ "$owner" == "@me" ]] && owner="$default_owner"
[[ -n "${owner//[[:space:]]/}" ]] || { echo "Project owner is required." >&2; exit 1; }

project_data="$(gh project create --owner "$owner" --title "$title" --format json --jq '.number, .url')"
mapfile -t project_info <<<"$project_data"
project_number="${project_info[0]:-}"
project_url="${project_info[1]:-}"
if [[ ! "$project_number" =~ ^[1-9][0-9]*$ || ! "$project_url" =~ ^https?:// ]]; then
    echo "The project may have been created, but its number or URL was missing from the response: $project_data" >&2
    exit 1
fi
echo "Project created: $project_url"

read -r -p "Link this project to the current repository? [Y/n]: " link_project
if [[ ! "$link_project" =~ ^[nN]$ ]]; then
    repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
    repo_owner="${repo%%/*}"
    if [[ "${repo_owner,,}" != "${owner,,}" ]]; then
        echo "Cannot link $repo: gh project link requires the repository and project to have the same owner." >&2
        exit 1
    fi
    gh project link "$project_number" --owner "$owner" --repo "${repo#*/}"
    echo "Project linked to $repo"
fi
