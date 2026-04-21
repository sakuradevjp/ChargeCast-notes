#!/usr/bin/env python3
"""Generate per-language index.html files from _template.html and langs.json.

Run from repo root:
    python build.py
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).parent
TEMPLATE = (ROOT / "_template.html").read_text(encoding="utf-8")
LANGS = json.loads((ROOT / "langs.json").read_text(encoding="utf-8"))

# Native display name per locale (used in language switcher)
NATIVE_NAMES = {
    "en": "English",
    "ja": "日本語",
    "zh-Hans": "简体中文",
    "zh-Hant": "繁體中文",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "sv": "Svenska",
    "ru": "Русский",
    "uk": "Українська",
    "tr": "Türkçe",
    "ar": "العربية",
    "hi": "हिन्दी",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "id": "Bahasa Indonesia",
    "ms": "Bahasa Melayu",
}

RTL_LANGS = {"ar"}

# The display order in the switcher (English first, then Japanese, then the rest alphabetical by native name)
DISPLAY_ORDER = [
    "en", "ja",
    "zh-Hans", "zh-Hant", "ko",
    "es", "fr", "de", "it", "pt", "nl", "pl", "sv",
    "ru", "uk",
    "tr", "ar", "hi", "th", "vi", "id", "ms",
]


def path_for(lang: str) -> str:
    return "" if lang == "en" else f"{lang}/"


def relative_to_root(lang: str) -> str:
    # from a page's directory, how do we get back to repo root?
    return "" if lang == "en" else "../"


def build_switcher(current_lang: str) -> str:
    base = relative_to_root(current_lang)
    links = []
    for code in DISPLAY_ORDER:
        if code not in LANGS:
            continue
        name = NATIVE_NAMES[code]
        href = base + path_for(code)
        if code == current_lang:
            links.append(f'<a href="{href}" aria-current="page"><strong>{name}</strong></a>')
        else:
            links.append(f'<a href="{href}" hreflang="{code}">{name}</a>')
    return " · ".join(links)


def build_hreflang_links(current_lang: str) -> str:
    base_url = "https://sakuradevjp.github.io/ChargeCast-notes/"
    out = []
    for code in DISPLAY_ORDER:
        if code not in LANGS:
            continue
        href = base_url + path_for(code)
        out.append(f'<link rel="alternate" hreflang="{code}" href="{href}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{base_url}">')
    return "\n".join(out)


def render(lang: str, strings: dict) -> str:
    ctx = dict(strings)
    ctx["lang"] = lang
    ctx["dirAttr"] = ' dir="rtl"' if lang in RTL_LANGS else ""
    ctx["assetsPath"] = relative_to_root(lang) + "assets/"
    ctx["langSwitcher"] = build_switcher(lang)
    ctx["hreflangLinks"] = build_hreflang_links(lang)

    def replace(match):
        key = match.group(1)
        if key not in ctx:
            print(f"[WARN] missing key '{key}' for lang '{lang}'", file=sys.stderr)
            return match.group(0)
        return ctx[key]

    return re.sub(r"\{\{(\w+)\}\}", replace, TEMPLATE)


def main() -> int:
    written = 0
    for lang, strings in LANGS.items():
        out_dir = ROOT if lang == "en" else ROOT / lang
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "index.html"
        out_path.write_text(render(lang, strings), encoding="utf-8")
        written += 1
        print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"\ntotal: {written} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
