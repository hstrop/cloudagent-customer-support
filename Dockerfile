FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/src
EXPOSE 8020
CMD ["uvicorn", "cloudagent.api:app", "--host", "0.0.0.0", "--port", "8020"]
