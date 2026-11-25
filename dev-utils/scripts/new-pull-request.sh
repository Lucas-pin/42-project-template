#!/usr/bin/env bash
set -euo pipefail

repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)" ||
    { echo "Run this command from a GitHub repository." >&2; exit 1; }

default_base="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)"
read -r -p "Base branch [$default_base]: " base
base="${base:-$default_base}"

read -r -p "Create pull request draft? [y/N]: " draft
args=(--base "$base" --template "PULL_REQUEST_TEMPLATE.md")
if [[ "$draft" =~ ^[yY]$ ]]; then
    args+=(--draft)
fi

echo "Creating pull request in $repo..."
gh pr create "${args[@]}"
