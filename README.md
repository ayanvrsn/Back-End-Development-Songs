# Back-End-Development-Songs

IBM Back-End Development Capstone implementation based on the official IBM Skills Network starter template. Original starter instructions are preserved in `IBM_STARTER_README.md`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --port 5001
```

Songs uses MongoDB (`MONGODB_URI` or the `MONGODB_SERVICE`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD` variables). Use `MONGODB_MOCK=1 pytest -v` only for an explicit isolated local test; this is not proof of a deployed MongoDB service.

## Evidence and deployment status

`evidence/` contains actual captured command output from local verification. Local test success does not assert IBM Cloud deployment. Docker and Kubernetes files provide a deployment configuration; cloud rollout must be executed and checked separately. No cloud endpoint or screenshot is fabricated.
