"""Policy model and enforcement for the allowlist gate."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

DEFAULT_POLICY_PATH = Path("policy.json")


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allowed_tools: list[str]

    @classmethod
    def load(cls, path: Path = DEFAULT_POLICY_PATH) -> "Policy":
        with open(path) as f:
            return cls.model_validate(json.load(f))

    def is_allowed(self, tool: str) -> bool:
        return tool in self.allowed_tools


class PolicyViolation(Exception):
    def __init__(self, tool: str) -> None:
        self.tool = tool
        super().__init__(tool)
