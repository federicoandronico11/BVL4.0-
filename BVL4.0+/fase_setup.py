"""
fase_setup.py — Fase 1: Configurazione torneo e iscrizione squadre
"""
import streamlit as st
from data_manager import (
    new_atleta, new_squadra, get_atleta_by_id,
    save_state, genera_gironi
)


def render_setup(state):
    st.markdown("## ⚙️ Configurazione Torneo")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Impostazioni Generali")
        
        nome = st.text_input("Nome Torneo", value=state["torneo"]["nome"], placeholder="es. Summer Cup 2025")
        state["torneo"]["nome"] = nome
        
        tipo_opts = ["Gironi + Playoff", "Doppia Eliminazione", "Girone Unico"]
        tipo_idx = tipo_opts.index(state["torneo"].get("tipo_tabellone", "Gironi + Playoff")) if state["torneo"].get("tipo_tabellone") in tipo_opts else 0
        tipo = st.selectbox("Tipo Tabellone", tipo_opts, index=tipo_idx)
        state["torneo"]["tipo_tabellone"] = tipo
        
        state["torneo"]["girone_unico"] = (tipo == "Girone Unico")
        
        formato = st.selectbox("Formato Set", ["Set Unico", "Best of 3"],
                               index=["Set Unico", "Best of 3"].index(state["torneo"]["formato_set"]))
        state["torneo"]["formato_set"] = formato
        
        pmax = st.number_input("Punteggio Massimo Set", min_value=11, max_value=30,
                               value=state["torneo"]["punteggio_max"])
        state["torneo"]["punteggio_max"] = pmax
        
        data = st.date_input("Data Torneo")
        state["torneo"]["data"] = str(data)

        st.markdown("### 🔵 Gironi e passaggio")
        if not state["torneo"]["girone_unico"]:
            n_sq = len(state["squadre"])
            num_gironi = st.number_input("Numero gironi", min_value=2, max_value=8, value=state["torneo"].get("num_gironi", 2), key="num_gironi_setup")
            state["torneo"]["num_gironi"] = num_gironi
            if n_sq > 0:
                per_girone = n_sq // num_gironi if num_gironi else 0
                st.caption(f"Squadre per girone (auto): circa {per_girone}")
            passano = st.number_input("Squadre che passano per girone", min_value=1, max_value=4, value=state["torneo"].get("passano_per_girone", 2), key="passano_setup")
            state["torneo"]["passano_per_girone"] = passano
            criterio = st.radio("Criterio passaggio", ["classifica", "avulsa"], index=0 if state["torneo"].get("criterio_passaggio", "classifica") == "classifica" else 1, key="criterio_setup", horizontal=True)
            state["torneo"]["criterio_passaggio"] = criterio
        else:
            state["torneo"]["num_gironi"] = 1
            state["torneo"]["passano_per_girone"] = max(2, len(state["squadre"]) // 2) if state["squadre"] else 2
    
    with col2:
        st.markdown("### 👤 Gestione Atleti")
        _render_atleti_manager(state)
    
    st.divider()
    st.markdown("### 🏐 Iscrizione Squadre")
    _render_squadre_manager(state)
    
    st.divider()
    
    n_squadre = len(state["squadre"])
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        if n_squadre < 4:
            st.warning(f"⚠️ Servono almeno 4 squadre per avviare il torneo. ({n_squadre}/4 iscritte)")
        elif not nome:
            st.warning("⚠️ Inserisci il nome del torneo.")
        else:
            st.success(f"✅ {n_squadre} squadre iscritte. Pronto per avviare!")
    
    with col_b:
        if n_squadre >= 4 and nome:
            if st.button("🚀 AVVIA TORNEO →", use_container_width=True):
                ids = [s["id"] for s in state["squadre"]]
                num_gironi = state["torneo"].get("num_gironi", max(2, n_squadre // 4))
                girone_unico = state["torneo"].get("girone_unico", False)
                state["gironi"] = genera_gironi(ids, num_gironi=num_gironi, girone_unico=girone_unico)
                state["fase"] = "gironi"
                save_state(state)
                st.rerun()


def _render_atleti_manager(state):
    nomi_esistenti = [a["nome"] for a in state["atleti"]]
    
    with st.expander("➕ Aggiungi Nuovo Atleta", expanded=False):
        nuovo_nome = st.text_input("Nome Atleta", key="new_atleta_name", placeholder="Nome Cognome")
        if st.button("Aggiungi Atleta", key="btn_add_atleta"):
            if nuovo_nome.strip() and nuovo_nome.strip() not in nomi_esistenti:
                state["atleti"].append(new_atleta(nuovo_nome.strip()))
                save_state(state)
                st.success(f"✅ {nuovo_nome} aggiunto!")
                st.rerun()
            elif nuovo_nome.strip() in nomi_esistenti:
                st.error("Atleta già presente.")
            else:
                st.error("Inserisci un nome valido.")
    
    if state["atleti"]:
        st.markdown(f"**Atleti registrati:** {len(state['atleti'])}")
        for a in state["atleti"][:5]:
            st.markdown(f"• {a['nome']}")
        if len(state["atleti"]) > 5:
            st.caption(f"... e altri {len(state['atleti'])-5}")


def _render_squadre_manager(state):
    atleti_nomi = [a["nome"] for a in state["atleti"]]
    
    if len(state["atleti"]) < 2:
        st.info("Aggiungi almeno 2 atleti per poter creare una squadra.")
        return
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        atleta1 = st.selectbox("Atleta 1 🔴", atleti_nomi, key="sq_a1")
    with col2:
        atleta2 = st.selectbox("Atleta 2 🔵", [n for n in atleti_nomi if n != atleta1], key="sq_a2")
    
    # Nome automatico con toggle
    nome_automatico = st.toggle("Nome automatico squadra", value=True, key="toggle_nome_auto")
    
    if nome_automatico:
        nome_sq = f"{atleta1.split()[0]}/{atleta2.split()[0]}"
        st.text_input("Nome Squadra (auto)", value=nome_sq, disabled=True, key="sq_nome_auto")
    else:
        nome_sq = st.text_input("Nome Squadra", placeholder="es. Team Sabbia", key="sq_nome_manual")
    
    if st.button("➕ Iscrive Squadra", key="btn_add_squadra"):
        # Trova atleta IDs
        a1_obj = next((a for a in state["atleti"] if a["nome"] == atleta1), None)
        a2_obj = next((a for a in state["atleti"] if a["nome"] == atleta2), None)
        
        if not a1_obj or not a2_obj:
            st.error("Atleti non trovati.")
        elif not nome_sq:
            st.error("Inserisci il nome della squadra.")
        else:
            # Verifica atleti non già in squadra
            atleti_in_squadra = [aid for sq in state["squadre"] for aid in sq["atleti"]]
            if a1_obj["id"] in atleti_in_squadra or a2_obj["id"] in atleti_in_squadra:
                st.warning("⚠️ Uno degli atleti è già iscritto in un'altra squadra.")
            else:
                sq = new_squadra(nome_sq, a1_obj["id"], a2_obj["id"])
                state["squadre"].append(sq)
                save_state(state)
                st.success(f"✅ Squadra '{nome_sq}' iscritta!")
                st.rerun()
    
    # Lista squadre iscritte
    if state["squadre"]:
        st.markdown(f"#### Squadre Iscritte ({len(state['squadre'])})")
        for i, sq in enumerate(state["squadre"]):
            a_names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
            col_s, col_btn = st.columns([4, 1])
            with col_s:
                st.markdown(f"**{sq['nome']}** — {' / '.join(a_names)}")
            with col_btn:
                if st.button("🗑️", key=f"del_sq_{i}"):
                    state["squadre"].pop(i)
                    save_state(state)
                    st.rerun()
