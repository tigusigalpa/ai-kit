# Bounded Python setup retries

## Scope

The repository's [CI](../.github/workflows/check-kit.yml) and [release workflow](../.github/workflows/publish-pypi.yml) use the local [setup action](../.github/actions/setup-python-retry/action.yml). It comes from the checked-out workflow commit; every external action remains pinned to a full SHA. Twine checks out the same source commit solely to load this local action, with checkout credentials disabled. Upload jobs still check out nothing, require the validated same-run artifact digests and retain the owner's protected-environment approval.

The existing validate/wheel OS/Python matrices and required check names stay unchanged. Python versions, architecture selection and setup-python's own cache/download behavior stay unchanged. There is no new external retry dependency, credential or write permission.

## Behavior and limits

- Try the existing pinned actions/setup-python once. If it succeeds, skip all waits/retries.
- After a failed setup, wait 20 seconds and try again. After a second failure, wait 40 seconds and make the third/final attempt.
- Only the first two setup attempts tolerate failure. The final setup failure fails its enclosing step/job; subsequent build/tests/upload cannot proceed as if Python had been installed.
- Waits and retries require the preceding attempt's `outcome == 'failure'` and `!cancelled()`. Cancellation never starts a new attempt. Caller steps have a 15-minute timeout covering the complete setup action.
- Only Python setup is retried. Tests, package builds, artifact checks and publications are not wrapped or replayed.
- The wrapper sees the action's success/failure outcome, not a structured HTTP status. Consequently **all setup failures**, including permanent configuration errors, receive this bounded retry policy; it is not a 504-only classifier. Unsupported versions or permissions still fail after the final attempt.
- Upstream already retries an archive request internally. These outer setup attempts are additional, not three total HTTP requests; an extended outage can still exhaust all attempts. Original failed-attempt logs/annotations remain visible after a later success.
- Pauses use PowerShell (`pwsh`), available on the selected GitHub-hosted Linux/Windows/macOS runners. This is an internal action for these workflows, not an installer option or a self-hosted-runner promise.

The standalone project-check template is unchanged: it is installed without this maintainer-only action and cannot reference it. App runtime, templates and the published v1.7.0 tag/artifacts are unchanged. This source change needs a later authorized commit/push before GitHub uses it; it creates no release or deployment approval.

## Distribution and image impact

The workflows ship inside the Python package/image for reference checks. Their local action must ship with them: archive validation requires it, and Docker's closed context explicitly includes that file. No application instruction or CLI operation changes. Rebuild/test the local development image for these packaging changes; never replace the published 1.7.0 image just to add an unreleased CI fix.

## Verification

Local verification on 2026-11-08:

- Windows/Python 3.12.14: **489 tests in 1747.892 seconds**, with 12 platform/environment skips and **one error**: `git init` exceeded its 30-second deadline while creating the temporary repository in a task test's setUp, before that test body ran. The unchanged case passed in isolation (one test in 2.378 seconds), then the whole task module passed again (24 tests in 56.058 seconds, one unavailable-symlink skip). The full Windows run is not represented as green. Packaged Linux/Python 3.13.16: **489 tests in 41.988 seconds**, successful with three skips (two Windows junction fixtures and an excluded local-maintainer entry check).
- Twenty-six targeted workflow-security/archive tests passed. Guards cover pinned dependencies, bounded attempts/delays, cancellation, final hard failure, output precedence, unchanged matrix/check names, read-only local-action loading, protected uploads and missing-action archive refusal.
- Checksum-verified actionlint 1.7.12 validated both workflows, including local action metadata; external shellcheck/pyflakes were disabled. Native PowerShell parsed both delay scripts without executing sleeps. Python 3.10 grammar passed for 62 files; native Python 3.10/macOS execution was not run in this task.
- Kit validation returned zero errors/warnings. Isolated sdist-to-wheel/resource/privacy checks, strict Twine and a fresh offline wheel CLI smoke passed. All **330 package files** match the reviewed LF source export, wheel and development image; the local action is present and root local maintainer files are absent.
- Docker smoke passed offline/read-only CLI checks, full optional-module installation, preservation/reruns, actual closed-context inclusion/privacy and SIGTERM with/without init. The retained development image is `sha256:1fdd3999925c2dac9a7ebb79f078068e445e38adb749bd62e8e48a356b62d2d2`; its revision label identifies the uncommitted worktree, not a released commit.
- The dedicated builder/cache (343.2 MB reported), container and state volume were retired. The published 1.7.0 image and unrelated workloads were retained. No host RAM/disk compaction or registry publication occurred.

Hosted execution of the modified action and an injected HTTP 504 recovery have **not** been run; local static guards do not establish native GitHub Actions retry behavior. Commit/push and publication were not performed. These verification-only notes and the changelog retain the tested wheel/image with their earlier documentation snapshot; workflow/action/checker bytes are unchanged after testing. Raw logs and build artifacts stay outside the source checkout.

## Primary references

Reviewed on 2026-11-08: pinned [setup-python inputs](https://github.com/actions/setup-python/blob/5fda3b95a4ea91299a34e894583c3862153e4b97/action.yml), [Python installer](https://github.com/actions/setup-python/blob/5fda3b95a4ea91299a34e894583c3862153e4b97/src/install-python.ts), GitHub [composite metadata](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax#runs-for-composite-actions) and [status expressions](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions#status-check-functions).
