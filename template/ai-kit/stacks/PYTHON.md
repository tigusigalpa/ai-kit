# Python scripts and packages

Confirm supported Python version, entry points, pyproject/requirements/lock, and configured checks.
- Separate I/O from core logic. Executables use main() and a __main__ guard; importing must not run the script's work.
- Use argparse or the existing CLI library; document arguments, output, errors, and exit codes.
- Use pathlib, explicit encodings, context managers, and streams for large inputs. Validate resolved paths before bulk changes; preview destructive operations.
- Use subprocess argument lists without a shell; never interpolate untrusted input into commands, eval, or unsafe deserialization.
- Annotate public/complex boundaries, catch expected exceptions, and preserve causes. Bound network timeouts.
- Use an isolated environment and versioned manifests/locks. New packages may prefer uv, ruff, and a chosen mypy/pyright baseline; standalone standard-library scripts need no packaging framework.
- Test success, invalid/boundary input, reruns, and file preservation with temporary directories and substituted external services.
- Run configured tests/format/lint/type checks; audit trusted dependencies where applicable. Keep real data/secrets out of fixtures and reports.
