#!/usr/bin/env bash
set -euo pipefail

repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner)" ||
    { echo "Run this command from a GitHub repository." >&2; exit 1; }

read -r -p "Issue title: " title
[[ -n "${title//[[:space:]]/}" ]] || { echo "Issue title is required." >&2; exit 1; }

labels_raw="$(gh label list --limit 200 --json name --jq '.[].name')"
if [[ -n "$labels_raw" ]]; then
    mapfile -t labels <<<"$labels_raw"
    PS3="Label: "
    select label in "No label" "${labels[@]}"; do
        [[ -n "$label" ]] && break
    done
else
    label="No label"
fi

body_file="$(mktemp --suffix=.md)"
trap 'rm -f "$body_file"' EXIT
cat >"$body_file" <<'EOF'
## Scope

## Acceptance criteria

- [ ] 

## Notes
EOF

editor="${VISUAL:-${EDITOR:-nano}}"
read -r -a editor_cmd <<<"$editor"
"${editor_cmd[@]}" "$body_file"

args=(--title "$title" --body-file "$body_file")
[[ "$label" != "No label" ]] && args+=(--label "$label")

read -r -p "Create issue in $repo? [y/N]: " confirm
if [[ "$confirm" =~ ^[yY]$ ]]; then
    gh issue create "${args[@]}"
else
    echo "Issue canceled."
fi
