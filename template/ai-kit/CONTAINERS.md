# Docker and microservices: Kubernetes-ready

Design all new Dockerfiles, containers, and microservices to be Kubernetes-ready from their first implementation, including local projects using Docker Compose. Readiness means a portable image and an explicit contract for startup, configuration, health, shutdown, and data storage. Apply the criteria to the container's role; record justified exceptions in the context and decision log.

## Runtime preflight

For Docker-dependent programming, verify both the Docker client and the selected context's daemon on the user's machine using actual availability/version checks.
A missing client, stopped daemon, wrong context, and permission failure are different outcomes. If the daemon is stopped, ask the user to start Docker Desktop/Engine; if the client is missing, request installation/configuration of the project's runtime.
Continue independent work while waiting, then repeat the relevant check after the user responds. Do not claim container tests passed before running them.
If the agent cannot access the user's runtime, ask for the client/daemon check results and mark local container checks unavailable. Tasks without a Docker dependency need no startup request.

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

- After Docker-based testing, including failed or interrupted runs once diagnostics are preserved, measure the combined size of Docker volumes and build caches belonging to the current project's test environment. The cleanup threshold is **strictly greater than 10 GB (10,000,000,000 bytes)**. At or below this threshold, size alone does not trigger cleanup.
- Verify the Docker context/daemon, test project identity, exact volume names, and builder/cache scope. Use [Docker disk usage](https://docs.docker.com/reference/cli/docker/system/df/) (`docker system df -v`) and the relevant [builder's cache usage](https://docs.docker.com/reference/cli/docker/buildx/du/). Count shared storage once; do not add a BuildKit backing volume's size to the cache it stores. If size or ownership cannot be established, report the unknowns without guessing or broadening deletion.
- When the combined size exceeds the threshold, remove unused, disposable test volumes and reclaimable test build-cache records until usage is at or below 10 GB, or no eligible resources remain. Preserve test reports and debugging evidence first. This rule authorizes cleanup of verified disposable test resources within the task; a separate confirmation is not needed for those resources.
- Prove disposability using test configuration, explicit lifecycle labels, or a documented inventory. An unused volume or a matching name alone does not prove its data is disposable. Preserve persistent databases, development/user data, backups, bind-mounted directories, resources used by other projects, and active builds/services. Stop/remove only completed disposable test containers when needed to release their volumes; recheck references before deletion and do not force removal of in-use resources. Use [volume removal](https://docs.docker.com/reference/cli/docker/volume/rm/) for verified names.
- Limit [build-cache pruning](https://docs.docker.com/reference/cli/docker/buildx/prune/) to a verified dedicated test builder or supported filters identifying the project's reclaimable records. A shared builder is not automatically project-scoped. Check the installed version's supported flags; do not run unscoped system, volume, or builder pruning to meet the threshold. Do not delete the builder's storage volume directly as a cache-cleanup shortcut.
- Measure again and report before/after usage, reclaimed space when verifiable, removed resources, and protected or unavailable cleanup. If protected/in-use resources keep usage above 10 GB, report the remaining size and reason; do not expand the deletion scope. Record stable test resource ownership and cleanup commands in `PROJECT_CONTEXT.md`; keep per-run results in the task report rather than permanent context.

These rules use the official Docker guidance for [builds](https://docs.docker.com/build/building/best-practices/) and [ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint), and Kubernetes guidance for [probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/), [security](https://kubernetes.io/docs/concepts/security/application-security-checklist/), [workloads](https://kubernetes.io/docs/concepts/workloads/), [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/), [Secret](https://kubernetes.io/docs/concepts/configuration/secret/), [storage](https://kubernetes.io/docs/concepts/storage/persistent-volumes/), and [resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/). During adaptation, check the documentation against actual project versions.
