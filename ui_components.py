"""
ui_components.py — Stile DAZN Dark Mode + componenti riutilizzabili + Carte FC26
"""
import streamlit as st
from data_manager import nome_squadra, get_squadra_by_id, compute_overall, compute_attributes, BYE_ID

# ─── CARTE FC26: STILE DA OVERALL ─────────────────────────────────────────────

def get_card_style(overall):
    """
    Restituisce la classe CSS del tier per la carta in base all'Overall (40-99).
    Nuovi giocatori (overall 40) → Bronzo Raro.
    """
    if overall is None:
        overall = 40
    overall = max(40, min(99, int(overall)))
    if overall == 40:
        return "fc-bronzo-rare"
    if overall < 45:
        return "fc-bronzo-comune"
    if overall < 50:
        return "fc-bronzo-rare"
    if overall < 55:
        return "fc-argento-comune"
    if overall < 60:
        return "fc-argento-rare"
    if overall < 65:
        return "fc-oro-comune"
    if overall < 70:
        return "fc-oro-rare"
    if overall < 75:
        return "fc-eroe"
    if overall < 80:
        return "fc-if"
    if overall < 85:
        return "fc-leggenda"
    if overall < 90:
        return "fc-toty"
    if overall < 95:
        return "fc-toty-evoluto"
    return "fc-goat"


