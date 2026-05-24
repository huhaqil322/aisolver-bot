from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional


def parse_latex(text: str) -> list[str]:
    inline = re.findall(r"\$([^$]+)\$", text)
    display = re.findall(r"\$\$([^$]+)\$\$", text)
    return display + inline


def strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    return text


def truncate_text(text: str, max_length: int = 4000, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)].rstrip() + suffix


def format_number(num: float, decimals: int = 2) -> str:
    if num >= 1_000_000:
        return f"{num / 1_000_000:.{decimals}f}M"
    if num >= 1_000:
        return f"{num / 1_000:.{decimals}f}K"
    return f"{num:.{decimals}f}"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data
