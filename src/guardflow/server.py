"""FastAPI HTTP wrapper for the guardflow pipeline."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError

from guardflow.models import Actor, RunRequest, ToolCall, ToolResult
from guardflow.pipeline import authorize, validate
from guardflow.policy import Policy, PolicyViolation
from guardflow.rbac import RbacDenial, RbacPolicy

logger = logging.getLogger(__name__)

_POLICY_PATH = Path("/app/policy.json")
_MODEL_CONF_PATH = Path("/app/model.conf")
_RBAC_POLICY_PATH = Path("/app/rbac_policy.csv")


def _load_policy() -> Policy:
    path = _POLICY_PATH if _POLICY_PATH.exists() else Path("policy.json")
    return Policy.load(path)


def _load_rbac() -> RbacPolicy:
    model_path = _MODEL_CONF_PATH if _MODEL_CONF_PATH.exists() else Path("model.conf")
    policy_path = _RBAC_POLICY_PATH if _RBAC_POLICY_PATH.exists() else Path("rbac_policy.csv")
    return RbacPolicy.load(model_path, policy_path)


app = FastAPI(title="guardflow", version="0.1.0")


class _HealthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "GET /health" not in record.getMessage()


logging.getLogger("uvicorn.access").addFilter(_HealthFilter())


class AuthorizeRequest(BaseModel):
    actor: Actor
    tool_call: ToolCall


class AuthorizeResponse(BaseModel):
    ok: bool
    step: str
    data: dict


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/authorize", response_model=AuthorizeResponse)
def authorize_endpoint(request: AuthorizeRequest) -> AuthorizeResponse:
    policy = _load_policy()
    rbac = _load_rbac()
    raw = request.model_dump()
    try:
        run_request = validate(raw)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "SCHEMA_REJECTED", "errors": exc.errors()},
        ) from exc
    try:
        authorize(run_request, policy, rbac)
    except PolicyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "UNAUTHORIZED_TOOL", "tool": exc.tool},
        ) from exc
    except RbacDenial as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "RBAC_DENIED", "role": exc.role, "tool": exc.tool},
        ) from exc
    return AuthorizeResponse(ok=True, step="authorize", data=run_request.model_dump())
