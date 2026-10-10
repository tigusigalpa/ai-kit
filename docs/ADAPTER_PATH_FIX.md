# Adapter file-parent compatibility

## Failure and cause

The supplied Linux/Python 3.13.16 CI log reports one error in `test_detected_clients_are_suggested_without_changing_selection`: probing `.clinerules/ai-kit.md` through an existing regular `.clinerules` file raises `NotADirectoryError` in `lstat`. Windows can report the child as missing instead, allowing the earlier local suite to pass and a selected Cline adapter to reach an invalid write plan.

## Corrected behavior

Link detection treats a non-directory ancestor as an absent child. Selected write paths separately require directory parents; the unselected-adapter warning probe skips only blocked file parents. Linked paths and permission failures still refuse installation. An existing `.clinerules` file remains detected and preserved; selecting the directory adapter refuses installation before any write. No automatic file-to-directory conversion is performed.

Explicit agent selections, private/team policies, registry paths, conflict handling, and upgrade baselines remain intact. Review covered absent and directory layouts, optional versus selected paths, links, permissions, and file preservation.

## Verification

2026-10-10, Windows/Python 3.12.14:

- Reproduced the supplied failure before the fix by simulating POSIX ENOTDIR in the original detection scenario. A real file-parent fixture also exposed the invalid selected-adapter plan on Windows.
- Seven focused checks passed after the fix. The complete suite then ran 133 tests: 129 passed, four skipped (one symlink, two junction variants, and the POSIX sh hook).
- Regressions cover nested detection markers, preserved file contents and agent suggestions, preview without writes, actual installation and rerun stability, selected-adapter refusal and CLI reporting, permission failures, and linked-parent refusal.
- Python 3.10 grammar validation passed for the changed installer and tests.
- Tests used a writable temporary root because the sandbox's default temporary directory denied fixture access.

Native Linux execution and corrected hosted CI remain unverified; WSL enumeration returned `Wsl/E_ACCESSDENIED`. Fixture checks do not establish native client activation or real application trials.
