# Docker and microservices: Kubernetes-ready

Design all new Dockerfiles, containers, and microservices to be Kubernetes-ready from their first implementation, including local projects using Docker Compose. Readiness means a portable image and an explicit contract for startup, configuration, health, shutdown, and data storage. Apply the criteria to the container's role; record justified exceptions in the context and decision log.

## Runtime preflight

For Docker-dependent programming, verify both the Docker client and the selected context's daemon on the user's machine using actual availability/version checks.
A missing client, stopped daemon, wrong context, and permission failure are different outcomes. If the daemon is stopped, ask the user to start Docker Desktop/Engine; if the client is missing, request installation/configuration of the project's runtime.
Continue independent work while waiting, then repeat the relevant check after the user responds. Do not claim container tests passed before running them.
If the agent cannot access the user's runtime, ask for the client/daemon check results and mark local container checks unavailable. Tasks without a Docker dependency need no startup request.

## Image freshness

- For every task, assess image impact: code, installed instructions/templates, assets, dependencies, configuration defaults, build context, entrypoint and runtime contracts. Source edits and restarting an old container do not update its image.
- Rebuild affected images from final sources; fix build/packaging inputs when needed. Test the changed behavior inside the container, checking version/labels, resources, user and relevant mounts/signals. Descriptive documentation, publication receipts or mounted data alone may need no rebuild; record the reason and any bundled-document snapshot difference.
- Use a development tag for unreleased work and preserve published release identities. Report local build/test status separately from registry freshness. Publishing or replacing registry tags requires user authorization; report unavailable runtime checks explicitly.

## Image and startup

- Provide a Dockerfile and `.dockerignore` for each new microservice. Build a standalone runtime image containing its code and dependencies. It must run without source code mounted from the developer's machine or package installation at startup. Separate build and runtime through multi-stage builds when build tools or development dependencies are present.
- Use a supported, minimal base image, pin its version, and use an immutable image reference for releases (a digest or a guaranteed immutable tag). Update the base regularly with compatibility checks; do not use `latest` for releases.
- Create `.dockerignore` for the actual build context: exclude Git, secrets, local AI-KIT files, caches, and unnecessary artifacts. Pass build secrets through the builder's secure mechanism to keep them out of image layers.
- In a Linux runtime, run the application as a non-root user with explicit UID/GID and correct permissions for required directories. Design for a read-only root filesystem with explicitly allocated writable volumes. Avoid requiring privileged mode, host networking, the Docker socket, or paths on the developer's machine; justify necessary exceptions.
- Separate web, worker, and scheduler roles into independently runnable workloads; one image may support several commands. Run the main process in the foreground. Use exec-form `ENTRYPOINT`/`CMD`; end shell wrappers with `exec`, ensure signal delivery, and reap child processes.

## Configuration, networking, and data

- Pass configuration through environment variables or mounted files, and supply secrets separately. In Kubernetes, use ConfigMap for ordinary settings and Secret or the project's secret manager for sensitive data. Keep environment-specific settings, passwords, service addresses, and actual secrets out of images and manifests; validate required configuration at startup.
- A network service listens on an interface reachable through the Pod, usually `0.0.0.0`; make its port and dependency addresses configurable. Use service discovery/DNS, timeouts, and bounded retries; account for startup order being unspecified.
- Write logs to stdout/stderr. Stateless application services must tolerate Pod replacement and multiple replicas: store sessions, jobs, and required shared data in external services. Protect one-off operations and jobs against duplication on retries.
- Keep persistent data out of the container's writable layer. For databases, Moodle `moodledata`, and other stateful components, use external storage or a PVC; document backup and scaling constraints. `emptyDir` is suitable for temporary files; check data access and volume permissions.

## Health and shutdown

- Provide a real readiness check for a service accepting traffic; liveness checks internal health when a restart can fix a failure. Do not tie liveness to database or another service's availability. Add a startup probe for slow startup. Choose HTTP, gRPC, TCP, or exec for the actual protocol and role; do not return unconditional success.
- Configure Kubernetes probes explicitly in manifests. Keep Docker `HEALTHCHECK`, if used locally, consistent with the health contract. Use a suitable health signal for a worker; a one-off Job exits with the correct code, without an artificial HTTP server or an endless wait.
- Handle `SIGTERM` or the documented stop signal: stop accepting new work, finish requests gracefully, and release resources. For queues, provide safe job completion or return the job to the queue. Align shutdown time with `terminationGracePeriodSeconds`; include `preStop` in the same time budget.
- Run migrations and other one-off actions as separate managed commands/Jobs; do not run them concurrently at every replica's startup. Preserve compatibility between old and new versions during rolling updates.

## Minimal manifests

