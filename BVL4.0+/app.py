"""
app.py — Entry point dell'app Beach Volley Tournament Manager
Avvia con: streamlit run app.py
"""
import streamlit as st
from data_manager import load_state, save_state
from ui_components import inject_css, render_header
from fase_setup import render_setup
from fase_gironi import render_gironi
from fase_eliminazione import render_eliminazione
from fase_proclamazione import render_proclamazione, render_ranking_globale, render_schede_carriera

# ─── CONFIGURAZIONE PAGINA ───────────────────────────────────────────────────

st.set_page_config(
    page_title="🏐 Beach Volley Tournament",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CARICAMENTO STATO (prima del CSS per usare theme) ──────────────────────
if "state" not in st.session_state:
    st.session_state.state = load_state()

state = st.session_state.state

# ─── CSS GLOBALE (tema da state, senza crash) ───────────────────────────────
theme = state.get("theme", "dazn_dark")
inject_css(theme)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px">
        <div style="font-size:2.5rem">🏐</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;
            font-weight:800;letter-spacing:2px;text-transform:uppercase">
            Beach Volley<br>Tournament
        </div>
        <div style="color:#e8002d;font-size:0.7rem;letter-spacing:3px;margin-top:4px">
            MANAGER PRO
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigazione rapida
    st.markdown("**🗺️ Navigazione**")
    
    fase_corrente = state["fase"]
    fasi_disponibili = []
    ordine = ["setup", "gironi", "eliminazione", "proclamazione"]
    idx_attuale = ordine.index(fase_corrente)
    
    for i, (k, label) in enumerate([
        ("setup", "⚙️ Setup"),
        ("gironi", "🔵 Gironi"),
        ("eliminazione", "⚡ Eliminazione"),
        ("proclamazione", "🏆 Proclamazione"),
    ]):
        disabled = i > idx_attuale
        if i <= idx_attuale:
            if st.button(label, key=f"nav_{k}", use_container_width=True,
                        type="primary" if k == fase_corrente else "secondary"):
                state["fase"] = k
                save_state(state)
                st.rerun()
        else:
            st.button(label, key=f"nav_{k}", use_container_width=True, disabled=True)
    
    st.divider()
    
    # Info torneo
    if state["torneo"]["nome"]:
        st.markdown("**📋 Torneo Attivo**")
        st.markdown(f"**{state['torneo']['nome']}**")
        st.caption(f"📅 {state['torneo']['data']}")
        st.caption(f"📊 {state['torneo']['tipo_tabellone']}")
        st.caption(f"🏐 {state['torneo']['formato_set']} · Max {state['torneo']['punteggio_max']} pt")
        st.caption(f"👥 {len(state['squadre'])} squadre")
        
        st.divider()
    
    # Ranking rapido in sidebar
    atleti_con_dati = [a for a in state["atleti"] if a["stats"]["tornei"] > 0]
    if atleti_con_dati:
        st.markdown("**🏅 Top Atleti**")
        atleti_sorted = sorted(atleti_con_dati, key=lambda a: -(
            sum({1:100,2:70,3:50}.get(p,20) for _,p in a["stats"]["storico_posizioni"])
        ))
        for i, a in enumerate(atleti_sorted[:5]):
            medals = {0:"🥇",1:"🥈",2:"🥉"}
            icon = medals.get(i,"•")
            st.caption(f"{icon} {a['nome']}")
        
        st.divider()
    
    # Salvataggio / Reset
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salva", use_container_width=True):
            save_state(state)
            st.success("Salvato!")
    with col2:
        with st.expander("⚠️"):
            if st.button("🔴 RESET", use_container_width=True):
                from data_manager import empty_state
                st.session_state.state = empty_state()
                save_state(st.session_state.state)
                for k in list(st.session_state.keys()):
                    if k != "state":
                        del st.session_state[k]
                st.rerun()
    
    # Tema (solo salvataggio in state + rerun, niente set_page_config dopo)
    st.markdown("**🎨 Tema**")
    theme_opts = ["dazn_dark", "dazn_red", "dark_blue"]
    theme_labels = {"dazn_dark": "Scuro DAZN", "dazn_red": "Rosso DAZN", "dark_blue": "Blu scuro"}
    idx = theme_opts.index(state.get("theme", "dazn_dark")) if state.get("theme") in theme_opts else 0
    new_theme = st.selectbox(
        "Stile interfaccia",
        options=theme_opts,
        format_func=lambda x: theme_labels.get(x, x),
        index=idx,
        key="sidebar_theme"
    )
    if new_theme != state.get("theme"):
        state["theme"] = new_theme
        save_state(state)
        st.rerun()

    st.caption("Dati salvati su: beach_volley_data.json")


# ─── HEADER PRINCIPALE ───────────────────────────────────────────────────────
render_header(state)

# ─── ROUTING FASI ────────────────────────────────────────────────────────────
fase = state["fase"]

if fase == "setup":
    render_setup(state)

elif fase == "gironi":
    render_gironi(state)

elif fase == "eliminazione":
    render_eliminazione(state)

elif fase == "proclamazione":
    render_proclamazione(state)

else:
    st.error(f"Fase sconosciuta: {fase}")

# ─── AUTOSAVE SILENZIOSO ─────────────────────────────────────────────────────
# Salva ad ogni ciclo per garantire persistenza
save_state(state)
