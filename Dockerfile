FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
COPY policy.json model.conf rbac_policy.csv ./

RUN uv pip install --system -e ".[standard]" 2>/dev/null || uv pip install --system -e . && \
    uv pip install --system fastapi "uvicorn[standard]"

EXPOSE 8003

CMD ["uvicorn", "guardflow.server:app", "--host", "0.0.0.0", "--port", "8003"]
