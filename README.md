---
title: weather-fx-agent
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# weather-fx-agent

A simple FX converter web app built with FastAPI.

## Local run

```bash
pip install -r requirements.txt
uvicorn webapp:app --host 0.0.0.0 --port 7860
```

## API

POST `/api/convert`

```json
{
  "base": "USD",
  "target": "CNY",
  "amount": 1000,
  "use_fixed_rate": false,
  "fixed_rate": 0,
  "bank_source": "Bank of China"
}
```

Health check:
- `GET /healthz`
