#!/usr/bin/env bash
set -euo pipefail

gh repo view >/dev/null 2>&1 || { echo "Run this command from a GitHub repository." >&2; exit 1; }

create_label() {
    local name="$1"
    local color="$2"
    local description="$3"
    if gh label list --json name --jq '.[].name' | grep -Fxq "$name"; then
        echo "Label already exists: $name"
    else
        gh label create "$name" --color "$color" --description "$description"
    fi
}

create_label "bug" "d73a4a" "Incorrect behavior"
create_label "enhancement" "a2eeef" "New feature or improvement"
create_label "documentation" "0075ca" "Documentation changes"
create_label "testing" "c5def5" "Tests or quality checks"
create_label "refactor" "fbca04" "Internal code improvement"
