# Windows CI temporary-path regression

Date: 2026-10-08. Bundle: 0.2.2. Scope: reference test fixtures.

## Published evidence

The supplied Windows/Python 3.13.15 log executed 45 tests and reported two failures:

- Junction setup compared a path containing RUNNER~1 with a resolved parent containing runneradmin. The lexical containment check raised ValueError before creating the junction.
- Rollback fault injection compared an unresolved fixture path with the installer's resolved destination. The equality condition did not match, so the intended OSError was never injected.

Published main was read at 5b487824e3c6f5ab697981f4f3b19f59f5d16af4. Its tests/test_install.py matched the local pre-fix source after normalizing line endings.
GitHub's [run 37819777582](https://github.com/tigusigalpa/ai-kit/actions/runs/37819777582) reported failure for Windows/Python 3.10 and 3.13, and success for Ubuntu/Python 3.10 and 3.13. The supplied Python 3.13.15 traceback and the separately read Windows/Python 3.10.11 job log show the same two failure signatures.
No releases or tag refs were returned at this source check. The user has published the v0.2.2 source; this additional fixture fix remains local.

## Correction

The fixture now resolves the temporary root before deriving target/source paths:

~~~python
self.base = Path(self.temp.name).resolve()
~~~

The installer already resolves its target. Matching the fixture's path representation restores the intended containment checks and fault injection.
Installer code, linked-path refusal, rollback logic, test assertions, and workflow gates were preserved. VERSION remains 0.2.2 while this release is being prepared.

Two regression variants execute the existing rollback and junction scenarios under a real noncanonical temporary path. A sibling route with '..' gives the same directory a different lexical prefix without depending on NTFS short-name configuration. Cleanup is bound to the original TemporaryDirectory objects, never to the alias route.
Before the correction, an independent reproduction produced the same ValueError and missing-OSError assertion signatures. After correction, rollback succeeds and junction setup reaches the actual host permission check.

## Verification

- Full local suite on Windows/Python 3.12.14: 47 tests, 44 passed, 3 skipped. Both rollback scenarios passed. The skips were symlink creation and the original/noncanonical junction variants due to host permissions.
- Kit validation returned no errors/warnings, including Git visibility. Source inventory, ZIP bytes/integrity, and Python 3.10 syntax were verified for the repackaged bundle.
- The independent reproduction now passes the rollback check and reaches the unavailable junction creation check. These equivalent-path scenarios exercise the path-spelling contract without claiming a successful local Windows 8.3 alias or actual junction trial.

The [implementation record](IMPLEMENTATION.md#windows-ci-fixture-verification) indexes these results.
Local junction creation remains unavailable in the sandbox; that check is reported as skipped, not passed. Successful hosted execution of the corrected Windows jobs requires publishing the fix and rerunning CI.

No commit, push, tag, release, or remote repository write was performed.
