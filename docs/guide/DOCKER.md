# Run AI-KIT with Docker

**Run the AI-KIT CLI from a container against a mounted application folder.** The image contains Python, Git, the packaged kit and all optional integration resources. Installation and the ordinary offline helpers need no host Python or network access at runtime. Each command exits when it finishes; there is no server to keep running.

This is an alternative way to run the same installer. Open your coding agent in the application afterward and bootstrap normally. The image also bundles the optional bounded OpenRouter text executor (since 1.4.4); live execution requires explicit model/key configuration and authorization. Native Codex helpers require a compatible coding client. Web Design, Context7, Cloudflare security-audit and Strix remain opt-in instruction modules; their external tools and live execution require separate setup.

Installer options and defaults are the same as outside Docker: put them after `install /workspace`. Fresh chat replies default to English and Laravel conventions follow the owner's opinionated profile; use `--chat-language Russian --conventions standard` for Russian replies and standard conventions. Saved languages survive upgrades; UUID guidance requires `--with-uuid` independently ([defaults](INSTALL.md#choose-your-defaults), [all flags](INSTALLER_FLAGS.md)).

## Use the published image

**Published image:** [`tigusigalpa/ai-kit`](https://hub.docker.com/r/tigusigalpa/ai-kit), `linux/amd64`. Image tags match the repository `VERSION` of their release; a source `VERSION` that does not appear on the [tags page](https://hub.docker.com/r/tigusigalpa/ai-kit/tags) is not published yet. Existing tags are retained and no `latest` tag is assigned, so always name a version. Version 1.6.0 is the release target; its [verification and publication status](../V1_6_0.md#docker-hub-publication) distinguishes preparation from an available registry tag.

~~~sh
docker pull tigusigalpa/ai-kit:1.6.0
docker run --rm tigusigalpa/ai-kit:1.6.0 --version
~~~

Use that image name in the examples below (`$image = 'tigusigalpa/ai-kit:1.6.0'` in PowerShell, `image="tigusigalpa/ai-kit:1.6.0"` in Bash), or tag it locally as `ai-kit:1.6.0`. The [Docker Hub Overview](../DOCKER_HUB_OVERVIEW.md) covers capabilities, release changes and launch examples.

## Build the local image

Build locally when you need a reviewed revision that is not published as an image. Use Docker with Linux containers and a running daemon. Check the actual selected context before building:

~~~sh
docker context show
docker version
~~~

From a reviewed AI-KIT checkout, build the version recorded in `VERSION`. In PowerShell:

~~~powershell
$kitVersion = (Get-Content -LiteralPath .\VERSION -Raw).Trim()
docker build --build-arg "AIKIT_VERSION=$kitVersion" --tag "ai-kit:$kitVersion" .
~~~

On Linux or macOS:

~~~sh
kit_version="$(cat VERSION)"
docker build --build-arg "AIKIT_VERSION=$kit_version" --tag "ai-kit:$kit_version" .
~~~

The build refuses a missing or mismatched `AIKIT_VERSION`. The Dockerfile pins the Python base by digest and build tools by version and wheel hash. Building downloads those tools and Debian packages; subsequent CLI execution can be offline. Git's Debian package is resolved at build time, so identical rebuilds are not promised. Record the resulting image identity when distributing a reviewed build. These commands create a local image; they do not upload it to a registry.

The closed `.dockerignore` includes distribution sources and excludes Git, personal client configuration, common credential files, private design output, journals and caches. Review new resources before extending its allowlist. Build from the kit checkout; application files enter through the runtime mount.

## Preview and apply on Windows

Choose an existing application folder outside the AI-KIT distribution. Use its absolute path, including quotes when it contains spaces. In the same PowerShell session:

~~~powershell
$appPath = (Resolve-Path -LiteralPath 'C:\Projects\my-app').Path
$image = "ai-kit:$kitVersion"   # or 'tigusigalpa/ai-kit:1.6.0'
$runtime = @('--rm', '--init', '--network', 'none', '--read-only',
    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m')

# Preview: the project mount is read-only and the installer writes nothing.
docker run @runtime --mount "type=bind,source=$appPath,target=/workspace,readonly" $image install /workspace --agent codex --with-web-design

# After reviewing the preview, apply with a writable project mount.
docker run @runtime --mount "type=bind,source=$appPath,target=/workspace" $image install /workspace --agent codex --with-web-design --apply --check

# Later health checks can use a read-only project mount.
docker run @runtime --mount "type=bind,source=$appPath,target=/workspace,readonly" $image doctor /workspace
~~~

Select the same agents, presets and `--with-*` options in preview and apply. Add `--agent claude`, `--with-context7`, `--with-security-audit` or `--with-strix` when wanted. Existing project documents, local settings, MCP configuration and edited managed files follow the normal preservation/conflict rules. Files written to `/workspace` persist in the host folder after the container is removed.

## Preview and apply on Linux or macOS

Run from an ordinary host user. Forward that user's UID/GID so the bind-mounted project and new files have usable ownership; the image's default UID/GID is `10001:10001`. In Bash:

~~~sh
app_path="$(cd /path/to/my-app && pwd)"
image="ai-kit:$kit_version"   # or tigusigalpa/ai-kit:1.6.0
runtime=(--rm --init --network none --read-only --cap-drop ALL
  --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=256m
  --user "$(id -u):$(id -g)")

docker run "${runtime[@]}" --mount "type=bind,source=$app_path,target=/workspace,readonly" \
  "$image" install /workspace --agent codex --with-web-design

# Run after reviewing and approving the preview.
docker run "${runtime[@]}" --mount "type=bind,source=$app_path,target=/workspace" \
  "$image" install /workspace --agent codex --with-web-design --apply --check
~~~

Do not forward UID `0`; grant a chosen non-root UID access to the project instead. The container does not change host ownership automatically. Docker Desktop file-sharing permissions and remote-daemon paths must also permit the mount. If Git reports dubious ownership, use matching ownership and a narrowly reviewed Git configuration; the image does not globally trust every directory.

## Other commands and writable paths

Arguments after the image name go directly to `aikit`. Reuse the runtime options above:

~~~powershell
docker run @runtime $image --help
docker run @runtime $image check
docker run @runtime $image route 'review an interface'
docker run @runtime --mount "type=bind,source=$appPath,target=/workspace,readonly" $image context select /workspace --workflow web-design
~~~

`check` validates the bundled distribution. `doctor /workspace` validates the installed project. Read-only reports need a read-only project mount; explicit writes such as `install --apply`, `context snapshot --apply`, configuration or local records need a writable mount. The root filesystem stays read-only, with temporary storage in `/tmp`. Interactive installation also needs `-it`.

| Runtime contract | Value |
| --- | --- |
| Entrypoint and default command | `aikit`, `--help` |
| Default Linux identity | UID/GID `10001:10001` |
| Working directory and project mount | `/workspace` |
| Temporary writable storage | `/tmp`, provided by the caller |
| Network and ports | Offline examples; no exposed ports |
| Shutdown | The CLI handles SIGTERM even as PID 1 and exits with code 143, so `--init` is optional (after 1.4.5; keep `--init` for 1.4.5 and earlier images, where it forwards signals and reaps children) |
| Completion | CLI exit code: installer 0 success, 1 refusal, 2 unresolved conflicts |

Stopping an installation is not a rollback operation. After an interruption, inspect the project, run `doctor` and preview again before continuing. The container smoke test checks SIGTERM while waiting in an interactive preview; it does not establish atomic cancellation during writes.

Framework toolchains, browsers, Node/Composer, model workers, MCP connections and the Strix executable are separate. Benchmark workers need their own reviewed runtime and project dependencies. The Docker inspection helper (`aikit docker`) runs on the host with Docker access; this CLI image does not mount the Docker socket or bundle a Docker client.

## Kubernetes preview Job

[install-preview-job.yaml](../../deploy/k8s/install-preview-job.yaml) runs one read-only installation preview against an existing `aikit-project` PVC. It sets a non-root identity, read-only root, dropped capabilities, no API token, an explicit deadline and no automatic retries. `/tmp` uses `emptyDir`; project data uses the PVC.

Its `ai-kit:local` image with `imagePullPolicy: Never` is a local-cluster example. Load/tag the reviewed image in the intended test cluster, or replace it with your registry image pinned by digest and an appropriate pull policy. Ensure UID `10001` can read the PVC. Initial CPU/memory requests and limits are estimates, not measured recommendations. A one-shot CLI reports completion through its exit code, so this Job needs no Service or HTTP probe. Before deployment, verify the actual cluster version, context, namespace, storage and resource requirements. Local schema checks do not establish a successful cluster run.

## Verify or update the image

~~~sh
python scripts/check_kit.py
python -m unittest discover -s tests -v
python tests/docker_smoke.py ai-kit:1.6.0 --context .
~~~

Use the tag you actually built. The Docker smoke uses disposable synthetic projects, no runtime network and Docker's actual ignore engine; it checks preview/apply, all optional modules, preservation, rerun stability, read-only refusal and SIGTERM. CI builds and tests a local image without publishing it. [Maintainer contract and results](../DOCKER.md) records pins, packaging, checks and unavailable environments.

For an upgrade, review the new revision, rebuild with VERSION, preview against the same application and apply normally. Review build inputs and rerun image checks. Complete the canonical [post-test cleanup](../../template/ai-kit/CONTAINERS.md#post-test-docker-cleanup) afterward; the operational guide below distinguishes resource deletion, RAM return and virtual-disk compaction.

## Docker cleanup and host reclamation

AI-KIT requires housekeeping after **every Docker build, test and debugging task**, including failed or interrupted runs once diagnostic evidence is saved. Agents clean within established ownership and authorization; installation itself runs no cleanup daemon or host compactor. The [container contract](../../template/ai-kit/CONTAINERS.md#post-test-docker-cleanup) owns the rules.

The project setting `docker_cleanup` in `ai-kit/settings.json`, set with the installer flag `--docker-cleanup`, selects one of two modes (added after 1.4.5; earlier releases always behave like `maximum`):

| Mode | After every Docker task | Host RAM/disk reclamation |
| --- | --- | --- |
| `maximum` (default) | Remove all eligible disposable Docker resources, including the dedicated builder and its cache. There is **no size or age threshold**; the goal is **zero eligible disposable resources**, rather than retaining a cache allowance. | After every task, as described below |
| `keep-cache` | Still remove task-owned containers, networks, volumes and superseded test images, but keep the dedicated project builder and its cache for faster rebuilds. | Only on explicit request or observed resource pressure |

~~~sh
aikit install /path/to/my-app --docker-cleanup keep-cache
~~~

Preview, then apply with `--apply`. An absent setting means `maximum`; the saved value is reused on upgrades.

### What the agent must remove

| Resource | Required treatment |
| --- | --- |
| Temporary containers | Save necessary reports, stop completed task-owned services and remove their containers. |
| Anonymous and named test volumes | Remove all proven-disposable, unreferenced volumes after checking their data purpose. An unused database volume can still hold important data. |
| Test networks | Remove disposable networks after their containers are removed and references rechecked. |
| Images | Remove unnecessary intermediate/superseded test images; preserve the required final image and documented recovery artifacts. |
| Build cache | Use a dedicated project/run builder, remove all its reclaimable cache and retire disposable builders through Buildx. With `keep-cache`, keep the dedicated project builder and its cache instead. Shared caches need exact record ownership or an established host-wide scope. |
| Host RAM and disk allocation | Perform supported reclamation separately and measure it separately from Docker's deleted bytes. With `keep-cache`, only on explicit request or observed resource pressure. |

Before creating resources, record the Docker context, run identity and builder. Add project/run labels and `ai-kit.disposable=true` to temporary containers, networks and volumes. Keep reports outside disposable storage. Exact known-safe resources can be removed even if their byte count is unavailable; unknown ownership never becomes permission to erase data.

For new builds, use a builder dedicated to the task. These Bash/PowerShell-compatible commands illustrate a new, previously unused builder name:

```sh
docker buildx create --name myapp-tests --driver docker-container
docker buildx build --builder myapp-tests --load --tag myapp:test .
docker buildx du --builder myapp-tests
```

After all work using that builder has completed and the required final image is retained (in `maximum` mode; `keep-cache` keeps the dedicated project builder):

```sh
docker buildx prune --builder myapp-tests --all --force
docker buildx rm myapp-tests
```

Verify no active build uses it first. Do not reuse the example name if it belongs to another task. Removing a builder through Buildx is preferable to deleting its storage volume directly. The `--all` flag also includes internal/frontend cache records; supported options depend on installed Buildx. [Buildx prune](https://docs.docker.com/reference/cli/docker/buildx/prune/).

For containers, images, networks and volumes, use the exact reviewed IDs/names. `docker system df -v` and the read-only `scripts/docker_test_usage.py --project NAME --builder NAME` helper provide evidence; the helper neither decides disposability nor deletes anything.

**A complete local development-host cleanup is a separate scope.** Establish it once with the owner, record retained resources and reuse that agreement. `docker system prune --all --volumes` removes stopped containers, unused images/networks/cache and anonymous volumes; it does **not** remove all unused named volumes. `docker volume prune --all` can remove named volumes and their data. Do not apply these broad commands to a shared/remote daemon or unknown volumes merely because Docker reports them as unused. [Docker pruning semantics](https://docs.docker.com/engine/manage-resources/pruning/).

### Return RAM to Windows with WSL2

Deleting images and volumes does not prove that Windows received RAM back. Check the installed Docker Desktop backend and WSL version. In WSL2, Resource Saver pauses the engine and reduces CPU use; it does not itself reclaim WSL RAM. Use supported WSL memory reclamation. [Docker Resource Saver](https://docs.docker.com/desktop/use-desktop/resource-saver/).

When host configuration changes are authorized, merge this value into the existing user `.wslconfig` under its existing `[experimental]` section, preserving other sections and settings:

```ini
[experimental]
autoMemoryReclaim=dropCache
```

Check whether it is already set; do not create duplicate sections or overwrite memory/CPU/network settings. Configuration applies when WSL restarts. `wsl --shutdown` stops **all** WSL distributions, so schedule it only in an authorized maintenance window after checking other terminals, services, containers and builds. Otherwise leave unrelated work running and report the pending restart. Measure actual host memory before and after; configuration alone is not proof of reclaimed bytes. [Microsoft WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

### Reclaim physical virtual-disk space

Docker's logical usage, a virtual disk's capacity and the disk file's physical allocation are different measurements. Removing resources can leave a large VHDX on the Windows disk.

1. Finish resource cleanup and preserve required data/backups. Identify the actual Docker backend, configured data location and exact virtual disk; locations vary between Docker Desktop versions and can be customized.
2. Use that backend/version's supported trim or disk-reclaim procedure. Check the applicable release notes; automatic reclaim behavior has changed between versions.
3. If physical allocation remains, prepare supported **offline compaction**. Verify the resolved disk path, backup/recovery method, sufficient host free space and an authorized idle maintenance window. Stop Docker/WSL gracefully only after establishing that no unrelated workloads will be interrupted.
4. Compact only a detached or read-only dynamic disk with supported tooling, such as DiskPart `compact vdisk` where applicable. Never compact a live disk, use `clean`, erase/unregister the Docker distro, delete the data VHDX, shrink filesystem capacity or fill the disk with zero files as a shortcut.
5. Restore the runtime if it was stopped, verify retained containers/data and compare host free space and physical allocation. Sparse-file length alone is not an allocation measurement. If the backend, privileges or maintenance window are unavailable, report the specific blocker; complete all other eligible cleanup.

[Microsoft compaction requirements](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk) and [Docker release notes](https://docs.docker.com/desktop/release-notes/) define supported behavior. A running CLI container cannot compact its host's Docker disk; the image intentionally has no Docker socket or administrative host access.

The completion report lists removed resources, eligible leftovers (target zero), protected resources/reasons, and separately verified Docker/cache, RAM and host-disk changes. Do not report physical reclamation merely because prune succeeded.
