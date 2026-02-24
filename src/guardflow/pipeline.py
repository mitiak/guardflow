"""Execution pipeline: validate → authorize → execute."""

import logging

from pydantic import ValidationError

from guardflow.models import RunRequest, ToolResult
from guardflow.policy import Policy, PolicyViolation
from guardflow.rbac import RbacPolicy, RbacDenial
from guardflow.sandbox import run_python, SandboxError

logger = logging.getLogger(__name__)


def validate(data: dict) -> RunRequest:
    """Validate the incoming tool-call request against the RunRequest schema."""
    logger.info(f"pipeline.validate: {data}")
    return RunRequest.model_validate(data)


def authorize(request: RunRequest, policy: Policy, rbac: RbacPolicy) -> RunRequest:
    """Authorize the tool-call against active policy."""
    if not policy.is_allowed(request.tool_call.tool):   # gate 1: allowlist
        raise PolicyViolation(request.tool_call.tool)
    rbac.check(request.actor.role, request.tool_call.tool)  # gate 2: RBAC
    logger.info(f"pipeline.authorize: {request}")
    return request


def execute(request: RunRequest) -> ToolResult:
    """Execute the tool call, dispatching to the Docker sandbox for python_exec."""
    logger.info(f"pipeline.execute: {request}")
    if request.tool_call.tool == "python_exec":
        code = request.tool_call.args.get("code", "")
        sandbox_result = run_python(code)
        return ToolResult(step="execute", ok=True, data={**request.model_dump(), "sandbox": sandbox_result})
    return ToolResult(step="execute", ok=True, data=request.model_dump())


def run_pipeline(data: dict, policy: Policy, rbac: RbacPolicy) -> ToolResult:
    """Run the full validate → authorize → execute pipeline."""
    request = validate(data)
    request = authorize(request, policy, rbac)
    return execute(request)
