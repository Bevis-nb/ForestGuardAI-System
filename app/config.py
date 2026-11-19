"""用户偏好配置读写（主题色、信息密度、刷新频率、告警阈值等）。"""
from __future__ import annotations

import json
import os

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "app_config.json"
)

DEFAULTS: dict = {
    "accent": "森林绿",
    "compact": False,
    "animations": True,
    "refresh": 1,
    "th_temp": 65,
    "th_smoke": 180,
    "th_risk": 80,
    "silent": False,
    "stream": True,
}


def load() -> dict:
    data = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data.update(json.load(f) or {})
    except (OSError, ValueError):
        pass
    return data


def save(data: dict) -> None:
    payload = dict(DEFAULTS)
    payload.update({k: v for k, v in data.items() if k in DEFAULTS})
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass
