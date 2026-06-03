"""OpenTelemetry tracing wire-up — Phase 13.11.

Spans we care about:

  • ``chat.turn``         — one operator turn end-to-end (parent)
  • ``chat.iteration``    — one Anthropic round inside the turn loop
  • ``chat.skill``        — one skill invocation
  • ``chat.anthropic``    — the actual messages.stream / .create call
  • ``chat.compaction``   — when the compaction layer fires
  • ``chat.self_correct`` — citation rewrite call when hallucinated

The OTLP exporter is enabled by setting ``OTEL_EXPORTER_OTLP_ENDPOINT``
(e.g. ``http://otel-collector:4318``). In its absence we use the
console exporter, which is loud but useful in dev. The console
exporter can be silenced by setting ``OTEL_DISABLE_CONSOLE_EXPORTER=1``.

Daemon threads spawned per turn need explicit context propagation:
``Context.attach`` at the top of the daemon's bootstrap so spans
created inside it nest correctly under the HTTP request span.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

log = logging.getLogger(__name__)


_TRACER_PROVIDER_INITIALISED = False


def _configure_provider() -> None:
    """Idempotent setup — calling twice is a no-op. Exporter choice
    is driven by env vars so the same code path works in dev and
    production without conditional imports."""
    global _TRACER_PROVIDER_INITIALISED
    if _TRACER_PROVIDER_INITIALISED:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
            SimpleSpanProcessor,
        )
    except ImportError:
        log.warning(
            "opentelemetry not installed — tracing disabled. "
            "pip install opentelemetry-{api,sdk}"
        )
        _TRACER_PROVIDER_INITIALISED = True
        return

    resource = Resource.create(
        {
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "signal-pilot"),
            "service.version": os.environ.get("APP_VERSION", "dev"),
        }
    )
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )
            log.info("OTLP tracing enabled → %s", otlp_endpoint)
        except ImportError:
            log.warning(
                "OTEL_EXPORTER_OTLP_ENDPOINT set but otlp http exporter "
                "missing; install opentelemetry-exporter-otlp-proto-http"
            )

    if os.environ.get("OTEL_DISABLE_CONSOLE_EXPORTER", "").lower() not in (
        "1",
        "true",
        "yes",
    ) and not otlp_endpoint:
        # Console exporter only when no real backend is configured —
        # avoids double-logging in production.
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _TRACER_PROVIDER_INITIALISED = True


def get_tracer(name: str = "signal-pilot") -> Any:
    """Lazy tracer accessor. Returns a no-op tracer if OTEL isn't
    installed so call sites never have to guard."""
    _configure_provider()
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return _NoopTracer()


class _NoopSpan:
    def set_attribute(self, *args, **kwargs):
        pass

    def set_status(self, *args, **kwargs):
        pass

    def record_exception(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _NoopTracer:
    def start_as_current_span(self, *args, **kwargs):
        return _NoopSpan()


def current_context() -> Any:
    """Snapshot the current OTEL context — usable for propagating a
    parent span into a daemon thread via ``context.attach`` /
    ``context.detach``."""
    try:
        from opentelemetry import context as otc

        return otc.get_current()
    except ImportError:
        return None


@contextmanager
def attached_context(token: Any) -> Iterator[None]:
    """Attach a previously-captured OTEL context for the duration of
    this with-block. Used by daemon-thread bootstrap so spans nest
    under the HTTP request that triggered them."""
    if token is None:
        yield
        return
    try:
        from opentelemetry import context as otc

        attach_token = otc.attach(token)
        try:
            yield
        finally:
            otc.detach(attach_token)
    except ImportError:
        yield
