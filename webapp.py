from datetime import datetime
from pathlib import Path
from typing import Dict

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


FX_URL = "https://open.er-api.com/v6/latest"

# 银行偏移系数（演示用途）。真实生产建议接入各银行官方牌价接口。
BANK_RATE_MULTIPLIER: Dict[str, float] = {
    "中国银行": 1.0000,
    "中国农业银行": 0.9995,
    "中国工商银行": 1.0003,
    "中国建设银行": 1.0001,
}


class ConvertRequest(BaseModel):
    base: str = Field(..., min_length=3, max_length=3)
    target: str = Field(..., min_length=3, max_length=3)
    amount: float = Field(..., gt=0)
    use_fixed_rate: bool = False
    fixed_rate: float = Field(0, ge=0)
    bank_source: str = "中国银行"


app = FastAPI(title="Weather-FX Web App")
app.mount("/static", StaticFiles(directory="."), name="static")
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = BASE_DIR / "templates" / "index.html"


def fetch_market_rate(base: str, target: str) -> float:
    resp = requests.get(f"{FX_URL}/{base}", timeout=12)
    resp.raise_for_status()
    data = resp.json()
    rate = data.get("rates", {}).get(target)
    if rate is None:
        raise HTTPException(status_code=400, detail=f"不支持币种对：{base}->{target}")
    return float(rate)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/api/convert")
def convert(payload: ConvertRequest):
    base = payload.base.upper().strip()
    target = payload.target.upper().strip()
    amount = float(payload.amount)

    if base == target:
        raise HTTPException(status_code=400, detail="待计算币种和目标币种不能相同。")

    if payload.use_fixed_rate:
        if payload.fixed_rate <= 0:
            raise HTTPException(status_code=400, detail="固定汇率必须大于 0。")
        rate = float(payload.fixed_rate)
        mode = "固定汇率"
        source = "手工固定汇率"
    else:
        market_rate = fetch_market_rate(base, target)
        bank = payload.bank_source.strip()
        if bank not in BANK_RATE_MULTIPLIER:
            raise HTTPException(status_code=400, detail="不支持的银行来源。")
        rate = market_rate * BANK_RATE_MULTIPLIER[bank]
        mode = "网络汇率"
        source = bank

    converted = round(amount * rate, 6)
    return {
        "ok": True,
        "mode": mode,
        "source": source,
        "base": base,
        "target": target,
        "amount": amount,
        "rate": round(rate, 6),
        "converted": converted,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "银行来源为演示口径，生产请接入银行官方接口。",
    }
