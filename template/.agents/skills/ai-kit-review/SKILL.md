---
name: ai-kit-review
description: "Run only when the user explicitly asks for an AI-KIT review of current changes or of a named diff, commit range, or path."
---

# AI-KIT review

1. Use the scope the user named; otherwise review staged and unstaged changes against HEAD plus untracked files. Read ../../../PROJECT_CONTEXT.md and the profiles of affected modules.
2. Apply the [engineering review rules](../../../ai-kit/ENGINEERING.md#review) and, for auth, data, input, or dependency boundaries, the [security baseline](../../../ai-kit/SECURITY.md).
3. Run the targeted checks recorded for affected modules when available; report unavailable checks as unverified.
4. Report findings by severity with file and line, the concrete failure scenario, and a suggested fix; say so explicitly when nothing material was found. Edit files only when the user asks; Core governs commits.
