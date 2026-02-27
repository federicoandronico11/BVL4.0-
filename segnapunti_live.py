"""
segnapunti_live.py — Vista segnapunti live full-screen
"""
import streamlit as st
from ui_components import render_match_card


def render_segnapunti_live(state):
    """Vista dedicata solo al tabellone live (monitor, maxi-schermo)."""
    st.markdown("## 🧮 Segnapunti Live")
    st.caption("Panoramica in tempo reale di tutti i match in corso e conclusi.")

    gironi = state.get("gironi", [])
    bracket = state.get("bracket", [])

    if not gironi and not bracket:
        st.info("Nessuna partita generata. Completa il Setup e avvia il torneo.")
        return

    if gironi:
        st.markdown("### 🔵 Fase a Gironi")
        for g in gironi:
            st.markdown(f"#### {g['nome']}")
            for i, partita in enumerate(g.get("partite", [])):
                label = f"{g['nome']} · Match {i+1}"
                render_match_card(state, partita, label=label)

    if bracket:
        st.markdown("### ⚡ Fase Eliminazione")
        for i, partita in enumerate(bracket):
            label = partita.get("label_elim") or f"Playoff {i+1}"
            render_match_card(state, partita, label=label)
