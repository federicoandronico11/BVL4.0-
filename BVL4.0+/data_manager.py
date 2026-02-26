"""
data_manager.py — Gestione persistenza JSON e modelli dati
"""
import json, os, random
from datetime import datetime
from pathlib import Path

DATA_FILE = "beach_volley_data.json"

# ─── STRUTTURA DATI DEFAULT ──────────────────────────────────────────────────

def empty_state():
    return {
        "fase": "setup",          # setup | gironi | eliminazione | proclamazione
        "torneo": {
            "nome": "",
            "tipo_tabellone": "Gironi + Playoff",   # o "Doppia Eliminazione" o "Girone Unico"
            "formato_set": "Set Unico",              # o "Best of 3"
            "punteggio_max": 21,
            "data": str(datetime.today().date()),
            "num_gironi": 2,
            "squadre_per_girone": 0,       # 0 = auto da num_gironi e n squadre
            "passano_per_girone": 2,        # quante squadre passano per girone
            "criterio_passaggio": "classifica",  # "classifica" | "avulsa"
            "girone_unico": False,          # True = girone unico all'italiana
        },
        "theme": "dazn_dark",     # tema UI (dazn_dark, ecc.) — non tocca DB
        "atleti": [],             # lista globale atleti: {id, nome, stats}
        "squadre": [],            # {id, nome, atleti:[id,id]}
        "gironi": [],             # [{nome, squadre:[id], partite:[...]}]
        "bracket": [],            # partite eliminazione diretta
        "ranking_globale": [],    # storico tornei per atleta
        "vincitore": None,
        "simulazione_al_ranking": True,
    }

# ─── LOAD / SAVE ─────────────────────────────────────────────────────────────

def load_state():
    base = empty_state()
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in base.items():
            data.setdefault(k, v)
        for tk, tv in base["torneo"].items():
            data["torneo"].setdefault(tk, tv)
        return data
    return base

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ─── ATLETI ──────────────────────────────────────────────────────────────────

def new_atleta(nome):
    return {
        "id": f"a_{nome.lower().replace(' ','_')}_{random.randint(1000,9999)}",
        "nome": nome,
        "stats": {
            "tornei": 0,
            "vittorie": 0,
            "sconfitte": 0,
            "set_vinti": 0,
            "set_persi": 0,
            "punti_fatti": 0,
            "punti_subiti": 0,
            "storico_posizioni": [],   # [(torneo_nome, posizione)]
        }
    }

def get_atleta_by_id(state, aid):
    for a in state["atleti"]:
        if a["id"] == aid:
            return a
    return None


