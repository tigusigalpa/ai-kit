# Python: scripts and packages

Apply this profile only when Python is actually present in the project. First read `PROJECT_CONTEXT.md`, then check existing scripts, the supported Python version, startup method, `pyproject.toml` or `requirements*.txt`, the lockfile, and test commands. Follow the current project style; add packaging, frameworks, or dependencies only when a simple script needs them.

## Implementation

- Separate I/O from core logic. For an executable script, use `main()` and `if __name__ == "__main__":`; importing a module must not unexpectedly run its work.
- Use `argparse` or the project's existing tool for command-line arguments. Document required parameters, output format, and exit codes.
- Use `pathlib.Path`, context managers, and explicit text encoding. Do not rely on the current working directory without an agreed contract. Stream large files where appropriate.
- Make file changes predictable: validate paths and input; provide a safe preview mode or explicit confirmation for bulk or destructive actions. Avoid unnecessary overwrites of user data.
- Add type annotations to public functions and complex boundaries, choose clear names, catch only expected exceptions, and preserve the original error cause. Error messages should help correct input or environment problems.
- Use the standard library when it adequately solves the task. Keep formatting changes scoped; follow the configured formatter/linter and established style.

## Dependencies and security

- Run the project in an isolated environment; record dependencies using the repository's chosen method. Use `pyproject.toml` for a new package; standalone scripts may use the existing dependency format. Keep manifests and lockfiles versioned by default.
- Do not use `eval` or unsafe deserialization of untrusted input. Prefer argument lists without a shell for external commands; do not interpolate untrusted strings into commands. Use parameterized SQL and network request timeouts.
- Keep secrets out of code and logs, and real data out of test fixtures. Check input boundaries and access permissions before writing or deleting files.

## Verification

- Test nontrivial logic and dangerous paths: success, invalid input, boundary cases, and reruns where idempotency matters. Use `pytest` or `unittest` according to project conventions; prefer temporary directories and substituted external services over real network requests.
- Run targeted tests and the project's configured formatting, lint, and type checks. If a command is unavailable, record that in the result; do not claim it passed.
- Follow the shared cycle and review rules in [ENGINEERING.md](../ENGINEERING.md). When startup, dependencies, or behavior change, update README/context and the decision log in proportion to the change's significance.
