from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any


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
    return datetime.now(UTC)


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


def sanitize_for_markdown(text: str) -> str:
    return text.replace("_", "＿")


_LATEX_UNICODE: dict[str, str] = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ",
    r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ", r"\mu": "μ",
    r"\nu": "ν", r"\xi": "ξ", r"\pi": "π", r"\rho": "ρ",
    r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ", r"\phi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Alpha": "Α", r"\Beta": "Β", r"\Gamma": "Γ", r"\Delta": "Δ",
    r"\Theta": "Θ", r"\Lambda": "Λ", r"\Xi": "Ξ", r"\Pi": "Π",
    r"\Sigma": "Σ", r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
    r"\sum": "Σ", r"\prod": "∏", r"\int": "∫", r"\iint": "∬",
    r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\geq": "≥", r"\leq": "≤", r"\neq": "≠", r"\approx": "≈",
    r"\equiv": "≡", r"\propto": "∝", r"\times": "×", r"\div": "÷",
    r"\pm": "±", r"\mp": "∓", r"\cdot": "·", r"\circ": "∘",
    r"\rightarrow": "→", r"\Rightarrow": "⇒", r"\leftarrow": "←",
    r"\Leftarrow": "⇐", r"\leftrightarrow": "↔", r"\mapsto": "↦",
    r"\forall": "∀", r"\exists": "∃", r"\emptyset": "∅",
    r"\in": "∈", r"\notin": "∉", r"\subset": "⊂", r"\supset": "⊃",
    r"\subseteq": "⊆", r"\supseteq": "⊇", r"\cup": "∪", r"\cap": "∩",
    r"\setminus": "∖", r"\oplus": "⊕", r"\otimes": "⊗",
    r"\bot": "⊥", r"\angle": "∠", r"\triangle": "△",
    r"\sqrt": "√", r"\sin": "sin", r"\cos": "cos", r"\tan": "tan",
    r"\log": "log", r"\ln": "ln", r"\lim": "lim",
}


def clean_latex_for_telegram(text: str) -> str:
    text = text.replace("{,}", ",")

    text = re.sub(r"\$\$", "", text)
    text = re.sub(r"\\\[|\\\]", "", text)
    text = re.sub(r"\\\(|\\\)", "", text)
    text = re.sub(r"\$(.+?)\$", r"\1", text)

    text = re.sub(r"\\boxed\{([^}]*)\}", r"**\1**", text)
    text = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", text)
    text = re.sub(r"\\binom\{([^}]*)\}\{([^}]*)\}", r"C(\1,\2)", text)
    text = re.sub(r"\\text\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", text)
    text = re.sub(r"\\underline\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\displaystyle", "", text)
    text = re.sub(r"\\[,;:!]", " ", text)
    text = re.sub(r"\\quad|\\qquad", "  ", text)
    text = re.sub(r"\\ ", " ", text)

    for cmd, unicode_char in _LATEX_UNICODE.items():
        text = text.replace(cmd, unicode_char)

    text = re.sub(r"\\([{}])", r"\1", text)

    return text
