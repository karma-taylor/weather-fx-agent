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

Traffic stats:
- `GET /api/visits/today` (today requests, unique IPs, IP counts)
- `GET /admin/visits` (simple admin dashboard page)
- `POST /api/visits/export/today` generate today's Excel file
- `GET /api/visits/export/{date_utc}` download Excel for a date (e.g. 2026-03-31)

Optional admin protection:
- Set env var `ADMIN_TOKEN=your_secret`
- Then access:
  - `/admin/visits?token=your_secret`
  - `/api/visits/today?token=your_secret`

Daily Excel schedule:
- A background scheduler runs every day (UTC by default) and exports yesterday's file.
- Env vars:
  - `SCHEDULER_TIMEZONE` (default `UTC`)
  - `DAILY_EXPORT_HOUR` (default `23`)
  - `DAILY_EXPORT_MINUTE` (default `55`)
  - `MONTHLY_EXPORT_HOUR` (default `0`)
  - `MONTHLY_EXPORT_MINUTE` (default `10`)

Export directory:
- Windows local default: `E:\ai\weather-fx-agent\shuju`
- Override by env: `EXPORT_ROOT_DIR=/your/path`

Monthly Excel:
- Auto: run at day 1 each month, export previous month file
- Manual create: `POST /api/visits/export/monthly/{YYYY-MM}`
- Download: `GET /api/visits/export/monthly/{YYYY-MM}/download`