- Create minimal Kubernetes manifests alongside each new service in the project's chosen directory (for example, `deploy/k8s/`). Use existing Helm/Kustomize conventions when present; plain YAML is sufficient for a simple project.
- Choose the workload by purpose: Deployment for replaceable replicas; StatefulSet when stable identity and an ordered lifecycle are required; Job/CronJob for one-off/scheduled tasks. Add a Service only for required network access.
- Specify the image, command, consistent labels/selectors and ports, configuration, applicable probes, volumes, and shutdown time. Set CPU/memory requests and justified limits; label initial values as estimates and verify them with measurements.
- For Linux, set `runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, `seccompProfile: RuntimeDefault`, and `readOnlyRootFilesystem: true` with necessary writable volumes. Grant ServiceAccount permissions as needed; disable token automount when the application does not use the Kubernetes API.
- Verify API compatibility with the target Kubernetes version. Add Ingress/Gateway, HPA, PDB, and NetworkPolicy according to project requirements and cluster capabilities.

## Verification and documentation

- For changed container code, check runtime image build and startup with external configuration, the declared user, and volumes; verify health, signal delivery, and graceful shutdown. For a stateless service, check restart and multiple replicas when the change affects those behaviors.
- Validate rendered manifests and their schemas; when a test cluster is available, run a server dry-run and the necessary startup/update check. Verify cluster context and namespace before working with it. State unavailable checks explicitly; distinguish a local build from a verified Kubernetes deployment.
- Record actual commands, ports, environment variables, probes, writable paths, resource needs, storage requirements, and shutdown behavior in README and `PROJECT_CONTEXT.md`. Record significant decisions in ADRs and changes in `CHANGELOG.md` according to the [engineering cycle](ENGINEERING.md).

## Post-test Docker cleanup

The `docker_cleanup` value in [settings](settings.json) selects the scope; a missing value means `maximum`.

| Mode | After every Docker task |
| --- | --- |
| `maximum` (default) | Apply every rule below: remove all eligible disposable resources, including the dedicated builder and its cache, and reclaim host resources |
| `keep-cache` | Remove task-owned containers, networks, volumes and superseded test images; keep the dedicated project builder and its cache for faster rebuilds; reclaim host RAM/disk only on explicit request or observed resource pressure |

- Cleanup is mandatory after every Docker build, test or debugging task, including failed/interrupted runs after diagnostics are saved. **No size or age threshold applies. Target zero eligible disposable resources**, not a retained cache allowance; in `keep-cache` mode the dedicated project builder and its cache are retained by design, not eligible. Do not finish with known removable leftovers; clean after each completed phase and at task end. This authorizes verified disposable task resources without another confirmation. Preserve the required final image, active services and explicitly retained recovery artifacts.
- Verify context/daemon; inventory containers, images, networks, volumes and builders. Prove ownership/disposability from labels, configuration or creation IDs; a name or unused/reclaimable status is insufficient. Label temporary resources with project/run identity and `ai-kit.disposable=true`. Unknown byte counts do not block proven-safe exact removals. Use `docker system df -v` and [buildx du](https://docs.docker.com/reference/cli/docker/buildx/du/); count builder backing storage once.
- Save reports, stop finished task-owned test services, remove their containers, then remove all unreferenced disposable volumes, networks and intermediate/superseded test images. Include named volumes when proven disposable. Recheck references before deletion; use exact IDs/names or verified positive filters. Preserve persistent databases, user/development data, backups, bind mounts, unrelated projects, active builds and resources with unknown ownership; never force-delete in-use resources.
- Prefer a dedicated project/run builder from the start. In `maximum` mode, [prune](https://docs.docker.com/reference/cli/docker/buildx/prune/) all its unused cache, including internal/frontend records when supported, then remove a disposable builder through `docker buildx rm` without retaining its state. In `keep-cache` mode, keep that dedicated builder and its cache. Shared builders require exact eligible-record filters or separately established host-wide maintenance scope. Check actual CLI flags. Do not infer cache scoping from Compose labels or delete a builder's backing volume directly.
- Maximum host-wide pruning requires a verified local development daemon and existing owner authorization covering every affected resource class, including named volumes and shared caches. Review its inventory and exclusions first; reuse standing authorization. Otherwise clean the proven project scope and report the remainder. `docker system prune --all --volumes` includes anonymous volumes, not all named volumes; a separate `docker volume prune --all` can erase unused named data. Neither is a project-scoped substitute for exact removal. Never reset Docker, unregister a distro or erase its data disk as cleanup.
- Reclaim host resources separately (every task in `maximum` mode; on explicit request or observed pressure in `keep-cache` mode): RAM, Docker usage and allocated host disk bytes. On WSL2, verify/merge supported `autoMemoryReclaim=dropCache` in `[experimental]` when host changes are authorized; preserve other settings. Resource Saver alone does not reclaim WSL RAM. Use supported backend trim/reclaim; if allocation remains, complete supported offline VHDX compaction in an authorized idle window. Discover the real disk from backend configuration; verify resolved path, backup and detached/read-only state. Never interrupt unrelated Docker/WSL work, compact a live disk, fill it with zero files or shrink filesystem capacity. Report blocked prerequisites and continue other cleanup.
- Measure again: removed IDs, eligible leftovers (target zero), retained resources/reasons, Docker/cache bytes and separately observed host disk/RAM reclamation. Do not claim RAM release or disk compaction from prune output. Record stable ownership, retention and maintenance scope in `PROJECT_CONTEXT.md`; keep run inventories/results in the task report. [Docker reclamation](https://docs.docker.com/desktop/use-desktop/resource-saver/), [WSL settings](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) and [offline compaction](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk) must match the installed backend/version.

These rules use the official Docker guidance for [builds](https://docs.docker.com/build/building/best-practices/) and [ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint), and Kubernetes guidance for [probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [security](https://kubernetes.io/docs/concepts/security/application-security-checklist/), [workloads](https://kubernetes.io/docs/concepts/workloads/), [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/), [Secret](https://kubernetes.io/docs/concepts/configuration/secret/), [storage](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), and [resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/). During adaptation, check the documentation against actual project versions.
