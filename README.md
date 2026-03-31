# weather-fx-agent

A simple FX converter web app with optional fixed-rate mode and bank source selection.

## Features
- Currency conversion using live market rate
- Optional fixed-rate conversion
- Bank source selector (for display and adjustment logic)
- Web UI for colleagues

## Run locally
```powershell
cd E:\ai\weather-fx-agent
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
start_web.bat
```

Open:
- `http://127.0.0.1:8000`

## API
Endpoint:
- `POST /api/convert`

Example payload:
```json
{
  "base": "USD",
  "target": "CNY",
  "amount": 1000,
  "use_fixed_rate": false,
  "fixed_rate": 0,
  "bank_source": "中国银行"
}
```
