# Multi-stage Dockerfile for signal-pilot backend.
#
# Stage 1 — build wheels for native deps in a fat image so the final
# image stays slim. The backend has minimal native code (sqlite is
# bundled in Python), but voyageai/anthropic/numpy install faster
# with build tools available.
#
# Stage 2 — copy only the venv + source into a slim runtime image.

FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Native build deps. ``--no-install-recommends`` keeps the layer
# small; we remove apt lists after install in the same RUN so
# nothing lingers in the layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m venv /venv && /venv/bin/pip install -r requirements.txt


FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Run as an unprivileged user. The Dockerfile creates a fixed UID
# so the bind-mounted ``data/`` directory ownership is predictable
# in compose / k8s setups.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home app

WORKDIR /app

COPY --from=builder /venv /venv
COPY backend/ ./backend/
COPY core/ ./core/
COPY config.py ./
COPY playbooks/ ./playbooks/

# Data and backup dirs are mounted at runtime. Created here so the
# image has the right ownership baked in.
RUN mkdir -p /app/data /app/backups \
    && chown -R app:app /app

USER app

EXPOSE 8000

# Healthcheck hits our deep readiness endpoint so the orchestrator
# notices DB/disk/Anthropic problems even if the process is up.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8000/health/live',timeout=5); sys.exit(0 if r.status==200 else 1)"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
