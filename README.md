# 🏐 Beach Volley Tournament Manager Pro — BVL 4.0+

App professionale per la gestione di tornei di beach volley con UI stile DAZN e **carte giocatori in stile FC26 Ultimate Team**.

## 🚀 Avvio Rapido

```bash
cd BVL4.0+
pip install -r requirements.txt
streamlit run app.py
```

**Dove vedere le carte carriera FC26:** in sidebar clicca **👤 Profili Giocatori** (sempre attivo). Oppure vai in **🏆 Proclamazione** e apri il tab **👤 Schede Carriera**. Servono almeno atleti inseriti in Setup.

## 📁 Architettura File

```
BVL4.0+/
│
├── app.py                  ← Entry point + routing fasi + sidebar + tema
├── data_manager.py         ← Modelli dati, persistenza JSON, gironi/BYE/bracket
├── ui_components.py        ← CSS DAZN + carte FC26 + get_card_style(overall)
├── fase_setup.py           ← Fase 1: Configurazione + gironi/passaggio/girone unico
├── fase_gironi.py          ← Fase 2: Gironi + scoreboard live + classifiche
├── fase_eliminazione.py    ← Fase 3: Semifinali + Finale 1-2 e 3-4 + BYE
├── fase_proclamazione.py   ← Fase 4: Podio (1º–4º) + ranking + Profili Giocatori
│
├── requirements.txt
├── README.md
└── beach_volley_data.json  ← Generato automaticamente al primo avvio
```

## 🔄 Flusso Dati

```
Setup → Gironi → Eliminazione → Proclamazione
  ↓        ↓           ↓              ↓
JSON ←── JSON ←──── JSON ←────── JSON (autosave)
  ↓
atleti[] / squadre[] / gironi[] / bracket[] / ranking_globale[]
```

## ✅ Funzionalità Implementate

### 1. Architettura & Fasi
- [x] Passaggio blindato tra fasi: Setup → Gironi → Eliminazione → Proclamazione
- [x] Navigazione sidebar con fasi bloccate (non si può saltare avanti)
- [x] Iscrizione squadre con ricerca atleti da tendina
- [x] Toggle ON/OFF nome squadra automatico
- [x] Scelta tabellone (Gironi+Playoff / Doppia Eliminazione)
- [x] Set Unico o Best of 3, punteggio max configurabile

### 2. UI & Scoreboard Stile DAZN
- [x] Dark Mode con CSS custom (colori #0a0a0f, red #e8002d, blue #0070f3)
- [x] Match card orizzontali con colori Rosso (sq1) e Azzurro (sq2)
- [x] Scoreboard live per ogni match con inserimento set e parziali
- [x] Campo "in battuta" per ogni match
- [x] Tasto "Conferma Risultato" che blocca i dati e aggiorna classifica

### 3. Simulatore Avanzato
- [x] "Simula Risultati" con punteggi realistici (scarto 2 punti)
- [x] Tie-break automatico in Best of 3 (terzo set a 15)
- [x] Toggle ON/OFF "Invia dati simulati al Ranking"

### 4. Ranking & Carriera Atleta
- [x] Animazione st.balloons() alla proclamazione vincitori
- [x] Banner dorato animato con i campioni
- [x] Podio grafico 1°/2°/3° con stili differenziati
- [x] Trasferimento automatico dati al Ranking globale
- [x] Scheda carriera atleta: statistiche, quoziente punti/set
- [x] Grafico st.line_chart() andamento posizioni

### 5. Persistenza
- [x] Autosave JSON ad ogni ciclo dell'app
- [x] Salvataggio esplicito ad ogni "Conferma Risultato"
- [x] Pulsante "Salva" manuale in sidebar
- [x] Reset torneo mantenendo atleti e ranking storico
- [x] File: beach_volley_data.json

### 6. BVL 4.0+ — Carte FC26 e torneo avanzato
- [x] **Carte Profili Giocatori** in stile FC26 Ultimate Team (HTML/CSS custom, 11 tier da Bronzo a GOAT)
- [x] Overall 40–99 calcolato da tornei/vittorie/set/punti; nuovi giocatori = Overall 40 Bronzo Raro
- [x] **Tema** in sidebar (Scuro DAZN, Rosso DAZN, Blu scuro) senza crash
- [x] **Gironi**: numero gironi, squadre che passano, criterio (classifica/avulsa), **Girone unico** all'italiana
- [x] **BYE** automatico e vittorie a tavolino quando le qualificate sono dispari
- [x] **Semifinali** e **Finale 1º-2º** e **Finale 3º-4º** con podio a 4 posti
- [x] Nessuna stringa di codice in vista (storico "4º posto", match card BYE/squadra mancante)

## 🎨 Design System

- **Font**: Barlow Condensed (display) + Barlow (body)
- **Background**: #0a0a0f (primario), #13131a (card), #1a1a24 (secondary)
- **Accent Red**: #e8002d — Squadra 1
- **Accent Blue**: #0070f3 — Squadra 2
- **Gold**: #ffd700 — Campione/Ranking
- **Green**: #00c851 — Vittorie/Conferme
