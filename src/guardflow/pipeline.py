"""Stub execution pipeline: validate → authorize → execute."""

import logging

logger = logging.getLogger(__name__)


def validate(data: dict) -> dict:
    """Validate the incoming tool-call request."""
    logger.info(f"pipeline.validate: {data}")
    return {"step": "validate", "ok": True, "data": data}


def authorize(data: dict) -> dict:
    """Authorize the tool-call against active policy."""
    logger.info(f"pipeline.authorize: {data}")
    return {"step": "authorize", "ok": True, "data": data}


def execute(data: dict) -> dict:
    """Execute the tool call in a sandboxed context."""
    logger.info(f"pipeline.execute: {data}")
    return {"step": "execute", "ok": True, "data": data}


def run_pipeline(data: dict) -> dict:
    """Run the full validate → authorize → execute pipeline."""
    result = validate(data)
    result = authorize(result)
    result = execute(result)
    return result
