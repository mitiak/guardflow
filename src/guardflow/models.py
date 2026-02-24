from pydantic import BaseModel, ConfigDict


class Actor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    role: str


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool: str
    args: dict


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actor: Actor
    tool_call: ToolCall


class ToolResult(BaseModel):
    step: str
    ok: bool
    data: dict


class SchemaError(BaseModel):
    code: str = "SCHEMA_REJECTED"
    detail: str


class PolicyError(BaseModel):
    code: str = "UNAUTHORIZED_TOOL"
    tool: str
    detail: str
