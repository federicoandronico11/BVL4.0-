"""
theme_manager.py — Gestione centralizzata dei temi UI
"""
import streamlit as st

THEMES = {
    "dazn_dark": {"label": "Scuro DAZN", "description": "Sfondo scuro, accento rosso."},
    "dazn_red": {"label": "Rosso DAZN", "description": "Rosso più intenso, look caldo."},
    "dark_blue": {"label": "Blu scuro", "description": "Blu notte con accenti azzurri."},
    "dark_green": {"label": "Verde scuro", "description": "Verde scuro con accenti lime."},
}


def render_theme_sidebar(state):
    """Controlli rapidi del tema in sidebar."""
    st.markdown("**🎨 Tema**")
    keys = list(THEMES.keys())
    current = state.get("theme", "dazn_dark")
    idx = keys.index(current) if current in keys else 0
    def _fmt(k: str) -> str:
        t = THEMES[k]
        return t["label"]
    new_theme = st.selectbox(
        "Stile interfaccia",
        options=keys,
        index=idx,
        format_func=_fmt,
        key="sidebar_theme_manager",
    )
    if new_theme != state.get("theme"):
        state["theme"] = new_theme
        st.success(f"Tema impostato su {THEMES[new_theme]['label']}.")
        return True
    return False


def render_theme_setup_section(state):
    """Sezione estesa per Setup → Personalizzazione tema (wrapper opzionale)."""
    st.markdown("Scegli l'aspetto dell'interfaccia. Il tema si applica a tutta l'app.")
    keys = list(THEMES.keys())
    current = state.get("theme", "dazn_dark")
    idx = keys.index(current) if current in keys else 0
    def _fmt(k: str) -> str:
        t = THEMES[k]
        return f"{t['label']} — {t['description']}"
    choice_idx = st.radio(
        "Tema interfaccia",
        range(len(keys)),
        index=idx,
        key="theme_radio_manager",
        format_func=lambda i: _fmt(keys[i]),
    )
    new_theme = keys[choice_idx]
    changed = False
    if new_theme != state.get("theme"):
        state["theme"] = new_theme
        st.success(f"Tema aggiornato: {THEMES[new_theme]['label']}.")
        changed = True
    return changed
