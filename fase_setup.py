"""
fase_setup.py — Fase 1: Configurazione torneo strutturata + iscrizione squadre
"""
import streamlit as st
from data_manager import (
    new_atleta, new_squadra, get_atleta_by_id,
    save_state, genera_gironi
)


def render_setup(state):
    st.markdown("## ⚙️ Configurazione Torneo")
    st.caption("Completa le sezioni in ordine. Tutte le impostazioni vengono salvate automaticamente.")

    # ─── 1. IMPOSTAZIONI GENERALI ───────────────────────────────────────────
    with st.expander("📋 1. Impostazioni generali", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input(
                "Nome torneo",
                value=state["torneo"]["nome"],
                placeholder="es. Summer Cup 2025",
                help="Nome ufficiale del torneo"
            )
            state["torneo"]["nome"] = nome
            from datetime import datetime as _dt
            _data_str = state["torneo"].get("data")
            try:
                _data_val = _dt.strptime(_data_str, "%Y-%m-%d").date() if _data_str else _dt.today().date()
            except Exception:
                _data_val = _dt.today().date()
            data = st.date_input("Data torneo", value=_data_val)
            state["torneo"]["data"] = str(data)
        with c2:
            sede = st.text_input(
                "Sede / Luogo",
                value=state["torneo"].get("sede", ""),
                placeholder="es. Lido di Ostia",
                help="Opzionale"
            )
            state["torneo"]["sede"] = sede

    # ─── 2. FORMATO DI GIOCO ─────────────────────────────────────────────────
    with st.expander("🏐 2. Formato di gioco", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            tipo_opts = ["Gironi + Playoff", "Doppia Eliminazione", "Girone Unico"]
            tipo_idx = tipo_opts.index(state["torneo"].get("tipo_tabellone", "Gironi + Playoff")) if state["torneo"].get("tipo_tabellone") in tipo_opts else 0
            tipo = st.selectbox(
                "Tipo tabellone",
                tipo_opts,
                index=tipo_idx,
                help="Girone Unico = un solo girone all'italiana"
            )
            state["torneo"]["tipo_tabellone"] = tipo
            state["torneo"]["girone_unico"] = (tipo == "Girone Unico")
        with c2:
            formato = st.selectbox(
                "Formato set",
                ["Set Unico", "Best of 3"],
                index=["Set Unico", "Best of 3"].index(state["torneo"]["formato_set"]),
                help="Best of 3 = al meglio delle 3 partite"
            )
            state["torneo"]["formato_set"] = formato
            pmax = st.number_input(
                "Punteggio massimo per set",
                min_value=11,
                max_value=30,
                value=state["torneo"]["punteggio_max"],
                help="Di solito 21; 15 per tie-break"
            )
            state["torneo"]["punteggio_max"] = pmax
        with c3:
            ptb = st.number_input(
                "Punteggio tie-break (se previsto)",
                min_value=11,
                max_value=25,
                value=state["torneo"].get("punteggio_tie_break", 15),
                help="Terzo set in Best of 3"
            )
            state["torneo"]["punteggio_tie_break"] = ptb

    # ─── 3. GIRONI E QUALIFICAZIONE ──────────────────────────────────────────
    with st.expander("🔵 3. Gironi e qualificazione", expanded=not state["torneo"].get("girone_unico")):
        girone_unico = state["torneo"].get("girone_unico", False)
        if girone_unico:
            st.info("Girone unico attivo: tutte le squadre in un solo girone. Le qualificate ai playoff dipendono dal numero di squadre.")
            state["torneo"]["num_gironi"] = 1
            n_sq = len(state["squadre"])
            state["torneo"]["passano_per_girone"] = max(2, n_sq // 2) if n_sq else 2
        else:
            r1, r2 = st.columns(2)
            with r1:
                st.markdown("**Numero di gironi**")
                num_gironi = st.slider(
                    "Gironi",
                    min_value=2,
                    max_value=8,
                    value=state["torneo"].get("num_gironi", 2),
                    key="num_gironi_setup",
                    help="Le squadre verranno distribuite tra i gironi"
                )
                state["torneo"]["num_gironi"] = num_gironi
                n_sq = len(state["squadre"])
                if n_sq > 0 and num_gironi > 0:
                    per_girone = n_sq // num_gironi
                    st.caption(f"→ Circa **{per_girone}** squadre per girone ({n_sq} totali)")
            with r2:
                st.markdown("**Qualificazione ai playoff**")
                passano = st.number_input(
                    "Squadre che passano per ogni girone",
                    min_value=1,
                    max_value=4,
                    value=state["torneo"].get("passano_per_girone", 2),
                    key="passano_setup"
                )
                state["torneo"]["passano_per_girone"] = passano
                criterio = st.radio(
                    "Criterio di passaggio",
                    ["classifica", "avulsa"],
                    index=0 if state["torneo"].get("criterio_passaggio", "classifica") == "classifica" else 1,
                    key="criterio_setup",
                    horizontal=True,
                    format_func=lambda x: "Classifica generale" if x == "classifica" else "Classifica avulsa"
                )
                state["torneo"]["criterio_passaggio"] = criterio

    # ─── 4. PERSONALIZZAZIONE TEMA ────────────────────────────────────────────
    with st.expander("🎨 4. Personalizzazione tema", expanded=False):
        st.markdown("Scegli l’aspetto dell’interfaccia. Il tema si applica a tutta l’app (sidebar, carte, tabelloni).")
        theme_opts = [
            ("dazn_dark", "Scuro DAZN", "Sfondo scuro con accento rosso. Stile ufficiale."),
            ("dazn_red", "Rosso DAZN", "Variante con rosso più intenso e sfumature calde."),
            ("dark_blue", "Blu scuro", "Sfondo blu notte con accenti azzurri."),
            ("dark_green", "Verde scuro", "Sfondo scuro con accenti verdi."),
        ]
        current = state.get("theme", "dazn_dark")
        idx = next((i for i, (k, _, _) in enumerate(theme_opts) if k == current), 0)
        choice = st.radio(
            "Tema interfaccia",
            range(len(theme_opts)),
            index=idx,
            key="theme_radio_setup",
            format_func=lambda i: f"{theme_opts[i][1]} — {theme_opts[i][2]}"
        )
        new_theme = theme_opts[choice][0]
        if new_theme != state.get("theme"):
            state["theme"] = new_theme
            save_state(state)
            st.success("Tema aggiornato. L’interfaccia si adatterà al prossimo caricamento.")
            if st.button("🔄 Applica tema ora", key="apply_theme_setup"):
                st.rerun()
        st.caption("Puoi cambiare il tema anche dalla sidebar in qualsiasi momento.")

    # ─── 5. GESTIONE ATLETI ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 👤 5. Gestione atleti")
    _render_atleti_manager(state)

    # ─── 6. ISCRIZIONE SQUADRE ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🏐 6. Iscrizione squadre")
    _render_squadre_manager(state)

    # ─── RIEPILOGO E AVVIO ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✅ Riepilogo e avvio")
    n_squadre = len(state["squadre"])
    col_a, col_b = st.columns([2, 1])

    with col_a:
        if n_squadre < 4:
            st.warning(f"⚠️ Servono almeno **4 squadre** per avviare il torneo. Attualmente: **{n_squadre}**.")
        elif not state["torneo"]["nome"]:
            st.warning("⚠️ Inserisci il **nome del torneo** nella sezione 1.")
        else:
            st.success(f"✅ **{n_squadre}** squadre iscritte — Pronto per avviare!")
        # Riepilogo testuale
        if state["torneo"]["nome"]:
            st.caption(f"Torneo: **{state['torneo']['nome']}** · {state['torneo']['data']} · {state['torneo']['tipo_tabellone']} · {state['torneo']['formato_set']} (max {state['torneo']['punteggio_max']} pt)")

    with col_b:
        if n_squadre >= 4 and state["torneo"]["nome"]:
            if st.button("🚀 AVVIA TORNEO →", use_container_width=True, type="primary"):
                ids = [s["id"] for s in state["squadre"]]
                num_gironi = state["torneo"].get("num_gironi", max(2, n_squadre // 4))
                girone_unico = state["torneo"].get("girone_unico", False)
                state["gironi"] = genera_gironi(ids, num_gironi=num_gironi, girone_unico=girone_unico)
                state["fase"] = "gironi"
                save_state(state)
                st.rerun()


def _render_atleti_manager(state):
    nomi_esistenti = [a["nome"] for a in state["atleti"]]

    with st.expander("➕ Aggiungi nuovo atleta", expanded=False):
        nuovo_nome = st.text_input("Nome atleta", key="new_atleta_name", placeholder="Nome Cognome")
        if st.button("Aggiungi atleta", key="btn_add_atleta"):
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
            st.caption(f"... e altri {len(state['atleti']) - 5}")


def _render_squadre_manager(state):
    atleti_nomi = [a["nome"] for a in state["atleti"]]

    if len(state["atleti"]) < 2:
        st.info("Aggiungi almeno **2 atleti** per poter creare una squadra.")
        return

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        atleta1 = st.selectbox("Atleta 1 🔴", atleti_nomi, key="sq_a1")
    with col2:
        atleta2 = st.selectbox("Atleta 2 🔵", [n for n in atleti_nomi if n != atleta1], key="sq_a2")

    nome_automatico = st.toggle("Nome automatico squadra", value=True, key="toggle_nome_auto")

    if nome_automatico:
        nome_sq = f"{atleta1.split()[0]}/{atleta2.split()[0]}"
        st.text_input("Nome squadra (auto)", value=nome_sq, disabled=True, key="sq_nome_auto")
    else:
        nome_sq = st.text_input("Nome squadra", placeholder="es. Team Sabbia", key="sq_nome_manual")

    if st.button("➕ Iscrivi squadra", key="btn_add_squadra"):
        a1_obj = next((a for a in state["atleti"] if a["nome"] == atleta1), None)
        a2_obj = next((a for a in state["atleti"] if a["nome"] == atleta2), None)

        if not a1_obj or not a2_obj:
            st.error("Atleti non trovati.")
        elif not nome_sq:
            st.error("Inserisci il nome della squadra.")
        else:
            atleti_in_squadra = [aid for sq in state["squadre"] for aid in sq["atleti"]]
            if a1_obj["id"] in atleti_in_squadra or a2_obj["id"] in atleti_in_squadra:
                st.warning("⚠️ Uno degli atleti è già iscritto in un'altra squadra.")
            else:
                sq = new_squadra(nome_sq, a1_obj["id"], a2_obj["id"])
                state["squadre"].append(sq)
                save_state(state)
                st.success(f"✅ Squadra **{nome_sq}** iscritta!")
                st.rerun()

    if state["squadre"]:
        st.markdown(f"#### Squadre iscritte ({len(state['squadre'])})")
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
