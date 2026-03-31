# weather-fx-agent

一个支持天气与汇率查询的 Agent 项目，并提供可分享的网页界面。

## 功能
- 天气查询（Open-Meteo）
- 汇率查询（open.er-api）
- 网页汇率换算（固定汇率 / 网络汇率来源）

## 本地运行（网页）
```powershell
cd E:\ai\weather-fx-agent
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
start_web.bat
```

启动后访问：
- `http://127.0.0.1:8000`

## API 调用
`POST /api/convert`

示例请求体：
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
