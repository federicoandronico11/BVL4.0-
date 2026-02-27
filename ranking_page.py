"""
ranking_page.py — Pagine ranking e profili come moduli riutilizzabili
"""
import streamlit as st
from fase_proclamazione import render_ranking_globale, render_schede_carriera


def render_ranking_page(state):
    """Vista standalone del Ranking Globale."""
    st.markdown("## 📊 Ranking Globale Atleti")
    render_ranking_globale(state)


def render_profili_page(state):
    """Vista standalone dei Profili Giocatori (carte carriera)."""
    st.markdown("## 👤 Profili Giocatori — Carte Carriera")
    render_schede_carriera(state)
