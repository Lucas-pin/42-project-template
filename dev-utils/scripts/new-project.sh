#!/usr/bin/env bash
set -euo pipefail

read -r -p "Project title: " title
[[ -n "${title//[[:space:]]/}" ]] || { echo "Project title is required." >&2; exit 1; }

owner="$(env -u GH_TOKEN gh api user --jq .login)"
project_url="$(env -u GH_TOKEN gh project create --owner "$owner" --title "$title" --format json --jq '.url')"
echo "Project created: $project_url"

read -r -p "Link this project to the current repository? [Y/n]: " link_project
if [[ ! "$link_project" =~ ^[nN]$ ]]; then
    repo="$(env -u GH_TOKEN gh repo view --json nameWithOwner --jq .nameWithOwner)"
    project_number="$(env -u GH_TOKEN gh project list --owner "$owner" --format json --jq ".projects[] | select(.title == \"$title\") | .number")"
    if [[ -n "$project_number" ]]; then
        env -u GH_TOKEN gh project link "$project_number" --owner "$owner" --repo "$repo"
        echo "Project linked to $repo"
    else
        echo "Could not determine the project number." >&2
    fi
fi
