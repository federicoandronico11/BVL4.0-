"""
fase_eliminazione.py — Fase 3: Eliminazione Diretta / Playoffs
"""
import streamlit as st
from data_manager import (
    save_state, simula_partita, aggiorna_classifica_squadra,
    get_squadra_by_id, new_partita, aggiungi_semifinali_e_finali,
)
from ui_components import render_match_card


def render_eliminazione(state):
    st.markdown("## ⚡ Eliminazione Diretta")
    
    bracket = state["bracket"]
    
    col_a, col_b = st.columns([2, 2])
    with col_a:
        state["simulazione_al_ranking"] = st.toggle(
            "📊 Invia dati simulati al Ranking",
            value=state["simulazione_al_ranking"]
        )
    with col_b:
        if st.button("🎲 Simula TUTTI i Playoff", use_container_width=True):
            _simula_tutti_playoff(state)
    
    st.divider()
    
    # Raggruppa per round
    rounds = _raggruppa_round(bracket)
    
    for round_name, partite in rounds.items():
        st.markdown(f"### {round_name}")
        
        for i, partita in enumerate(partite):
            render_match_card(state, partita, label=round_name)
            
            if not partita["confermata"]:
                _render_scoreboard_playoff(state, partita, f"pl_{partita['id']}")
            else:
                # Mostra vincitore
                sq = get_squadra_by_id(state, partita["vincitore"])
                if sq:
                    st.success(f"✅ Vincitore: **{sq['nome']}** → avanza al turno successivo")
            
            st.markdown("---")
    
    # Controlla se c'è una finale completata
    _check_finale(state)


def _raggruppa_round(bracket):
    """Raggruppa partite per round_elim e label_elim (Semifinali, Finale 1-2, Finale 3-4)."""
    if not bracket:
        return {}
    by_round = {}
    for p in bracket:
        r = p.get("round_elim", 0)
        label = p.get("label_elim", "")
        if r == 1:
            name = "🥇 SEMIFINALI"
        elif r == 2 and label == "finale_12":
            name = "🏆 FINALE 1º-2º POSTO"
        elif r == 2 and label == "finale_34":
            name = "🥉 FINALE 3º-4º POSTO"
        else:
            name = "⚡ QUARTI / TURNO 1"
        by_round.setdefault(name, []).append(p)
    # Ordine: quarti, semi, finale 1-2, finale 3-4
    order = ["⚡ QUARTI / TURNO 1", "🥇 SEMIFINALI", "🏆 FINALE 1º-2º POSTO", "🥉 FINALE 3º-4º POSTO"]
    return {k: by_round[k] for k in order if k in by_round}


def _render_scoreboard_playoff(state, partita, key_prefix):
    from data_manager import BYE_ID
    sq1 = get_squadra_by_id(state, partita["sq1"]) if partita.get("sq1") != BYE_ID else None
    sq2 = get_squadra_by_id(state, partita["sq2"]) if partita.get("sq2") != BYE_ID else None
    if not sq1 or not sq2:
        return  # BYE o squadra mancante: partita già gestita
    torneo = state["torneo"]
    formato = torneo["formato_set"]

    with st.expander("📝 Inserisci Risultato", expanded=False):
        n_set = 1 if formato == "Set Unico" else 3

        punteggi_inseriti = []
        for s in range(n_set):
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                p1 = st.number_input(f"Set {s+1} — {sq1['nome']}", 0, 50, 0, key=f"{key_prefix}_s{s}_p1")
            with col2:
                st.markdown("<div style='text-align:center;padding-top:28px;color:#666'>vs</div>", unsafe_allow_html=True)
            with col3:
                p2 = st.number_input(f"Set {s+1} — {sq2['nome']}", 0, 50, 0, key=f"{key_prefix}_s{s}_p2")
            punteggi_inseriti.append((p1, p2))
        
        if st.button("✅ CONFERMA RISULTATO", key=f"{key_prefix}_confirm", use_container_width=True):
            s1v, s2v = 0, 0
            punteggi_validi = []
            for p1, p2 in punteggi_inseriti:
                if p1 > 0 or p2 > 0:
                    if p1 > p2: s1v += 1
                    else: s2v += 1
                    punteggi_validi.append((p1, p2))
            
            if not punteggi_validi:
                st.error("Inserisci almeno un set.")
                return
            
            partita["punteggi"] = punteggi_validi
            partita["set_sq1"] = s1v
            partita["set_sq2"] = s2v
            partita["vincitore"] = partita["sq1"] if s1v > s2v else partita["sq2"]
            partita["confermata"] = True
            aggiorna_classifica_squadra(state, partita)
            
            aggiungi_semifinali_e_finali(state)
            save_state(state)
            st.rerun()

        if st.button("🎲 Simula", key=f"{key_prefix}_sim"):
            simula_partita(state, partita)
            if state["simulazione_al_ranking"]:
                aggiorna_classifica_squadra(state, partita)
            aggiungi_semifinali_e_finali(state)
            save_state(state)
            st.rerun()


