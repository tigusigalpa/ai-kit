# AI-KIT CLI image

## Role and boundary

The [Dockerfile](../Dockerfile) packages AI-KIT's CLI as a one-shot Linux workload, including the optional bounded OpenRouter text executor. Live calls require explicit configuration and invocation; native clients and scanners are separate. [README](guide/DOCKER.md) covers usage; [CONTAINERS](../template/ai-kit/CONTAINERS.md) owns policy. [ADR 0013](adr/0013-docker-cli-image.md) records the initial design.

The wheel is installed at build time, including templates, pinned security resources, optional skills, docs and tests. Runtime uses no checkout mount or package installation. `/workspace` is an application bind mount, outside the reference distribution; `/tmp` is explicitly writable temporary storage. No Docker socket, host credentials, privileged mode or anonymous volume is required. Git supports project evidence/visibility checks; external framework tools and reviewed benchmark workers are outside this image.

Root AGENTS.md, PROJECT_CONTEXT.md and WIKI.md stay local and are excluded from wheel/context; template counterparts remain packaged. See [maintenance](../CONTRIBUTING.md#local-maintainer-files).

The entrypoint is exec-form `aikit`, default command `--help`, default UID/GID `10001:10001`, and stop signal SIGTERM. Callers use `--init`, a read-only root, dropped capabilities and no-new-privileges. Ordinary reports can disable networking and mount the project read-only. Installation requires an intentional writable project mount and `--apply`. Existing installer defaults, preservation and conflicts are unchanged. Mid-apply interruption is not an atomic rollback guarantee; inspect, run doctor and preview again.

## Build inputs

Verified 2026-10-14 against the [official Python image manifest](https://github.com/docker-library/official-images/blob/master/library/python), the Docker registry and PyPI release metadata:

| Input | Pin |
| --- | --- |
| Python base | `python:3.13.16-slim-bookworm` |
| Multiarchitecture image index | `sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641` |
| Observed linux/amd64 manifest | `sha256:f040863673aea2570c3ff6a5c3fb4c673a016cbc5375005ad145915922b6b78a` |
| Build-only setuptools | 84.0.0 |
| Build-only wheel | 0.48.0 |
| Build-only packaging | 26.3 |

[build-requirements.txt](../docker/build-requirements.txt) records exact wheel SHA-256 hashes; pip verifies them with `--require-hashes`. The builder produces a no-runtime-dependency wheel without isolated dependency resolution. Runtime installation uses `--no-index --no-deps`. Git and its Debian dependencies resolve at build time; the base/tool pins do not promise byte-identical rebuilds. A distributable release must record its own resulting immutable image identity. Registry publication requires explicit authorization and remote verification.

`AIKIT_VERSION` must match [VERSION](../VERSION); [the guard](../docker/check_version.py) refuses missing/mismatched labels before building. Tags remain mutable. Follow the [release checklist](../CONTRIBUTING.md#docker-hub-releases) to update the [Overview](DOCKER_HUB_OVERVIEW.md) for every image release. [v1.5.0](V1_5_0.md#docker-hub-publication) records the current image publication; the results below retain their original versions.

The [.dockerignore](../.dockerignore) is a closed allowlist with later sensitive/cache exclusions. Unknown root files are excluded. Included source directories still require review: a filename denylist cannot detect arbitrary credentials embedded in allowed source. Synthetic context tests verify actual Docker ignore behavior, including hidden source skill directories, without reading personal credentials. The `context-audit` scratch stage is a test export target, never the runtime image. Package-data and MANIFEST include image resources so the installed wheel can pass kit validation.

## Change impact and image refresh

Assess image impact on every maintenance task, including changes outside Dockerfile. Canonical policy: [image freshness](../template/ai-kit/CONTAINERS.md#image-freshness).

- Rebuild when CLI/scripts, installed templates/skills, ignore policies, integration resources, defaults or runtime dependencies change. Inspect Dockerfile COPY steps, `.dockerignore`, wheel package-data and MANIFEST: changing a source file is ineffective if packaging omits it. VERSION, build tools, base image, entrypoint and runtime-contract changes also require rebuilding and relevant checks.
- Descriptive README/maintainer edits or publication receipts may retain the prepared image when runtime behavior and installed guidance stay unchanged; record that its bundled documentation is an earlier snapshot. Changes only in a mounted application or private dialogue workspace do not update the kit distribution and normally need no kit rebuild.
- Build from final sources as `ai-kit:dev` in a clean LF checkout, passing the current VERSION through AIKIT_VERSION and the source commit through AIKIT_REVISION. Keep every published `tigusigalpa/ai-kit` tag and digest intact. Use normal cache invalidation; editing Dockerfile or disabling all cache is unnecessary for ordinary source changes.
- Run kit validation, affected behavior tests and `python tests/docker_smoke.py ai-kit:dev --context .`; compare the changed packaged resources with source. Follow the verification procedure below for scope, preflight and cleanup. Keep artifact binaries and per-run identity/results outside the source checkout. Record a reason when no rebuild is needed; report runtime checks that could not run.
- Local refresh does not refresh Docker Hub. Publish only under explicit authorization for the intended tag; an earlier one-time release push does not authorize future replacements. A requested release version must agree across VERSION, wheel and image label. Verify the remote digest/configuration after an authorized push.

## Verification procedure

1. Read the selected Docker context and both client/server versions; distinguish permissions from a stopped daemon. Build locally with the value from VERSION and record the tested architecture.
2. Run `python scripts/check_kit.py` and `python -m unittest discover -s tests -v` after packaging/checker changes. Keep wheel output in an isolated source copy so tests cannot copy locked build artifacts.
3. Build `docker build --build-arg AIKIT_VERSION=<value> --build-arg AIKIT_REVISION=<commit> --tag ai-kit:<value> .` from a clean LF export of that commit (for example `git archive`) and run `python tests/docker_smoke.py ai-kit:<value> --context .`. An optional `--builder NAME` scopes the synthetic context export to a dedicated builder.
4. Check a missing/mismatched version build refuses. Inspect image user, labels, entrypoint and architecture; exercise the packaged wheel without host sources.
5. Validate the [Job](../deploy/k8s/install-preview-job.yaml) against the target Kubernetes schema. Cluster dry-run and startup require a separately verified cluster context and existing PVC. No cluster deployment is part of image integration.
6. Complete [maximum cleanup](../template/ai-kit/CONTAINERS.md#post-test-docker-cleanup) after success/failure (the maintainer default; installed projects may select `keep-cache`): zero eligible disposable containers, volumes, networks, images and builder cache, without a size threshold. Use a dedicated builder; preserve data and unrelated workloads. Report Docker usage, host RAM and physical disk reclamation separately; no host compactor runs inside this CLI image.

[docker_smoke.py](../tests/docker_smoke.py) checks non-root execution, matching version/label, no service/anonymous-volume contract, offline read-only help/route/check, a project path with spaces, read-only preview and refusal, all five opt-in modules, orchestration preview/status, preserved project/client documents, doctor, design context selection, stable rerun, SIGTERM in interactive preview both with `--init` and as PID 1 without it (as in a Kubernetes Job), and LF line endings in every packaged text file outside pinned vendor bytes. It removes only its own labeled temporary signal container; ordinary commands use `--rm`. It creates no Docker volumes. Linux callers forward a non-root host UID/GID for bind ownership; Windows uses the image default. Unit tests cover the version guard and safe command construction without requiring Docker.

The `Docker CLI` CI job builds and smoke-tests the image on Ubuntu. Existing validation/wheel check names are unchanged. Hosted execution and branch-protection changes need their own evidence/authorization.

## Kubernetes contract

The supplied batch/v1 Job is a read-only preview, not an apply operation: `install /workspace --agent codex`. `backoffLimit: 0` avoids retrying a one-shot operation automatically. It has a 300-second deadline, 30-second termination grace, non-root UID/GID, RuntimeDefault seccomp, dropped capabilities, no privilege escalation, no service-account token and read-only root. It reads an existing PVC and writes temporary files to a bounded emptyDir. It has no Service or artificial probe.

`ai-kit:local`/Never requires that local image on the selected nodes. Use a reviewed registry digest/pull policy for other environments. Storage must be readable by UID 10001; no ownership mutation or fsGroup policy is assumed. CPU 100m/1 and memory 128Mi/512Mi are initial estimates, to be measured for the actual project. Add configuration, authentication or network controls only when the selected command needs them.

## Verification results

Local build and published image: [v1.5.0](V1_5_0.md#docker-hub-publication). Earlier results retain their dates/versions.

Verified locally on 2026-10-14:

- Docker Desktop 4.95.0 (242831), client/server 29.8.2, selected `desktop-linux` daemon, BuildKit v0.33.1. Built and smoke-tested `ai-kit:1.3.0` on linux/amd64. Runtime Python 3.13.16, Git 2.39.5 and AI-KIT 1.3.0 matched the declared image identity; default UID/GID was 10001:10001. Missing and mismatched version builds refused at the guard.
- Actual container smoke passed with network disabled, read-only root, temporary storage and a Windows bind mount containing spaces: preview, read-only apply refusal, all four extras with Codex/Claude entries, preserved README/MCP bytes, doctor, design context and stable rerun. Docker's ignore engine included hidden source skills and excluded synthetic secret/private files. Interactive preview received SIGTERM and exited 143 without a forced kill. Alternate UID/GID 1002:1003 installed and checked a project on temporary storage with matching created-file ownership.
- Full Windows/Python 3.12.14 discovery: 309 tests in 575.738 seconds, 307 passed and two skips (symlink privilege and unavailable POSIX sh). Both junction tests ran. Full packaged Linux/Python 3.13.16 discovery under a non-root, offline, read-only container: 309 tests in 29.096 seconds, 307 passed and two Windows-junction skips. These runs preceded the final result/ADR documentation; final packaging and kit/image checks follow that documentation update.
- Windows wheel built in an isolated source copy without network dependency resolution; offline fresh-venv smoke passed, including all opt-in modules and packaged Docker resources. Added Python files parsed with Python 3.10 grammar. Kit validation and diff review were clean.
- Job YAML passed strict field/type validation against the official [Kubernetes v1.35.0 OpenAPI schema](https://github.com/kubernetes/kubernetes/blob/v1.35.0/api/openapi-spec/swagger.json), with local preview/security assertions. Download SHA-256: `483500149ee52ce5753d75f5639101d985bb4f5e902cc05b1ba7627465d62446`. This is static schema coverage, not admission or storage/startup acceptance.
- Test containers were removed; no test Docker volumes were created. The shared `desktop-linux` builder and existing volumes contain unrelated resources, so project cache bytes/ownership could not be isolated. No cache/volume prune was performed. The local CLI image is retained; per-run inventory is kept in the task report.

In that 2026-10-14 run, registry publication, hosted CI, macOS execution, other image architectures and Kubernetes server dry-run/deployment were not run; later publication records are linked above. Native AI client activation, model calls, real benchmarks, framework/browser acceptance and security scans remain separate work.
