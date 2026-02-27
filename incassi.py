"""
incassi.py — Dashboard incassi torneo (iscrizioni, extra)
"""
import streamlit as st


def _get_incassi_state():
    if "_incassi" not in st.session_state:
        st.session_state._incassi = {
            "quota_iscrizione": 0.0,
            "extra_descrizioni": [],
            "extra_importi": [],
        }
    return st.session_state._incassi


def render_incassi(state):
    """Dashboard semplice per calcolare gli incassi del torneo.

    Nota: per non toccare la struttura dati del torneo, i valori sono tenuti solo in sessione Streamlit.
    """
    st.markdown("## 💶 Incassi del Torneo")
    st.caption("Calcolo rapido degli incassi da iscrizioni e voci extra.")

    inc = _get_incassi_state()

    n_squadre = len(state.get("squadre", []))
    quota = st.number_input("Quota iscrizione per squadra (€)", min_value=0.0, step=5.0, value=float(inc["quota_iscrizione"]))
    inc["quota_iscrizione"] = quota

    incasso_iscrizioni = quota * n_squadre

    st.markdown("### ➕ Voci extra")
    c1, c2 = st.columns([3, 1])
    with c1:
        desc = st.text_input("Descrizione", key="incassi_desc")
    with c2:
        val = st.number_input("Importo (€)", min_value=0.0, step=5.0, key="incassi_val")
    if st.button("Aggiungi voce", key="btn_add_voce_incasso"):
        if desc and val > 0:
            inc["extra_descrizioni"].append(desc)
            inc["extra_importi"].append(val)
        else:
            st.warning("Inserisci una descrizione e un importo > 0.")

    extra_total = 0.0
    if inc["extra_descrizioni"]:
        for d, v in zip(inc["extra_descrizioni"], inc["extra_importi"]):
            st.markdown(f"• {d}: **€ {v:,.2f}**")
            extra_total += v

    st.markdown("---")
    totale = incasso_iscrizioni + extra_total
    st.metric("Incassi iscrizioni", f"€ {incasso_iscrizioni:,.2f}")
    st.metric("Incassi extra", f"€ {extra_total:,.2f}")
    st.metric("Totale incassi", f"€ {totale:,.2f}")
