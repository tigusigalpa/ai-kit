# Manus audit disposition

Review date: 2026-10-08. Working patch: [VERSION](../VERSION), prepared locally.
The supplied Manus audit targets published main at 73707036c1098d8c1c81ab2c51d723c3d521f6b8 (v0.2). It does not evaluate the local v0.2.1 overlay fix or the expanded README.

## Evidence and scope

- The published snapshot was previously rebuilt from all 91 tracked blobs with matching Git object hashes. Its checker reproduced the five missing-heading errors and the oversized MODELS warning.
- GitHub's API reported [run 37810446904](https://github.com/tigusigalpa/ai-kit/actions/runs/37810446904) as completed/failure for that SHA. No successful hosted run of this patch has been established.
- Separate temporary-project reproductions against local v0.2.1 confirmed edited-candidate overwrite, retained Claude files losing their baseline records, and an unsupported/mixed-type state causing an uncaught TypeError.
- The audit's reported 31-passed/2-failed suite is reviewer evidence; it is not presented as our independently executed old-version suite.

## Decisions

| Finding | Disposition |
| --- | --- |
| P0: stale root anchors and failed CI | Already corrected locally in v0.2.1 with compact compatibility pointers. Published main still needs the patch and successful hosted validation. |
| P1: edited candidates overwritten | Fixed in v0.2.2: candidates use the incoming file's SHA-256 directory; exclusive creation preserves every existing file. Preview exposes paths and hashes; metadata records the first observation. |
| P1: agent changes orphan adapters | Fixed with a review conflict when tracked unselected adapters remain. Accepted files/state stay unchanged; exact paths are reported. Custom/untracked entries produce warnings. No automatic deletion or add/remove CLI redesign. |
| P2: invalid installer state/types | Fixed with schema/type/hash/path checks before planning. Unknown schema or corrupt input produces a controlled refusal, without blanket exception suppression. |
| P2: two active policy layers | Already corrected locally: old reference paths are pointers, canonical application policies are in template/. Old source history remains distinguishable from active policy. |
| P2: permanent verification claims | Results below and in IMPLEMENTATION are dated bundle snapshots. Source-read revisions, local patch versions, and hosted results remain separate. |
| P3: integration coverage | Added an existing mixed Go/Composer/Python fixture with local AGENTS/README/ignore rules and real installed Git private/team checks; retained upgrade/backup/rollback scenarios and added previous-version state coverage. |
| P3: Windows linked paths | Added a Windows junction fixture and detection using lstat reparse tags available on Python 3.10. Real junction execution remains dependent on host permissions. |
| P3: obtaining the kit | README includes clone/open instructions and requires a reviewed revision. It does not advertise a nonexistent release tag. |

Candidate metadata is not a live ledger: its local hash and timestamp describe first creation. Later preview reports current local hashes and edited-draft mismatches. A source-file hash is not an upstream Git SHA, and storing a candidate does not accept an installation.

Adapter retirement is deliberately manual in this patch. Retaining the old agent selection is the immediate way to keep its files managed. After reviewing and preserving local work, retire only the listed managed files and rerun preview; custom skills/settings require separate review.

## Public metadata and deferred work

The repository API confirmed main as default branch, an English description, MIT, empty topics/homepage, no releases, and no matching tag refs at review time. The audit's Community Profile percentage and master/docs documentation URL were not independently verified; an empty repository homepage is not proof of that separate URL claim.

Publication requires a separate explicit request. Before a first release: publish the reviewed patch, obtain a successful full hosted matrix, then choose a tag matching VERSION and prepare release notes/checksums. Do not publish the audit's proposed old v0.2.0 tag as if it contained these fixes.
Topics and any documentation URL can be reviewed then. A Code of Conduct requires an owner-selected policy/contact; issue/PR forms and release automation are useful later, but do not resolve the reproduced installer failures.

Full add/remove/replace adapter commands are deferred until their safe deletion and custom-file ownership contracts are designed. The blocking retirement conflict supplies the audit's minimum safe behavior now.

## Verification

The final local checks and execution limits are recorded in [the implementation record](IMPLEMENTATION.md#manus-patch-verification).
The mixed-project fixtures use synthetic manifests/locks; they do not run Laravel, Composer, Go builds, or Python dependency installation and are not real application trials.
Docker tests remain simulated read-only checks. Native instruction activation, live model switching, real Docker cleanup, and hosted success are not inferred from these tests.

No commit, push, tag, release, or remote settings write was performed.