def compute_overall(atleta):
    """
    Calcola Overall 40-99 da trofei, tornei, medaglie, set e punti.
    Nuovi giocatori (nessun torneo) = 40.
    """
    s = atleta.get("stats", {})
    tornei = s.get("tornei", 0)
    vittorie = s.get("vittorie", 0)
    set_vinti = s.get("set_vinti", 0)
    punti_fatti = s.get("punti_fatti", 0)
    storico = s.get("storico_posizioni", [])

    if tornei == 0 and vittorie == 0 and set_vinti == 0 and punti_fatti == 0:
        return 40  # Nuovo giocatore: carta Overall 40 Bronzo Raro

    # Punti da medaglie/posizioni (1°=25, 2°=18, 3°=12, altri=3)
    pts_pos = sum({1: 25, 2: 18, 3: 12}.get(pos, 3) for _, pos in storico)
    # Punti da vittorie e set
    pts_vittorie = vittorie * 4
    pts_set = min(set_vinti * 2, 30)
    pts_punti = min(punti_fatti // 20, 25)
    pts_tornei = min(tornei * 3, 20)

    raw = 40 + (pts_pos + pts_vittorie + pts_set + pts_punti + pts_tornei) // 4
    return min(99, max(40, raw))

# ─── SQUADRE ─────────────────────────────────────────────────────────────────

def new_squadra(nome, atleta1_id, atleta2_id):
    return {
        "id": f"sq_{random.randint(10000,99999)}",
        "nome": nome,
        "atleti": [atleta1_id, atleta2_id],
        "punti_classifica": 0,
        "set_vinti": 0,
        "set_persi": 0,
        "punti_fatti": 0,
        "punti_subiti": 0,
        "vittorie": 0,
        "sconfitte": 0,
    }

def get_squadra_by_id(state, sid):
    for s in state["squadre"]:
        if s["id"] == sid:
            return s
    return None

def nome_squadra(state, sid):
    s = get_squadra_by_id(state, sid)
    return s["nome"] if s else "?"

# ─── PARTITE ─────────────────────────────────────────────────────────────────

def new_partita(sq1_id, sq2_id, fase="girone", girone=None, round_elim=0, label_elim=""):
    return {
        "id": f"p_{random.randint(100000,999999)}",
        "sq1": sq1_id,
        "sq2": sq2_id,
        "fase": fase,
        "girone": girone,
        "round_elim": round_elim,   # 0=quarti/semi, 1=semifinali, 2=finali
        "label_elim": label_elim,   # "finale_12" | "finale_34" | ""
        "set_sq1": 0,
        "set_sq2": 0,
        "punteggi": [],
        "in_battuta": 1,
        "confermata": False,
        "vincitore": None,
    }

# ─── SIMULAZIONE ─────────────────────────────────────────────────────────────

def simula_set(pmax, tie_break=False):
    limit = 15 if tie_break else pmax
    a, b = 0, 0
    while True:
        if random.random() > 0.5:
            a += 1
        else:
            b += 1
        if a >= limit or b >= limit:
            if abs(a - b) >= 2:
                return a, b
            if a > limit + 6 or b > limit + 6:
                return (a, b) if a > b else (b, a)

def simula_partita(state, partita):
    torneo = state["torneo"]
    pmax = torneo["punteggio_max"]
    formato = torneo["formato_set"]
    
    if formato == "Set Unico":
        p1, p2 = simula_set(pmax)
        partita["punteggi"] = [(p1, p2)]
        partita["set_sq1"] = 1 if p1 > p2 else 0
        partita["set_sq2"] = 1 if p2 > p1 else 0
    else:  # Best of 3
        sets_1, sets_2 = 0, 0
        punteggi = []
        while sets_1 < 2 and sets_2 < 2:
            tie = (sets_1 == 1 and sets_2 == 1)
            p1, p2 = simula_set(pmax, tie_break=tie)
            punteggi.append((p1, p2))
            if p1 > p2: sets_1 += 1
            else: sets_2 += 1
        partita["punteggi"] = punteggi
        partita["set_sq1"] = sets_1
        partita["set_sq2"] = sets_2
    
    partita["vincitore"] = partita["sq1"] if partita["set_sq1"] > partita["set_sq2"] else partita["sq2"]
    partita["confermata"] = True
    return partita

# ─── CLASSIFICA GIRONE ───────────────────────────────────────────────────────

def aggiorna_classifica_squadra(state, partita):
    """Aggiorna stats squadra dopo conferma risultato."""
    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    if not sq1 or not sq2:
        return

    s1v, s2v = partita["set_sq1"], partita["set_sq2"]
    p1_tot = sum(p[0] for p in partita["punteggi"])
    p2_tot = sum(p[1] for p in partita["punteggi"])

    sq1["set_vinti"] += s1v; sq1["set_persi"] += s2v
    sq2["set_vinti"] += s2v; sq2["set_persi"] += s1v
    sq1["punti_fatti"] += p1_tot; sq1["punti_subiti"] += p2_tot
    sq2["punti_fatti"] += p2_tot; sq2["punti_subiti"] += p1_tot

    if partita["vincitore"] == partita["sq1"]:
        sq1["vittorie"] += 1; sq1["punti_classifica"] += 3
        sq2["sconfitte"] += 1; sq2["punti_classifica"] += 1
    else:
        sq2["vittorie"] += 1; sq2["punti_classifica"] += 3
        sq1["sconfitte"] += 1; sq1["punti_classifica"] += 1

# ─── TRASFERIMENTO RANKING ATLETI ────────────────────────────────────────────

def trasferisci_al_ranking(state, podio):
    """podio = [(1, sq_id), (2, sq_id), (3, sq_id)]"""
    nome_torneo = state["torneo"]["nome"]
    for pos, sq_id in podio:
        sq = get_squadra_by_id(state, sq_id)
        if not sq: continue
        for aid in sq["atleti"]:
            atleta = get_atleta_by_id(state, aid)
            if not atleta: continue
            s = atleta["stats"]
            s["tornei"] += 1
            s["storico_posizioni"].append((nome_torneo, pos))
            s["set_vinti"] += sq["set_vinti"]
            s["set_persi"] += sq["set_persi"]
            s["punti_fatti"] += sq["punti_fatti"]
            s["punti_subiti"] += sq["punti_subiti"]
            if pos == 1: s["vittorie"] += 1
            else: s["sconfitte"] += 1

# ─── GENERAZIONE GIRONI ──────────────────────────────────────────────────────

def genera_gironi(squadre_ids, num_gironi=2, girone_unico=False):
    """
    Distribuisce squadre in gironi. Se girone_unico=True, un solo girone con tutte.
    """
    random.shuffle(squadre_ids)
    gironi = []
    if girone_unico or num_gironi <= 1:
        squadre_girone = list(squadre_ids)
        partite = []
        for j in range(len(squadre_girone)):
            for k in range(j + 1, len(squadre_girone)):
                partite.append(new_partita(squadre_girone[j], squadre_girone[k], "girone", 0))
        gironi.append({
            "nome": "Girone Unico",
            "squadre": squadre_girone,
            "partite": partite,
        })
    else:
        for i in range(num_gironi):
            squadre_girone = squadre_ids[i::num_gironi]
            partite = []
            for j in range(len(squadre_girone)):
                for k in range(j + 1, len(squadre_girone)):
                    partite.append(new_partita(squadre_girone[j], squadre_girone[k], "girone", i))
            gironi.append({
                "nome": f"Girone {'ABCDEFGH'[i]}",
                "squadre": squadre_girone,
                "partite": partite,
            })
    return gironi

# ID squadra fantasma per BYE
BYE_ID = "sq_BYE"


def _classifica_girone(state, girone):
    """Restituisce lista di squadra_id ordinate per classifica (migliori prime)."""
    squadre_dati = []
    for sid in girone["squadre"]:
        sq = get_squadra_by_id(state, sid)
        if sq:
            squadre_dati.append(sq)
    return sorted(
        squadre_dati,
        key=lambda s: (
            -s["punti_classifica"], -s["vittorie"],
            -(s["set_vinti"] - s["set_persi"]),
            -(s["punti_fatti"] - s["punti_subiti"]),
        ),
    )


def genera_bracket_da_gironi(state):
    """
    Qualificate dalle gironi (classifica reale), passano_per_girone per girone.
    Se dispari, BYE: una squadra passa con vittoria a tavolino.
    Restituisce primo round (quarti o semifinali).
    """
    gironi = state["gironi"]
    passano = state["torneo"].get("passano_per_girone", 2)
    teste_di_serie = []
    for g in gironi:
        ordinate = _classifica_girone(state, g)
        for sq in ordinate[:passano]:
            teste_di_serie.append(sq["id"])

    # BYE: se dispari, aggiungi squadra fantasma
    if len(teste_di_serie) % 2 == 1:
        teste_di_serie.append(BYE_ID)

    random.shuffle(teste_di_serie)
    bracket = []
    for i in range(0, len(teste_di_serie), 2):
        a, b = teste_di_serie[i], teste_di_serie[i + 1]
        if a == BYE_ID or b == BYE_ID:
            vincitore = b if a == BYE_ID else a
            p = new_partita(a, b, "eliminazione", round_elim=0)
            p["confermata"] = True
            p["vincitore"] = vincitore
            p["set_sq1"] = 1 if vincitore == a else 0
            p["set_sq2"] = 1 if vincitore == b else 0
            p["punteggi"] = [(21, 0)] if vincitore == a else [(0, 21)]
            bracket.append(p)
        else:
            bracket.append(new_partita(a, b, "eliminazione", round_elim=0))
    return bracket


def aggiungi_semifinali_e_finali(state):
    """
    Quando il round 0 è tutto confermato: aggiunge semifinali (round 1).
    Quando il round 1 è tutto confermato: aggiunge finale 1-2 e finale 3-4 (round 2).
    Chiamata da fase_eliminazione dopo conferma risultato.
    """
    bracket = state["bracket"]
    by_round = {}
    for p in bracket:
        r = p.get("round_elim", 0)
        by_round.setdefault(r, []).append(p)

    max_round = max(by_round.keys()) if by_round else -1
    partite_ultimo = by_round.get(max_round, [])

    if not partite_ultimo or not all(p["confermata"] for p in partite_ultimo):
        return

    vincitori = [p["vincitore"] for p in partite_ultimo]
    perdenti = [p["sq1"] if p["vincitore"] == p["sq2"] else p["sq2"] for p in partite_ultimo]

    if max_round == 0:
        if any(p.get("round_elim") == 1 for p in bracket):
            return
        if len(partite_ultimo) == 4:
            state["bracket"].append(new_partita(vincitori[0], vincitori[1], "eliminazione", round_elim=1))
            state["bracket"].append(new_partita(vincitori[2], vincitori[3], "eliminazione", round_elim=1))
        elif len(partite_ultimo) == 2:
            # 4 squadre: vai direttamente a finale 1-2 e 3-4
            if any(p.get("round_elim") == 2 for p in bracket):
                return
            state["bracket"].append(new_partita(vincitori[0], vincitori[1], "eliminazione", round_elim=2, label_elim="finale_12"))
            state["bracket"].append(new_partita(perdenti[0], perdenti[1], "eliminazione", round_elim=2, label_elim="finale_34"))
    elif max_round == 1:
        if any(p.get("round_elim") == 2 for p in bracket):
            return
        state["bracket"].append(new_partita(vincitori[0], vincitori[1], "eliminazione", round_elim=2, label_elim="finale_12"))
        state["bracket"].append(new_partita(perdenti[0], perdenti[1], "eliminazione", round_elim=2, label_elim="finale_34"))