def _simula_tutti_playoff(state):
    for partita in state["bracket"]:
        if not partita["confermata"]:
            simula_partita(state, partita)
            if state["simulazione_al_ranking"]:
                aggiorna_classifica_squadra(state, partita)
    save_state(state)
    st.rerun()


def _check_finale(state):
    """Se tutti confermati e c'è un solo vincitore: vai alla proclamazione."""
    bracket = state["bracket"]
    if not bracket: return
    
    tutti_confermati = all(p["confermata"] for p in bracket)
    
    if tutti_confermati:
        st.divider()
        col1, col2 = st.columns([3, 1])
        
        vincitori = [p["vincitore"] for p in bracket]
        finale_winner = vincitori[-1] if vincitori else None
        
        with col1:
            if finale_winner:
                sq = get_squadra_by_id(state, finale_winner)
                if sq:
                    st.success(f"🏆 Il torneo è terminato! **{sq['nome']}** ha vinto!")
        
        with col2:
            if st.button("🏆 PROCLAMAZIONE →", use_container_width=True):
                state["vincitore"] = finale_winner
                # Podio: da Finale 1-2 e Finale 3-4 se presenti
                podio = []
                f12 = [p for p in bracket if p.get("label_elim") == "finale_12" and p.get("confermata")]
                f34 = [p for p in bracket if p.get("label_elim") == "finale_34" and p.get("confermata")]
                if f12:
                    w = f12[0]["vincitore"]
                    l = f12[0]["sq1"] if f12[0]["vincitore"] == f12[0]["sq2"] else f12[0]["sq2"]
                    podio = [(1, w), (2, l)]
                else:
                    perdenti = [p["sq1"] if p["vincitore"] == p["sq2"] else p["sq2"] for p in bracket]
                    podio = [(1, finale_winner)]
                    if perdenti:
                        podio.append((2, perdenti[-1]))
                    if len(perdenti) > 1:
                        podio.append((3, perdenti[-2]))
                if f34:
                    w3 = f34[0]["vincitore"]
                    l4 = f34[0]["sq1"] if f34[0]["vincitore"] == f34[0]["sq2"] else f34[0]["sq2"]
                    podio.append((3, w3))
                    podio.append((4, l4))
                elif len(podio) == 2:
                    # Nessuna finale 3-4: 3° = perdente altra semi
                    semi = [p for p in bracket if p.get("round_elim") == 1]
                    perdenti_semi = [p["sq1"] if p["vincitore"] == p["sq2"] else p["sq2"] for p in semi if p.get("confermata")]
                    if perdenti_semi:
                        podio.append((3, perdenti_semi[0]))
                
                state["podio"] = podio
                if state["simulazione_al_ranking"]:
                    from data_manager import trasferisci_al_ranking
                    trasferisci_al_ranking(state, podio)
                
                state["fase"] = "proclamazione"
                save_state(state)
                st.rerun()
