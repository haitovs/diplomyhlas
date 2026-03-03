"""
Internationalization (i18n) helper for the dashboard.
Loads JSON locale files and provides a t(key) function.
"""

import json
import streamlit as st
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent / "locales"
_CACHE: dict = {}

SUPPORTED_LANGS = {"en": "English", "tk": "Türkmen"}
DEFAULT_LANG = "en"


def _load_locale(lang: str) -> dict:
    """Load and cache a locale JSON file."""
    if lang in _CACHE:
        return _CACHE[lang]

    path = _LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = _LOCALES_DIR / f"{DEFAULT_LANG}.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _CACHE[lang] = data
    return data


def get_lang() -> str:
    """Return the currently selected language code."""
    return st.session_state.get("lang", DEFAULT_LANG)


def set_lang(lang: str):
    """Set the active language."""
    st.session_state["lang"] = lang


def t(key: str, **kwargs) -> str:
    """Translate a dot-separated key, e.g. t('home.hero_title').

    Supports {placeholder} interpolation via kwargs:
        t('live.capturing_on', interface='eth0')
    Falls back to English, then to the raw key.
    """
    lang = get_lang()
    data = _load_locale(lang)

    parts = key.split(".")
    value = data
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            # Fallback to English
            if lang != DEFAULT_LANG:
                en_data = _load_locale(DEFAULT_LANG)
                val = en_data
                for p in parts:
                    if isinstance(val, dict) and p in val:
                        val = val[p]
                    else:
                        return key
                if isinstance(val, str):
                    return val.format(**kwargs) if kwargs else val
            return key

    if isinstance(value, str):
        return value.format(**kwargs) if kwargs else value
    return key
