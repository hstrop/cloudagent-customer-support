# CloudAgent Customer Support

CloudAgent is an offline-first customer support assistant prototype. It turns the core customer-service workflow into an observable backend: intent classification → knowledge retrieval → policy gate → grounded reply or human handoff.

## Global AI/LLM Internship Portfolio

This project demonstrates product-minded agent engineering rather than a black-box chat wrapper. The API returns evidence, policy decisions, handoff state, and trace steps so the behavior can be evaluated and explained.

**Engineering signals:** Python · FastAPI · evidence-grounded support · policy gates · human handoff · session lifecycle · responsive browser UI.

The repository includes a deterministic offline knowledge base. It does not claim live customer data, real-time order access, or production SLA. A hosted LLM, CRM, ticketing system, and vector database can be added behind the existing service boundary.

## Features

- Chinese support intents for refund, delivery, account safety, and general service questions.
- Evidence cards with source IDs and match scores.
- Explicit sensitive-data policy gate for passwords, verification codes, card details, and identity information.
- Human-handoff state for sensitive or unsupported requests.
- Session reset endpoint and a compact browser workbench with workflow visualization.
- FastAPI docs at `http://127.0.0.1:8020/docs`.

## Quick start

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\run_demo.ps1
```

Open `http://127.0.0.1:8020/`. For a dependency-light local run, use the same Python environment as the other portfolio projects.

## Verification

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
```

The suite covers grounded answers, policy blocking, unknown-intent handoff, session reset, API validation, and health behavior.

## Container deployment

```powershell
docker build -t cloudagent-customer-support .
docker run --rm -p 8020:8020 cloudagent-customer-support
```

Open `http://127.0.0.1:8020/`. The image contains only the deterministic offline fixture and no customer data.
