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

### 2026-04-03（固定汇率 / 人民币固定档）
- **结果区「使用汇率」**：只要货币对涉及 CNY，展示统一为「1 非 CNY = x CNY」形式（`templates/index.html` 中 `formatRateLineForCNY`）。
- **默认固定汇率快照**：`localStorage` 键 `weather_fx_fixed_prefs_v1` 保存「汇率 + Base/Target + 是否勾选固定汇率」；仅用户点击 💾 写入，网络换算不覆盖；启动时整单恢复。
- **人民币多档预设**：键 `weather_fx_cny_fixed_presets_v1`，按外币存「1 外币 = x CNY」；在「外币 ↔ CNY」货币对下 💾 时写入对应档位。
- **快捷开关（标签）**：目标币种行右侧展示六个一字档（美/俄/土/伊/日/欧，对应 USD、RUB、TRY、IQD、JPY、EUR）；仅当前为「该外币与 CNY」换算时可点选启用已存汇价，其余灰色禁用；与「使用固定汇率」勾选及输入框联动。
- **布局迭代**：移除原单字蓝框标签；去掉「人民币固定档」标题与说明小字，仅保留开关行；开关容器与目标币种输入框同边框样式并垂直对齐；六档单行均分排列。

### 2026-04-04（固定汇率方向）
- **修复**：固定汇率按「1 Base = rate × Target」计算；原先在 USD/CNY 存 7.2 后若改为 CNY/USD，框内仍为 7.2 会导致「1000 CNY = 7200 USD」等错误。
- **行为**：记录上一组有效 Base/Target；当新组合与上一组**互为对调**（同一对币种互换方向）时，自动对 rate **取倒数**；**⇅ 互换**与**下拉修改币种**均走同一套 `updateFixedNote()` 逻辑，无需重复操作。

