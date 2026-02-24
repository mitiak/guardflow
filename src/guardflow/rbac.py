"""Casbin-based RBAC policy enforcement."""

from pathlib import Path

import casbin

DEFAULT_RBAC_MODEL_PATH = Path("model.conf")
DEFAULT_RBAC_POLICY_PATH = Path("rbac_policy.csv")


class RbacDenial(Exception):
    def __init__(self, role: str, tool: str) -> None:
        self.role = role
        self.tool = tool
        super().__init__(f"role '{role}' is not permitted to use tool '{tool}'")


class RbacPolicy:
    def __init__(self, model_path: Path, policy_path: Path) -> None:
        self._enforcer = casbin.Enforcer(str(model_path), str(policy_path))

    @classmethod
    def load(
        cls,
        model_path: Path = DEFAULT_RBAC_MODEL_PATH,
        policy_path: Path = DEFAULT_RBAC_POLICY_PATH,
    ) -> "RbacPolicy":
        return cls(model_path, policy_path)

    def is_allowed(self, role: str, tool: str) -> bool:
        return self._enforcer.enforce(role, tool)

    def check(self, role: str, tool: str) -> None:
        if not self.is_allowed(role, tool):
            raise RbacDenial(role=role, tool=tool)
