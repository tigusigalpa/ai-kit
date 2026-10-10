# AI-KIT session-start context. A client session-start hook runs this file and adds its
# output to the new session: the session instructions, current project facts, and
# repository state, so the first task needs no extra file reads.
# The installed hook pipes this file through tr before sh, so CRLF checkouts still run.
root="${CLAUDE_PROJECT_DIR:-.}"
limit=8000
cat "$root/.agents/hooks/session-start.md" 2>/dev/null
context="$root/PROJECT_CONTEXT.md"
if [ -f "$context" ]; then
  size=$(wc -c < "$context" | tr -d ' ')
  printf '\n--- PROJECT_CONTEXT.md ---\n\n'
  head -c "$limit" "$context"
  if [ "$size" -gt "$limit" ]; then
    printf '\n\n[Truncated at %s of %s bytes; read PROJECT_CONTEXT.md for the rest.]\n' "$limit" "$size"
  fi
fi
if git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf '\n--- Repository state ---\n\n'
  git -C "$root" status --short --branch 2>/dev/null | head -n 40
fi
exit 0
