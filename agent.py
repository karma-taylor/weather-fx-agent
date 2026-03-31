import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    RateLimitError,
)


SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"

WEATHER_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
FX_URL = "https://open.er-api.com/v6/latest"


def get_weather(city: str) -> Dict[str, Any]:
    geo_resp = requests.get(
        WEATHER_GEOCODE_URL,
        params={"name": city, "count": 1, "language": "zh", "format": "json"},
        timeout=15,
    )
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        return {"ok": False, "error": f"没有找到城市: {city}"}

    place = geo_data["results"][0]
    lat = place["latitude"]
    lon = place["longitude"]

    weather_resp = requests.get(
        WEATHER_FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "weather_code",
            ],
            "timezone": "auto",
        },
        timeout=15,
    )
    weather_resp.raise_for_status()
    weather_data = weather_resp.json()

    return {
        "ok": True,
        "city": place.get("name"),
        "country": place.get("country"),
        "admin1": place.get("admin1"),
        "latitude": lat,
        "longitude": lon,
        "current": weather_data.get("current", {}),
    }


def get_exchange_rate(base: str, target: str, amount: float = 1.0) -> Dict[str, Any]:
    base = base.upper().strip()
    target = target.upper().strip()

    fx_resp = requests.get(f"{FX_URL}/{base}", timeout=15)
    fx_resp.raise_for_status()
    data = fx_resp.json()

    rate = data.get("rates", {}).get(target)
    if rate is None:
        return {"ok": False, "error": f"暂不支持汇率查询: {base} -> {target}"}

    return {
        "ok": True,
        "base": data.get("base_code", base),
        "target": target,
        "amount": amount,
        "converted": round(float(rate) * float(amount), 6),
        "rate": rate,
        "date": data.get("time_last_update_utc"),
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询城市当前天气，返回温度、湿度、风速等信息。",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名，如北京、Shanghai、Baghdad"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "查询两种货币之间的实时汇率与换算值。",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {"type": "string", "description": "基准货币代码，如 CNY"},
                    "target": {"type": "string", "description": "目标货币代码，如 IQD"},
                    "amount": {"type": "number", "description": "兑换金额，默认 1"},
                },
                "required": ["base", "target"],
            },
        },
    },
]


def _normalize_api_key(raw: Optional[str]) -> str:
    if not raw:
        return ""
    key = raw.strip()
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1].strip()
    return key


def _mask_key(key: str) -> str:
    if len(key) <= 12:
        return "(长度过短或已隐藏)"
    return f"{key[:7]}...{key[-4:]}（共 {len(key)} 个字符）"


def _looks_like_placeholder_key(key: str) -> bool:
    """检测是否仍使用 .env.example 里的示例占位符，或明显未粘贴完整 Key。"""
    k = key.strip().lower()
    if not k:
        return True
    if k in ("your_api_key_here", "changeme", "placeholder", "sk-xxxxx"):
        return True
    if "your_api_key" in k:
        return True
    # OpenAI 官方密钥以 sk- 开头且很长；过短多半是占位符或复制不全
    if k.startswith("sk-") and len(key) < 40:
        return True
    return False


def _ollama_api_root(base_url: str) -> Optional[str]:
    u = base_url.strip().rstrip("/")
    if "127.0.0.1:11434" in u or "localhost:11434" in u:
        return u.rsplit("/v1", 1)[0] if u.endswith("/v1") else u
    return None