def _placeholder_svg_athlete():
    """SVG placeholder sagoma atletica grigia."""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 180" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
      <defs><linearGradient id="g" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#444"/><stop offset="100%" stop-color="#222"/></linearGradient></defs>
      <ellipse cx="60" cy="32" rx="22" ry="24" fill="url(#g)"/>
      <path d="M35 95 Q60 75 85 95 L85 160 Q60 180 35 160 Z" fill="url(#g)"/>
      <rect x="50" y="95" width="20" height="65" fill="url(#g)"/>
      <circle cx="60" cy="155" r="18" fill="url(#g)"/>
    </svg>"""


def render_player_card_html(atleta, photo_url=None):
    """
    Genera HTML della carta FC26.
    - Se photo_url manca, usa placeholder SVG.
    - Mostra Overall in alto a sinistra.
    - Mostra 6 attributi stile FIFA (ATT, DEF, ALZ, RIC, MUR, BAT) derivati dai risultati.
    - Badge sotto la foto per trofei, vittorie, tornei.
    """
    overall = compute_overall(atleta)
    tier_class = get_card_style(overall)
    nome = (atleta.get("nome") or "Atleta").replace("<", "&lt;").replace(">", "&gt;")
    s = atleta.get("stats", {})
    trofei = sum(1 for _, pos in s.get("storico_posizioni", []) if pos == 1)
    vittorie = s.get("vittorie", 0)
    tornei = s.get("tornei", 0)

    if photo_url and photo_url.strip():
        img_block = f'<img src="{photo_url.strip()}" alt="{nome}"/>'
    else:
        img_block = _placeholder_svg_athlete()

    # Attributi stile FIFA
    attrs = compute_attributes(atleta)
    # Disposti 3 a sinistra, 3 a destra
    stats_html = f"""
            <div class="fc-card-stats">
                <div class="fc-stat-col">
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['ATT']}</span><span class="fc-stat-label">ATT</span></div>
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['ALZ']}</span><span class="fc-stat-label">ALZ</span></div>
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['MUR']}</span><span class="fc-stat-label">MUR</span></div>
                </div>
                <div class="fc-stat-col">
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['DEF']}</span><span class="fc-stat-label">DEF</span></div>
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['RIC']}</span><span class="fc-stat-label">RIC</span></div>
                    <div class="fc-stat-row"><span class="fc-stat-value">{attrs['BAT']}</span><span class="fc-stat-label">BAT</span></div>
                </div>
            </div>
    """

    badges = []
    if tornei > 0:
        badges.append(f'<span class="fc-badge">🏆 {tornei}</span>')
    if vittorie > 0:
        badges.append(f'<span class="fc-badge">✅ {vittorie}</span>')
    if trofei > 0:
        badges.append(f'<span class="fc-badge">🥇 {trofei}</span>')
    badges_html = "".join(badges) if badges else '<span class="fc-badge">—</span>'

    return f"""
    <div class="fc-card-wrap {tier_class}">
        <div class="fc-card-inner">
            <div class="fc-card-overall">{overall}</div>
            <div class="fc-card-photo-wrap">{img_block}</div>
            <div class="fc-card-name">{nome}</div>
{stats_html}
            <div class="fc-card-badges">{badges_html}</div>
        </div>
    </div>
    """


# ─── CSS DARK MODE STILE DAZN ────────────────────────────────────────────────

def inject_css(theme="dazn_dark"):
    try:
        theme = (theme or "dazn_dark").strip()
    except Exception:
        theme = "dazn_dark"
    theme_overrides = ""
    if theme == "dazn_red":
        theme_overrides = """
    :root {
        --accent-red: #ff2244;
        --bg-primary: #0f0a0a;
        --border: #3a2a2a;
    }"""
    elif theme == "dark_blue":
        theme_overrides = """
    :root {
        --accent-red: #0070f3;
        --accent-blue: #00aaff;
        --bg-primary: #0a0f1a;
        --border: #2a3a4a;
    }"""
    elif theme == "dark_green":
        theme_overrides = """
    :root {
        --accent-red: #00c851;
        --accent-blue: #00e676;
        --bg-primary: #0a0f0a;
        --border: #2a3a2a;
        --green: #00e676;
    }"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;800&family=Barlow:wght@400;500;600&display=swap');

    :root {
        --bg-primary: #0a0a0f;
        --bg-card: #13131a;
        --bg-card2: #1a1a24;
        --accent-red: #e8002d;
        --accent-blue: #0070f3;
        --accent-gold: #ffd700;
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --border: #2a2a3a;
        --green: #00c851;
    }
    """ + theme_overrides + """

    html, body, [class*="css"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Barlow', sans-serif !important;
    }

    /* Nasconde elementi Streamlit di default */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem !important; max-width: 1200px !important; }

    /* HEADER TORNEO */
    .tournament-header {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%);
        border-bottom: 3px solid var(--accent-red);
        padding: 20px 30px;
        text-align: center;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .tournament-header::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 300%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(232,0,45,0.05), transparent);
        animation: shimmer 4s infinite;
    }
    @keyframes shimmer { to { left: 100%; } }
    .tournament-title {
        font-family: 'Barlow Condensed', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }
    .tournament-subtitle {
        color: var(--accent-red);
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 4px;
    }

    /* FASE BADGE */
    .fase-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--bg-card2);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin: 4px;
    }
    .fase-badge.active {
        background: var(--accent-red);
        border-color: var(--accent-red);
        color: white;
    }
    .fase-badge.done {
        background: var(--bg-card2);
        border-color: var(--green);
        color: var(--green);
    }

    /* MATCH CARD */
    .match-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0;
        margin-bottom: 12px;
        overflow: hidden;
        transition: border-color 0.2s;
    }
    .match-card:hover { border-color: #444; }
    .match-card.confirmed { border-left: 4px solid var(--green); }
    .match-card-header {
        background: var(--bg-card2);
        padding: 8px 16px;
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-secondary);
        font-weight: 600;
    }
    .match-body {
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .team-side {
        flex: 1;
        text-align: center;
    }
    .team-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .team-red .team-name { color: var(--accent-red); }
    .team-blue .team-name { color: var(--accent-blue); }
    .team-players {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    .score-center {
        text-align: center;
        min-width: 100px;
    }
    .score-sets {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: white;
        line-height: 1;
    }
    .score-sets span { color: var(--text-secondary); font-size: 2rem; }
    .score-parziale {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    .vs-label {
        font-size: 0.7rem;
        letter-spacing: 2px;
        color: var(--text-secondary);
        text-transform: uppercase;
    }

    /* CLASSIFICA TABLE */
    .rank-table { width: 100%; border-collapse: collapse; }
    .rank-table th {
        background: var(--bg-card2);
        color: var(--text-secondary);
        font-size: 0.7rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid var(--border);
    }
    .rank-table td {
        padding: 12px 14px;
        text-align: center;
        border-bottom: 1px solid var(--border);
        font-size: 0.9rem;
    }
    .rank-table tr:hover td { background: var(--bg-card2); }
    .rank-pos { font-family: 'Barlow Condensed', sans-serif; font-weight: 800; font-size: 1.2rem; }
    .rank-pos.gold { color: var(--accent-gold); }
    .rank-pos.silver { color: #c0c0c0; }
    .rank-pos.bronze { color: #cd7f32; }

    /* PODIO */
    .podio-container {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 12px;
        padding: 30px 0;
    }
    .podio-step {
        text-align: center;
        border-radius: 8px 8px 0 0;
        padding: 20px 24px 16px;
        min-width: 150px;
    }
    .podio-1 { background: linear-gradient(180deg, #b8860b, #ffd700); height: 180px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-2 { background: linear-gradient(180deg, #808080, #c0c0c0); height: 140px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-3 { background: linear-gradient(180deg, #8b4513, #cd7f32); height: 110px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-4 { background: linear-gradient(180deg, #4a4a4a, #6a6a6a); height: 90px; display: flex; flex-direction: column; justify-content: flex-end; }
    .podio-rank { font-family: 'Barlow Condensed', sans-serif; font-size: 2rem; font-weight: 800; color: rgba(0,0,0,0.7); }
    .podio-name { font-weight: 700; font-size: 0.9rem; color: rgba(0,0,0,0.9); text-transform: uppercase; letter-spacing: 1px; }

    /* WINNER BANNER */
    .winner-banner {
        background: linear-gradient(135deg, #b8860b, #ffd700, #b8860b);
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        animation: pulse-gold 2s ease-in-out infinite;
    }
    @keyframes pulse-gold {
        0%, 100% { box-shadow: 0 0 20px rgba(255,215,0,0.4); }
        50% { box-shadow: 0 0 50px rgba(255,215,0,0.8); }
    }
    .winner-title {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.7);
        font-weight: 600;
    }
    .winner-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #000;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .winner-players { color: rgba(0,0,0,0.8); font-size: 1rem; font-weight: 600; }

    /* CAREER CARD (legacy fallback) */
    .career-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }
    .career-name { font-family: 'Barlow Condensed', sans-serif; font-size: 2rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-top: 16px; }
    .stat-box { background: var(--bg-card2); border-radius: 8px; padding: 12px; text-align: center; }
    .stat-value { font-family: 'Barlow Condensed', sans-serif; font-size: 1.8rem; font-weight: 700; color: var(--accent-blue); }
    .stat-label { font-size: 0.65rem; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-secondary); margin-top: 4px; }

    /* ─── FC26 ULTIMATE TEAM CARDS ─────────────────────────────────────────── */
    .fc-card-wrap {
        position: relative;
        width: 320px;
        min-height: 420px;
        margin: 20px auto;
        border-radius: 16px;
        overflow: visible;
        backdrop-filter: blur(12px);
    }
    .fc-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        border-radius: inherit;
        overflow: hidden;
        box-sizing: border-box;
    }
    .fc-card-overall {
        position: absolute;
        top: 12px;
        left: 12px;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #fff;
        text-shadow: 0 0 12px currentColor;
        z-index: 3;
        animation: fc-pulse-glow 2s ease-in-out infinite;
    }
    @keyframes fc-pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 6px rgba(255,255,255,0.8)); }
        50% { filter: drop-shadow(0 0 14px rgba(255,255,255,1)); }
    }
    .fc-card-photo-wrap {
        width: 100%;
        height: 220px;
        background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, transparent 50%);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    .fc-card-photo-wrap img { width: 100%; height: 100%; object-fit: cover; }
    .fc-card-stats {
        display: flex;
        justify-content: space-between;
        padding: 4px 18px 0;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 0.8rem;
        color: #f5f5f5;
    }
    .fc-stat-col {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .fc-stat-row {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .fc-stat-value {
        font-weight: 800;
        min-width: 26px;
    }
    .fc-stat-label {
        font-weight: 600;
        letter-spacing: 1px;
    }

    .fc-card-name {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #fff;
        padding: 10px 14px 4px;
        text-align: center;
        line-height: 1.2;
    }
    .fc-card-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        justify-content: center;
        padding: 8px 14px 14px;
    }
    .fc-badge {
        background: rgba(0,0,0,0.5);
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        color: #ffd700;
        border: 1px solid rgba(255,215,0,0.4);
    }
    @keyframes fc-shine {
        0% { transform: translateX(-100%) skewX(-15deg); }
        100% { transform: translateX(200%) skewX(-15deg); }
    }
    .fc-card-inner::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 60%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        animation: fc-shine 3s ease-in-out infinite;
        pointer-events: none;
    }
    /* Tier: Bronzo Comune 40-45 */
    .fc-card-wrap.fc-bronzo-comune {
        background: linear-gradient(145deg, #5c4033 0%, #3d2b24 50%, #2a1f1a 100%);
        border: 2px solid #8b7355;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.4);
    }
    .fc-card-wrap.fc-bronzo-comune .fc-card-inner { background: repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px); }
    /* Tier: Bronzo Raro 45-50 (e 40 per nuovi) */
    .fc-card-wrap.fc-bronzo-rare {
        background: linear-gradient(145deg, #b87333 0%, #8b5a2b 50%, #5c4033 100%);
        border: 2px solid #daa520;
        box-shadow: 0 0 20px rgba(218,165,32,0.3), inset 0 0 20px rgba(255,255,255,0.05);
        animation: fc-bronzo-shine 4s ease-in-out infinite;
    }
    @keyframes fc-bronzo-shine {
        0%, 100% { box-shadow: 0 0 20px rgba(218,165,32,0.3), inset 0 0 20px rgba(255,255,255,0.05); }
        50% { box-shadow: 0 0 35px rgba(218,165,32,0.5), inset 0 0 25px rgba(255,255,255,0.08); }
    }
    /* Argento Comune 50-55 */
    .fc-card-wrap.fc-argento-comune {
        background: linear-gradient(145deg, #7a7a7a 0%, #5a5a5a 50%, #3d3d3d 100%);
        border: 2px solid #9a9a9a;
        box-shadow: inset 0 0 40px rgba(255,255,255,0.06);
    }
    /* Argento Raro 55-60 */
    .fc-card-wrap.fc-argento-rare {
        background: linear-gradient(145deg, #c0c0c0 0%, #a0a0a0 50%, #707070 100%);
        border: 2px solid #e0e0e0;
        box-shadow: 0 0 25px rgba(255,255,255,0.2), inset 0 0 30px rgba(255,255,255,0.1);
        animation: fc-argento-shine 3s ease-in-out infinite;
    }
    @keyframes fc-argento-shine {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.15); }
    }
    /* Oro Comune 60-65 */
    .fc-card-wrap.fc-oro-comune {
        background: linear-gradient(145deg, #d4af37 0%, #b8860b 50%, #8b6914 100%);
        border: 2px solid #ffd700;
        box-shadow: 0 0 30px rgba(255,215,0,0.35);
    }
    /* Oro Raro 65-70 */
    .fc-card-wrap.fc-oro-rare {
        background: linear-gradient(145deg, #ffd700 0%, #daa520 50%, #b8860b 100%);
        border: 2px solid #fff8dc;
        box-shadow: 0 0 40px rgba(255,215,0,0.5);
        animation: fc-oro-shine 2.5s ease-in-out infinite;
    }
    @keyframes fc-oro-shine {
        0%, 100% { box-shadow: 0 0 40px rgba(255,215,0,0.5); }
        50% { box-shadow: 0 0 60px rgba(255,215,0,0.8); }
    }
    /* Eroe 70-75: viola, neon, fulmini, nastri */
    .fc-card-wrap.fc-eroe {
        background: linear-gradient(145deg, #4a148c 0%, #2d0a5c 50%, #1a0630 100%);
        border: 2px solid #bb86fc;
        box-shadow: 0 0 25px rgba(187,134,252,0.5), inset 0 0 20px rgba(0,0,0,0.3);
    }
    .fc-card-wrap.fc-eroe::before {
        content: '';
        position: absolute;
        top: -2px; left: -2px; right: -2px; bottom: -2px;
        border-radius: inherit;
        background: linear-gradient(45deg, transparent 40%, rgba(187,134,252,0.3) 50%, transparent 60%);
        animation: fc-neon-border 2s linear infinite;
        z-index: -1;
    }
    .fc-card-wrap.fc-eroe .fc-card-inner::before {
        content: '⚡';
        position: absolute;
        font-size: 1.5rem;
        opacity: 0.7;
        animation: fc-lightning 1.5s ease-in-out infinite;
    }
    @keyframes fc-neon-border { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    @keyframes fc-lightning { 0%, 100% { opacity: 0.3; } 50% { opacity: 0.9; } }
    /* IF 75-80: nero premium, shiny, forma premium */
    .fc-card-wrap.fc-if {
        background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 50%, #000 100%);
        border: 2px solid #ffd700;
        box-shadow: 0 0 35px rgba(255,215,0,0.4);
        clip-path: polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px));
    }
    /* Leggenda 80-85: bianco perla, fulmini, ali */
    .fc-card-wrap.fc-leggenda {
        background: linear-gradient(145deg, #f5f5dc 0%, #e8e8d0 50%, #d4c4a0 100%);
        border: 2px solid #ffd700;
        box-shadow: 0 0 40px rgba(255,215,0,0.5);
        clip-path: polygon(0 12px, 12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%);
    }
    .fc-card-wrap.fc-leggenda .fc-card-inner::before { content: '⚡'; position: absolute; font-size: 1.2rem; opacity: 0.6; animation: fc-lightning 1.2s ease-in-out infinite; }
    /* TOTY 85-90: blu reale e oro, ali argentate, barocco */
    .fc-card-wrap.fc-toty {
        background: linear-gradient(145deg, #1e3a5f 0%, #0d1b2a 50%, #0a1628 100%);
        border: 2px solid #ffd700;
        box-shadow: 0 0 50px rgba(255,215,0,0.4);
        border-radius: 24px;
        clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
    }
    .fc-card-wrap.fc-toty::after {
        content: '';
        position: absolute;
        top: -30px; left: -10px;
        width: 40px; height: 60px;
        background: linear-gradient(180deg, rgba(192,192,192,0.6), transparent);
        clip-path: polygon(50% 0, 100% 100%, 0 100%);
        filter: blur(2px);
    }
    .fc-card-wrap.fc-toty::before {
        content: '';
        position: absolute;
        top: -30px; right: -10px;
        width: 40px; height: 60px;
        background: linear-gradient(180deg, rgba(192,192,192,0.6), transparent);
        clip-path: polygon(50% 0, 100% 100%, 0 100%);
        filter: blur(2px);
    }
    /* TOTY Evoluto 90-95: viola, ali dorate, nubi fulmini, barocco */
    .fc-card-wrap.fc-toty-evoluto {
        background: linear-gradient(145deg, #2d1b4e 0%, #1e3a5f 50%, #0d1b2a 100%);
        border: 2px solid #bb86fc;
        box-shadow: 0 0 45px rgba(187,134,252,0.5), 0 0 60px rgba(255,215,0,0.3);
        border-radius: 24px;
    }
    .fc-card-wrap.fc-toty-evoluto::after {
        content: '';
        position: absolute;
        top: -35px; left: -10px;
        width: 45px; height: 65px;
        background: linear-gradient(180deg, rgba(255,215,0,0.7), transparent);
        clip-path: polygon(50% 0, 100% 100%, 0 100%);
        filter: blur(2px);
    }
    /* GOAT 95-99: infernale, ali nere, fulmini nuvole */
    .fc-card-wrap.fc-goat {
        background: linear-gradient(145deg, #8b0000 0%, #2d0a0a 50%, #0d0000 100%);
        border: 2px solid #ff4500;
        box-shadow: 0 0 50px rgba(255,69,0,0.5), inset 0 0 30px rgba(0,0,0,0.5);
        border-radius: 16px;
        clip-path: polygon(0 0, calc(100% - 25px) 0, 100% 25px, 100% 100%, 0 100%, 0 0);
    }
    .fc-card-wrap.fc-goat .fc-card-inner::before {
        content: '⚡';
        position: absolute;
        font-size: 1.4rem;
        color: #333;
        opacity: 0.8;
        animation: fc-lightning 0.8s ease-in-out infinite;
    }

    /* BUTTONS */
    .stButton > button {
        background: var(--accent-red) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        padding: 10px 20px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #ff1a45 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(232,0,45,0.4) !important;
    }

    /* INPUTS */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: var(--bg-card2) !important;
        border: 1px solid var(--border) !important;
        color: white !important;
        border-radius: 6px !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 4px !important; }
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card2) !important;
        color: var(--text-secondary) !important;
        border-radius: 6px 6px 0 0 !important;
        border: 1px solid var(--border) !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-red) !important;
        color: white !important;
        border-color: var(--accent-red) !important;
    }

    /* DIVIDER */
    hr { border-color: var(--border) !important; }

    /* METRIC */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────

def render_header(state):
    nome = state["torneo"]["nome"] or "Beach Volley"
    st.markdown(f"""
    <div class="tournament-header">
        <div class="tournament-title">🏐 {nome}</div>
        <div class="tournament-subtitle">Tournament Manager Pro</div>
    </div>
    """, unsafe_allow_html=True)
    
    fasi = [("setup","⚙️ Setup"), ("gironi","🔵 Gironi"), ("eliminazione","⚡ Eliminazione"), ("proclamazione","🏆 Finale")]
    stati = []
    fase_corrente = state["fase"]
    ordine = ["setup","gironi","eliminazione","proclamazione"]
    idx_corrente = ordine.index(fase_corrente)
    
    html = '<div style="display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:20px;">'
    for i, (k, label) in enumerate(fasi):
        if i < idx_corrente:
            css = "fase-badge done"
            icon = "✓ "
        elif i == idx_corrente:
            css = "fase-badge active"
            icon = ""
        else:
            css = "fase-badge"
            icon = ""
        html += f'<span class="{css}">{icon}{label}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── MATCH CARD ──────────────────────────────────────────────────────────────

def render_match_card(state, partita, label=""):
    from data_manager import get_atleta_by_id, BYE_ID

    def safe_sq(sid):
        if sid == BYE_ID or not sid:
            return {"nome": "— BYE —", "atleti": []}
        return get_squadra_by_id(state, sid)

    sq1 = safe_sq(partita.get("sq1"))
    sq2 = safe_sq(partita.get("sq2"))
    if not sq1:
        sq1 = {"nome": "Squadra da definire", "atleti": []}
    if not sq2:
        sq2 = {"nome": "Squadra da definire", "atleti": []}

    def players_str(sq):
        if not sq or sq.get("nome") == "— BYE —":
            return ""
        names = [get_atleta_by_id(state, aid)["nome"] for aid in sq.get("atleti", []) if get_atleta_by_id(state, aid)]
        return " / ".join(names) if names else "—"

    parziali = " | ".join([f"{p[0]}-{p[1]}" for p in partita.get("punteggi", [])]) if partita.get("punteggi") else "—"
    confirmed_class = "confirmed" if partita.get("confermata") else ""

    nome1 = (sq1.get("nome") or "—").replace("<", "&lt;").replace(">", "&gt;")
    nome2 = (sq2.get("nome") or "—").replace("<", "&lt;").replace(">", "&gt;")
    header_label = (label or "").replace("<", "&lt;").replace(">", "&gt;")
    status = "✅ CONFERMATA" if partita.get("confermata") else "🔴 LIVE"

    st.markdown(f"""
    <div class="match-card {confirmed_class}">
        <div class="match-card-header">{header_label} {status}</div>
        <div class="match-body">
            <div class="team-side team-red">
                <div class="team-name">{nome1}</div>
                <div class="team-players">{players_str(sq1)}</div>
            </div>
            <div class="score-center">
                <div class="score-sets">
                    <span style="color:var(--accent-red)">{partita.get('set_sq1', 0)}</span>
                    <span>–</span>
                    <span style="color:var(--accent-blue)">{partita.get('set_sq2', 0)}</span>
                </div>
                <div class="score-parziale">{parziali}</div>
            </div>
            <div class="team-side team-blue">
                <div class="team-name">{nome2}</div>
                <div class="team-players">{players_str(sq2)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── PODIO ───────────────────────────────────────────────────────────────────

def render_podio(state, podio):
    """podio = [(pos, sq_id), ...]"""
    def sq_info(sid):
        sq = get_squadra_by_id(state, sid)
        from data_manager import get_atleta_by_id
        if not sq: return "?", "?"
        names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
        return sq["nome"], " / ".join(names)
    
    podio_dict = {pos: sid for pos, sid in podio}
    
    items = []
    for pos in [2, 1, 3, 4]:
        if pos in podio_dict:
            nome_sq, players = sq_info(podio_dict[pos])
            items.append((pos, nome_sq, players))

    html = '<div class="podio-container">'
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4º"}
    for pos, nome_sq, players in items:
        css = f"podio-{pos}"
        medal = medals.get(pos, str(pos))
        html += f"""
        <div class="podio-step {css}">
            <div class="podio-name">{nome_sq}</div>
            <div style="font-size:0.7rem;color:rgba(0,0,0,0.7);margin-top:2px">{players}</div>
            <div class="podio-rank">{medal}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── WINNER BANNER ───────────────────────────────────────────────────────────

def render_winner_banner(state, vincitore_sq_id):
    sq = get_squadra_by_id(state, vincitore_sq_id)
    if not sq: return
    from data_manager import get_atleta_by_id
    names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
    st.markdown(f"""
    <div class="winner-banner">
        <div class="winner-title">🏆 Campioni del Torneo 🏆</div>
        <div class="winner-name">{sq['nome']}</div>
        <div class="winner-players">{' & '.join(names)}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── CAREER CARD (FC26 Ultimate Team style) ───────────────────────────────────

def render_career_card(atleta):
    """Carta dinamica FC26 in base a Overall; sotto la griglia statistiche."""
    if not atleta:
        st.info("Seleziona un atleta per vedere la scheda.")
        return
    photo_url = atleta.get("foto_url") or atleta.get("photo_url")  # opzionale, non in schema
    card_html = render_player_card_html(atleta, photo_url=photo_url)
    st.markdown(card_html, unsafe_allow_html=True)

    s = atleta.get("stats", {})
    quoziente = round(s.get("punti_fatti", 0) / max(s.get("set_vinti", 1), 1), 2)
    win_rate = round(s.get("vittorie", 0) / max(s.get("tornei", 1), 1) * 100, 1)
    nome_safe = (atleta.get("nome") or "Atleta").replace("<", "&lt;").replace(">", "&gt;")

    st.markdown(f"""
    <div class="career-card" style="margin-top:16px">
        <div class="career-name">📊 Dettaglio statistiche — {nome_safe}</div>
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-value">{s.get('tornei', 0)}</div><div class="stat-label">Tornei</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--green)">{s.get('vittorie', 0)}</div><div class="stat-label">Vinti</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--accent-red)">{s.get('sconfitte', 0)}</div><div class="stat-label">Persi</div></div>
            <div class="stat-box"><div class="stat-value">{s.get('set_vinti', 0)}</div><div class="stat-label">Set Vinti</div></div>
            <div class="stat-box"><div class="stat-value">{s.get('set_persi', 0)}</div><div class="stat-label">Set Persi</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--accent-gold)">{quoziente}</div><div class="stat-label">Quot. Punti/Set</div></div>
            <div class="stat-box"><div class="stat-value">{win_rate}%</div><div class="stat-label">Win Rate</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
