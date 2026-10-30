# CLI runtime. Build from a clean LF checkout with --build-arg AIKIT_VERSION=<VERSION file value>
# and --build-arg AIKIT_REVISION=<full source commit>.
FROM scratch AS context-audit
COPY . /

FROM python:3.13.16-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641 AS wheel-builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /build/source
ARG AIKIT_VERSION
COPY VERSION ./VERSION
COPY docker/check_version.py /build/check_version.py
RUN python /build/check_version.py
COPY docker/build-requirements.txt /build/build-requirements.txt
RUN python -m pip install --require-hashes -r /build/build-requirements.txt
COPY . .
RUN python -m pip wheel . --no-index --no-deps --no-build-isolation --wheel-dir /build/wheels

FROM python:3.13.16-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641 AS runtime
ARG AIKIT_VERSION
ARG AIKIT_REVISION=unknown
LABEL org.opencontainers.image.title="AI-KIT CLI" \
      org.opencontainers.image.description="Offline AI-KIT instructions, installer and project helpers" \
      org.opencontainers.image.source="https://github.com/tigusigalpa/ai-kit" \
      org.opencontainers.image.licenses="MIT AND Apache-2.0" \
      org.opencontainers.image.version="${AIKIT_VERSION}" \
      org.opencontainers.image.revision="${AIKIT_REVISION}"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONNOUSERSITE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 aikit \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin aikit \
    && mkdir -p /workspace \
    && chown 10001:10001 /workspace
COPY --from=wheel-builder /build/wheels /wheels
RUN python -m pip install --no-index --no-deps /wheels/*.whl \
    && rm -rf /wheels
USER 10001:10001
WORKDIR /workspace
STOPSIGNAL SIGTERM
ENTRYPOINT ["aikit"]
CMD ["--help"]
