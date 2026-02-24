"""Execution pipeline: validate → authorize → execute."""

import logging

from pydantic import ValidationError

from guardflow.models import RunRequest, ToolResult
from guardflow.policy import Policy, PolicyViolation

logger = logging.getLogger(__name__)


def validate(data: dict) -> RunRequest:
    """Validate the incoming tool-call request against the RunRequest schema."""
    logger.info(f"pipeline.validate: {data}")
    return RunRequest.model_validate(data)


def authorize(request: RunRequest, policy: Policy) -> RunRequest:
    """Authorize the tool-call against active policy."""
    if not policy.is_allowed(request.tool_call.tool):
        raise PolicyViolation(request.tool_call.tool)
    logger.info(f"pipeline.authorize: {request}")
    return request


def execute(request: RunRequest) -> ToolResult:
    """Execute the tool call in a sandboxed context."""
    logger.info(f"pipeline.execute: {request}")
    return ToolResult(step="execute", ok=True, data=request.model_dump())


def run_pipeline(data: dict, policy: Policy) -> ToolResult:
    """Run the full validate → authorize → execute pipeline."""
    request = validate(data)
    request = authorize(request, policy)
    return execute(request)