def _ollama_installed_model_names(api_root: str) -> Optional[List[str]]:
    try:
        resp = requests.get(f"{api_root}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return None


def _warn_if_ollama_model_missing(base_url: str, model: str) -> None:
    root = _ollama_api_root(base_url)
    if not root:
        return
    names = _ollama_installed_model_names(root)
    if names is None:
        print("[Ollama] 无法连接本机 Ollama（请确认 Ollama 已启动）。\n")
        return
    if not names:
        print(
            "[Ollama] 尚未下载任何模型。请在 PowerShell 执行例如：\n"
            "  ollama pull llama3.2:3b\n"
            "然后把 .env 里 MODEL= 写成与 `ollama list` 第一列完全一致的名字（如 llama3.2:3b）。\n"
        )
        return
    if model in names:
        return
    print(
        f"[Ollama] .env 里的 MODEL={model!r} 在本机不存在。\n"
        f"本机已有模型：{', '.join(names)}\n"
        "请把 MODEL= 改成上面某一行的完整名称（区分 llama3.2 与 llama3.2:3b）。\n"
    )


def _print_model_not_found_help(model: str, base_url: str) -> None:
    print(
        f"\n【模型不存在 404】当前请求的 model={model!r} 在服务端找不到。\n"
        "若使用 Ollama：MODEL 必须与 `ollama list` 第一列完全一致，"
        "例如下载的是 llama3.2:3b 就要写 llama3.2:3b，不能只写 llama3.2。\n"
        "在 PowerShell 运行：ollama list   再改 .env 后重新启动。\n"
    )
    _warn_if_ollama_model_missing(base_url, model)


def _print_quota_help(exc: Optional[Any] = None) -> None:
    detail = ""
    if exc is not None:
        err_str = str(exc).lower()
        if "insufficient_quota" in err_str or "quota" in err_str:
            detail = "（当前为：账户额度不足 / 未绑定付费）\n"
    print(
        "\n【额度不足 429】" + detail
        + "含义：OpenAI 账号下没有可用额度（免费试用用完、或未绑支付方式、或余额为 0）。\n"
        "这与程序无关，需要你在 OpenAI 侧处理：\n"
        "1) 打开 https://platform.openai.com/account/billing 查看余额、绑定银行卡/充值\n"
        "2) 查看 Usage / Limits 是否达到上限\n"
        "3) 若暂不想付费：换用支持免费额度的兼容接口，并把 .env 里 OPENAI_BASE_URL、MODEL 改成该服务商文档要求\n"
    )


def _print_auth_help() -> None:
    print(
        "\n【API Key 无效 (401)】请检查：\n"
        "1) 确认配置文件路径为（与 agent.py 同目录）：\n"
        f"   {ENV_FILE}\n"
        "   文件名必须是 .env，不能是 .env.txt（可在资源管理器勾选「显示文件扩展名」核对）。\n"
        "2) 在 https://platform.openai.com/account/api-keys 创建新 Key，整行粘贴到：OPENAI_API_KEY=sk-...\n"
        "3) 若曾设置过系统环境变量 OPENAI_API_KEY，可能覆盖 .env；本程序已优先读取上述 .env，仍 401 请换新 Key 或核对 BASE_URL。\n"
        "4) 国内/第三方 Key：必须把 OPENAI_BASE_URL、MODEL 改成该服务商提供的值。\n"
    )


def _print_startup_config(api_key: str, base_url: str, model: str) -> None:
    exists = ENV_FILE.is_file()
    print(f"[配置] 使用的 .env 路径: {ENV_FILE}")
    print(f"[配置] 文件是否存在: {'是' if exists else '否（程序读不到 Key，请把 .env 放在本目录）'}")
    print(f"[配置] OPENAI_BASE_URL = {base_url}")
    print(f"[配置] MODEL = {model}")
    print(f"[配置] OPENAI_API_KEY = {_mask_key(api_key)}")
    if not exists:
        print("[提示] 若你从别处复制了 Key，请在本项目文件夹内新建 .env，不要放在桌面其它目录。")
    print()


def run() -> None:
    # 始终从「本脚本所在目录」加载 .env，避免从其它目录启动时读不到配置
    # override=True：以 .env 为准，避免系统里残留的旧 OPENAI_API_KEY 覆盖你刚填的值
    load_dotenv(ENV_FILE, override=True)

    api_key = _normalize_api_key(os.getenv("OPENAI_API_KEY"))
    base_url = (os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").strip().rstrip("/")
    model = os.getenv("MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError(
            f"未读取到 OPENAI_API_KEY。\n"
            f"请在以下路径创建或编辑 .env 文件（与 agent.py 同目录）：\n{ENV_FILE}"
        )

    _print_startup_config(api_key, base_url, model)

    _warn_if_ollama_model_missing(base_url, model)

    if _looks_like_placeholder_key(api_key):
        print(
            "【错误】当前 OPENAI_API_KEY 仍是示例占位符或未粘贴完整。\n"
            "请用记事本打开：\n"
            f"  {ENV_FILE}\n"
            "把 OPENAI_API_KEY= 后面改成官网「完整复制」的一整串（以 sk- 开头，长度通常几十到一百多字符），\n"
            "不要保留 your_api_key_here 这类示例文字。保存后重新运行。\n"
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        client.models.list()
    except AuthenticationError:
        _print_auth_help()
        sys.exit(1)
    except RateLimitError as exc:
        _print_quota_help(exc)
        sys.exit(1)
    except APIConnectionError as exc:
        print(f"\n无法连接 API 服务：{exc}\n请检查网络或 OPENAI_BASE_URL。\n")
        sys.exit(1)
    except Exception:
        pass

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个实用型中文助手。"
                "当用户询问天气或汇率时，必须优先调用工具获取实时数据，再用自然语言回答。"
                "回答要简洁，包含关键数字和单位。"
            ),
        }
    ]

    print("Weather/FX Agent 已启动，输入 exit 退出。")
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("已退出。")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.2,
                )
            except AuthenticationError:
                _print_auth_help()
                return
            except RateLimitError as exc:
                _print_quota_help(exc)
                messages.pop()
                break
            except NotFoundError:
                _print_model_not_found_help(model, base_url)
                messages.pop()
                break
            except APIConnectionError as exc:
                print(f"\n网络或接口异常：{exc}\n")
                messages.pop()
                break

            msg = response.choices[0].message

            if not msg.tool_calls:
                final_text = msg.content or "我暂时没有得到结果。"
                print(f"\nAgent: {final_text}")
                messages.append({"role": "assistant", "content": final_text})
                break

            messages.append(msg.model_dump())

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")

                try:
                    if name == "get_weather":
                        result = get_weather(**args)
                    elif name == "get_exchange_rate":
                        result = get_exchange_rate(**args)
                    else:
                        result = {"ok": False, "error": f"未知工具: {name}"}
                except Exception as exc:
                    result = {"ok": False, "error": str(exc)}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )


if __name__ == "__main__":
    run()
