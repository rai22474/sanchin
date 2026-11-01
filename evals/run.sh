#!/usr/bin/env bash
# Run sanchin's eval suite. Arguments go to `claude plugin eval`, e.g.:
#   evals/run.sh --scaffold --allow-tools Bash Write Edit
#   evals/run.sh --scaffold --case 'developer-*' --runs 1
#
# Why a wrapper: sanchin depends on mattpocock-skills@claude-plugins-official,
# and the eval sandbox has no marketplaces, so a dependency can't resolve and
# Claude Code silently doesn't load sanchin — every case would measure Claude
# without the plugin. (A case's `plugins:` can't help: a plugin loaded from a
# path is `@inline`, which doesn't satisfy the dependency, and the list
# replaces the plugin under test.) So the suite runs against a copy of the
# working tree with `dependencies` removed. The grilling skill, which every
# grill must invoke, is copied in from the installed dependency as
# `sanchin:grilling`, and the copy's references point to it; the generic code
# review runs without its skill here.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
for tool in claude git jq tar; do
  command -v "$tool" >/dev/null 2>&1 || { echo "evals/run.sh: $tool is required" >&2; exit 2; }
done

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# The working tree as it is, uncommitted changes included, without ignored files.
(cd "$root" && git ls-files -z --cached --others --exclude-standard | tar --null -T - -cf -) | tar -xf - -C "$work"
jq 'del(.dependencies)' "$root/.claude-plugin/plugin.json" > "$work/.claude-plugin/plugin.json"

grilling=$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/*/mattpocock-skills/*/skills/productivity/grilling 2>/dev/null | sort -V | tail -1)
if [ -n "$grilling" ]; then
  mkdir -p "$work/skills/grilling" && cp -R "$grilling"/. "$work/skills/grilling/"
  grep -rl 'mattpocock-skills:grilling' "$work/skills" "$work/docs" | xargs -r sed -i 's/mattpocock-skills:grilling/sanchin:grilling/g'
else
  echo "evals/run.sh: mattpocock-skills isn't installed; grill cases will fail (install it in Claude Code)" >&2
fi

# The default judge (haiku) misreads multi-part criteria — it failed reviews
# that met every one — so the llm graders get a stronger judge unless the
# caller picks one.
judge=(--judge-model sonnet)
for argument in "$@"; do
  [[ "$argument" == --judge-model* ]] && judge=()
done

results="$root/evals/results/$(date -u +%Y-%m-%dT%H-%M-%SZ)"
mkdir -p "$results"
status=0
claude plugin eval "$work" --output-dir "$results" --report "$results/report.html" "${judge[@]}" "$@" || status=$?
echo "evals/run.sh: results in $results" >&2
exit "$status"
