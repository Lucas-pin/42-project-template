#!/usr/bin/env bash
set -euo pipefail

read -r -p "Branch name: " branch_name
[[ -n "${branch_name//[[:space:]]/}" ]] || { echo "Branch name is required." >&2; exit 1; }

git switch -c "$branch_name"
echo "Switched to branch $branch_name"
