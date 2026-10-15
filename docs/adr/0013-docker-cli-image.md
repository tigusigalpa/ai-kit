# ADR 0013: Standalone Docker CLI image

- Date: 2026-10-14
- Status: accepted for local integration; registry and cluster deployment remain separate.

## Context

The owner requested a Docker image for the portable instruction/installer kit. The existing Python CLI already supports preview, explicit apply, preservation, conflict candidates and scoped helpers. Its workload is a command that finishes; no server, agent loop or model adapter is required.

## Decision

Package the existing no-runtime-dependency wheel in a multi-stage Linux image. Pin the Python base by digest and build tools by wheel hashes. Require the source VERSION to match the OCI label; resolve Debian Git packages at build time and record actual runtime versions. The runtime starts offline without installing packages or mounting source code.

Run as UID/GID 10001:10001, with exec-form `aikit`, writable temporary storage and an explicitly mounted application. Support an alternate non-root UID for host ownership. Preview uses a read-only project mount; writes retain the installer's explicit apply/conflict contract. Preserve installer defaults and canonical template policies. Ship no Docker socket, credentials, scanner runtime, HTTP server or model worker.

Use a Kubernetes Job for an optional installation preview. Its exit status is the health/completion contract: no Service or artificial probes. Disable automatic retries, API-token mounting and privilege escalation; allocate temporary storage separately from the existing project PVC. Resource values are estimates. Apply operations and actual cluster deployment require a separately reviewed configuration.

SIGTERM stops the foreground CLI. This does not promise a transactional rollback during installation; after interrupted writes, inspect, run doctor and preview again. Add no launcher that changes host ownership or globally trusts Git directories. A shared builder does not establish test-cache ownership and cannot justify pruning.

## Consequences and verification

Users can run the installer without host Python; native client activation and external toolchains remain separate. Builds need network access and regular base/tool review. Git package resolution means rebuild bytes can differ; distribution requires a reviewed final image identity and explicit publication authorization.

The [README](../../README.md#run-ai-kit-with-docker) documents usage. [Docker verification](../DOCKER.md#verification-results) records actual builds, offline/non-root/read-only behavior, all extras, preservation, reruns, signals, wheel resources, full regressions and schema coverage. Synthetic tests do not establish application, hosted CI or cluster acceptance.
