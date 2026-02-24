"""Docker-based sandbox for isolated code execution."""

import docker
import requests.exceptions

SANDBOX_IMAGE = "python:3.12-slim"
SANDBOX_TIMEOUT = 10          # seconds
SANDBOX_MEMORY = "128m"
SANDBOX_NANO_CPUS = 500_000_000  # 0.5 CPUs


class SandboxError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def run_python(code: str, timeout: int = SANDBOX_TIMEOUT) -> dict:
    """Execute Python code in an isolated Docker container.

    Constraints applied:
    - No network access (network_mode=none)
    - 128 MiB memory limit
    - 0.5 CPU quota
    - Hard timeout (container is killed if it exceeds it)

    Returns a dict with ``stdout``, ``stderr``, and ``exit_code``.
    Raises ``SandboxError`` on timeout or Docker failure.
    """
    try:
        client = docker.from_env()
    except docker.errors.DockerException as exc:
        raise SandboxError(f"Docker unavailable: {exc}") from exc

    container = client.containers.run(
        image=SANDBOX_IMAGE,
        command=["python", "-c", code],
        network_mode="none",
        mem_limit=SANDBOX_MEMORY,
        nano_cpus=SANDBOX_NANO_CPUS,
        detach=True,
        stdout=True,
        stderr=True,
    )
    try:
        status = container.wait(timeout=timeout)
        exit_code = status["StatusCode"]
        stdout = container.logs(stdout=True, stderr=False).decode()
        stderr = container.logs(stdout=False, stderr=True).decode()
        return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}
    except requests.exceptions.ReadTimeout:
        container.kill()
        raise SandboxError(f"Code execution timed out after {timeout}s") from None
    except Exception as exc:
        raise SandboxError(str(exc)) from exc
    finally:
        container.remove(force=True)
