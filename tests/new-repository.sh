#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cat >"$tmp_dir/gh" <<'EOF'
#!/usr/bin/env bash
printf '<%s>\n' "$@" >>"$GH_TEST_LOG"
if [[ "$1 $2" == "repo create" ]]; then
    [[ "${GH_TEST_FAIL_CREATE:-}" != "1" ]] || exit 1
    echo "https://github.com/example/project"
fi
EOF
chmod +x "$tmp_dir/gh"
export PATH="$tmp_dir:$PATH"
export GH_TEST_LOG="$tmp_dir/gh.log"

printf 'project\nprivate\nA description with spaces\nn\n' |
    bash "$root/dev-utils/scripts/new-repository.sh" >/dev/null
cat >"$tmp_dir/expected" <<'EOF'
<repo>
<create>
<project>
<--private>
<--template>
<Lucas-pin/42-project-template>
<--description>
<A description with spaces>
EOF
diff -u "$tmp_dir/expected" "$GH_TEST_LOG"

: >"$GH_TEST_LOG"
printf 'example/project\n\n\n\n' |
    bash "$root/dev-utils/scripts/new-repository.sh" >/dev/null
cat >"$tmp_dir/expected" <<'EOF'
<repo>
<create>
<example/project>
<--public>
<--template>
<Lucas-pin/42-project-template>
<repo>
<clone>
<example/project>
EOF
diff -u "$tmp_dir/expected" "$GH_TEST_LOG"

: >"$GH_TEST_LOG"
if printf 'project\n\n\ny\n' |
    GH_TEST_FAIL_CREATE=1 bash "$root/dev-utils/scripts/new-repository.sh" >/dev/null; then
    echo "Repository creation failure was not propagated." >&2
    exit 1
fi
if grep -Fxq '<clone>' "$GH_TEST_LOG"; then
    echo "Clone was attempted after repository creation failed." >&2
    exit 1
fi

echo "Repository creation tests passed."
