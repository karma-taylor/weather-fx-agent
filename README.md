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

## Update Log

### 2026-04-01
- Added client-side conversion history panel (`localStorage`) with a toggle switch.
- Added history clear action and responsive two-pane layout (stacks on small screens).
- Added no-cache headers for `/` in `webapp.py` to reduce stale HTML after deploy.

### 2026-04-01（下午）
- **图表**：结果区右侧为 SVG 平滑曲线图；坐标轴与刻度；鼠标靠近曲线时显示汇率并标橙色点；`GET /api/rates/history` 支持 7/30/90 天并按银行系数调整；历史源不可用时回退为当前价平线，避免 404 与图表卡住。
- **币种**：解析逻辑收紧（代码优先、`data-code` 绑定下拉选择）；移除易误判别名；修复不同币种被误判为“相同币种”的问题。
- **银行**：新增「威海银行」选项（前后端 `BANK_RATE_MULTIPLIER` 与下拉一致）。
- **布局与交互**：输出区 4:6 分栏、多层留白与紧凑高度多次迭代；标题与「立即换算」居中/加宽；删除页面底部冗长「支持币种」说明文案。
- **固定汇率**：本地默认固定汇率保存（💾）与读取。

### 2026-04-02
- **离线能力（MVP）**：新增 PWA（`manifest.json` + `sw.js`），支持离线打开页面；固定汇率改为本地计算，离线/在线均可用；网络汇率在离线时可回退最近一次实时缓存汇率进行计算。
- **结果区增强**：换算结果数字支持独立容器展示与一键复制；显示结果统一保留两位小数（第三位四舍五入）；结果文本行距与单行展示做了紧凑优化。
- **币种交互**：新增一键互换开关（Base/Target），互换后自动刷新汇率图与相关提示。
- **界面微调**：持续优化输出区边界可见性、左右容器对齐、图表缩放适配与间距细节。
