# Quiz – Anpassungen

---

## App-Beschreibung

Die **Quiz-App** ist eine eigenständige, rein statische Web-Anwendung ohne externe
Abhängigkeiten. Sie läuft direkt im Browser aus dem lokalen Dateisystem oder über
einen einfachen HTTP-Server.

| Eigenschaft | Wert |
|-------------|------|
| Projektordner | `C:\Daten\Projects\quiz` |
| Einstiegspunkt | `index.html` |
| Lokaler Server | `python -m http.server 4174` → `http://localhost:4174/` |
| Veröffentlichung | `.\publish-to-weberding.ps1` → `weberding\quiz` |
| Technologie | Reines HTML/CSS/JavaScript, kein Build-Schritt |

### Modi

**Duo** – Richtig/Falsch-Modus: Eine Aussage wird angezeigt, der Spieler entscheidet
„Richtig" oder „Falsch". Themendateien: `td_[thema].htm`.

**Quattro** – Multiple-Choice-Modus: Eine Frage mit vier Antwortmöglichkeiten (A–D).
Nur eine Antwort ist korrekt. Themendateien: `tq_[thema].htm`.

---

## Quiz-Skills

Für die Pflege der App stehen zwei KI-Assistenten zur Verfügung, die dieselben
Befehle in ihrem jeweiligen Format bereitstellen.

### Claude Code Skill – `/quiz`

Definiert in `SKILL.md` im Projektstamm. Wird in Claude Code mit dem Präfix `/quiz`
aufgerufen.

| Befehl | Wirkung |
|--------|---------|
| `/quiz duo [thema] create` | 100 Richtig/Falsch-Fragen erstellen |
| `/quiz quattro [thema] create` | 100 Multiple-Choice-Fragen erstellen |
| `/quiz [duo\|quattro] [thema] check` | Strukturelle Validierung |
| `/quiz [duo\|quattro] [thema] check count:nnn` | Validierung mit Mindestanzahl |
| `/quiz all check` | Alle Kataloge prüfen |
| `/quiz [duo\|quattro] [thema] check-lang` | Sprachprüfung (Rechtschreibung, Grammatik, Interpunktion) |
| `/quiz all check-lang` | Alle Kataloge sprachlich prüfen |
| `/quiz publish` | App nach `weberding\quiz` synchronisieren |
| `/quiz ?` | Hilfe anzeigen |

### ChatGPT Codex Agent – `$quiz`

Definiert in `agents/openai.yaml`. Identische Funktionen unter dem Präfix `$quiz`.
Fallback-Lösung, wenn Claude-Token-Kontingent überschritten.

### Skill quiz-anpassungen – `/quiz-anpassungen`

Definiert in `.claude/skills/quiz-anpassungen/SKILL.md`. Pflegt diese Dokumentation:
fügt neue Entwicklungsphasen chronologisch ein und hält `Anpassungen.md` und
`Anpassungen.html` synchron.

---

## Themendateien

### Struktur

Alle Themendateien sind vollständige HTML-Seiten mit einem eingebetteten
`<div id="question_data">`-Block, der die Fragen als JSON-Array enthält.
Die `index.html` lädt die gewählte Themendatei per `fetch()` und parst den JSON-Block.

### Duo-Format (`td_[thema].htm`)

```html
<div id="question_data">
[
  {
    "aussage": "Eine klare, faktisch prüfbare Aussage.",
    "antwort": true,
    "grad": "leicht"
  }
]
</div>
```

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `aussage` | String | Aussagesatz (kein Fragesatz), endet mit `.` oder `!` |
| `antwort` | Boolean | `true` = Aussage ist korrekt, `false` = falsch |
| `grad` | String | `"leicht"`, `"mittel"` oder `"schwer"` |

### Quattro-Format (`tq_[thema].htm`)

```html
<div id="question_data">
[
  {
    "frage": "Welche Antwort ist richtig?",
    "antworten": ["Antwort A", "Antwort B", "Antwort C", "Antwort D"],
    "richtig": 0,
    "grad": "leicht"
  }
]
</div>
```

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `frage` | String | Fragesatz, endet mit `?` |
| `antworten` | Array[4] | Genau vier eindeutige, nichtleere Antwortoptionen |
| `richtig` | Integer | Index 0–3 der korrekten Antwort |
| `grad` | String | `"leicht"`, `"mittel"` oder `"schwer"` |

### Validierung

Das Skript `scripts/quiz_tool.py` prüft alle Kataloge:

```
python -B scripts\quiz_tool.py all check          # strukturell
python -B scripts\quiz_tool.py all check --lint   # + heuristischer Sprachlint
```

Der Lint prüft zusätzlich Großschreibung am Satzanfang, korrekte Satzzeichen am Ende,
Textlängen, doppelte Leerzeichen, HTML-Tags und Platzhaltertext.

### Vorhandene Kataloge

| Datei | Modus | Thema |
|-------|-------|-------|
| `td_auswahlverfahren.htm` | Duo | Beamten-Auswahlverfahren (LPA Bayern) |
| `td_bayern.htm` | Duo | Bayern allgemein |
| `td_deutsch.htm` | Duo | Deutsche Sprache |
| `td_geschichte.htm` | Duo | Deutsche Geschichte |
| `td_pflanzen.htm` | Duo | Pflanzen |
| `td_poolbillardregeln.htm` | Duo | Pool-Billard-Regeln |
| `td_society.htm` | Duo | Gesellschaft & Kultur |
| `td_tiere.htm` | Duo | Tiere |
| `tq_auswahlverfahren.htm` | Quattro | Beamten-Auswahlverfahren (LPA Bayern) |
| `tq_poolbillardregeln.htm` | Quattro | Pool-Billard-Regeln |

---

<details>
<summary><strong>Entwicklungsphasen 1–11</strong></summary>

## Phase 1 – Initiales Quiz-Projekt (8. Mai 2026)

Auslagerung der Quiz-Komponente aus dem Weberding-Hauptprojekt in einen
eigenständigen Projektordner mit eigenem Git-Repository.

### 1.1  Projektstruktur

**Dateien:** `index.html`, `scripts/quiz_tool.py`, `SKILL.md`, `agents/openai.yaml`,
`publish-to-weberding.ps1`, `.gitignore`, `README.md`

Acht Duo-Themendateien (`t_*.htm`) aus dem Weberding-Projekt übernommen.
Sounddateien für Richtig/Falsch-Feedback kopiert.

### 1.2  quiz_tool.py

Erstes Validierungsskript: JSON-Extraktion, Pflichtfelder, Datentypen,
Duplikaterkennung, Antwortbalance-Prüfung (40–60 % true).

### 1.3  Publish-Script

`publish-to-weberding.ps1` synchronisiert per robocopy nach
`C:\Daten\Projects\weberding\quiz` (ohne `.git` und `__pycache__`).

---

## Phase 2 – Duo/Quattro-Modi (8. Mai 2026)

Einführung des zweiten Quiz-Modus: **Quattro** (Multiple-Choice mit vier Antworten A–D).
Umbenennung aller Themendateien auf das neue Präfixschema.

### 2.1  Dateinamen-Schema

Alle bisherigen `t_*.htm` umbenannt in `td_*.htm` (Duo).
Zwei neue Quattro-Dateien erstellt: `tq_auswahlverfahren.htm`, `tq_poolbillardregeln.htm`.

### 2.2  index.html – Moduswahl

Neue Moduswahl Duo/Quattro in der Oberfläche. Separate Darstellung für Quattro-Antworten
(A–D-Buttons statt zwei großer Schaltflächen).

### 2.3  quiz_tool.py – Refaktorierung

Validator für beide Modi (`validate_duo`, `validate_quattro`) mit gemeinsamer
`validate()`-Dispatcher-Funktion. Automatische Modus-Erkennung anhand des Dateinamenpräfixes.

---

## Phase 3 – Umlaut-Fixes & Quattro-Layout (9. Mai 2026)

Behebung korrumpierter Umlaute in den Quattro-Katalogen und Layout-Korrektur
der Antwort-Buttons.

### 3.1  Umlaut-Korrekturen

In `tq_auswahlverfahren.htm` und `tq_poolbillardregeln.htm` alle durch `?`
ersetzten Umlaute (ä, ö, ü, ß etc.) wiederhergestellt.

### 3.2  Quattro-Button-Ausrichtung

CSS-Anpassung `.btn_quattro`: `justify-content: flex-start` und `padding-inline`
ergänzt, damit A–D-Labels linksbündig erscheinen.

---

## Phase 4 – Schreibweise & Icon-Einheitlichkeit (9. Mai 2026)

Einheitliche Schreibweise „Quattro" (zuvor teils „Quattro") und konsistente
Darstellung der A–D-Kreissymbole.

### 4.1  Schreibweise vereinheitlicht

Alle Vorkommen von „Quattro"/„quattro" in CSS-Klassen, JS-Variablen, HTML-Option
und Anzeigetext auf „Quattro"/„quattro" korrigiert.

### 4.2  A–D-Icon-Größe

Explizites `font-size: 1.15rem` und `flex-shrink: 0` für die Buchstaben-Kreise,
damit alle vier Symbole identische Größe haben.

### 4.3  Antworttext-Layout

Antworttext mit `flex: 1` linksbündig ausgerichtet. Kleinere `font-size` für
längere Antworttexte im Quattro-Modus.

---

## Phase 5 – Quellenangaben entfernt (9. Mai 2026)

Bereinigung der Quizfragen: Alle Verweise auf LPA-Quellen aus den Fragetexten
entfernt, da diese in einem Quiz-Kontext irrelevant und irreführend sind.

### 5.1  Quellenverweise

**Datei:** `tq_auswahlverfahren.htm`

22 Vorkommen von „laut LPA", „laut FAQ", „laut LPA-FAQ", „nach den LPA-FAQ" und
„steht in den FAQ" entfernt. Wo der Verweis das Hauptprädikat war (Frage 92),
wurde die Frage zu „ist korrekt?" umformuliert.

---

## Phase 6 – Skill quiz konsolidiert & erweitert (9. Mai 2026)

Vollständige Überarbeitung des Quiz-Skills: Sprachlint im Python-Tool, neuer
`check-lang`-Befehl, `publish`-Befehl, vollständige ChatGPT-Codex-Implementierung
und diese Anpassungs-Dokumentation.

### 6.1  quiz_tool.py – Heuristischer Sprachlint

Neue Funktion `lint_text()` mit heuristischen Sprachprüfungen:
Großschreibung am Satzanfang, Satzzeichen am Ende (Aussagen `.`/`!`, Fragen `?`),
Textlänge (10–250 Zeichen), doppelte Leerzeichen, HTML-Tags, Platzhaltertext.

Neues Flag `--lint` für den `check`-Befehl. `create` aktiviert Lint automatisch.

### 6.2  SKILL.md – check-lang & publish

Neuer Befehl `/quiz [duo|quattro] [thema] check-lang`: zweistufige Sprachprüfung –
zuerst heuristischer Lint via Python-Tool, dann inhaltlich-sprachliche Prüfung
durch Claude (Rechtschreibung, Grammatik, Interpunktion mit direkter Korrektur).

Neuer Befehl `/quiz publish`: ruft `publish-to-weberding.ps1` auf.

### 6.3  agents/openai.yaml – vollständige ChatGPT-Implementierung

Von 4 Zeilen auf vollständige Instruktionen erweitert: alle Befehle (`$quiz`-Präfix),
Datenstrukturen, create/check/check-lang/publish-Workflows – als Fallback für
ChatGPT Codex bei überschrittenem Claude-Token-Kontingent.

### 6.4  Anpassungen-Dokumentation

`Anpassungen.md` und `Anpassungen.html` erstellt. Skill `quiz-anpassungen`
(`/quiz-anpassungen`) für die chronologische Fortschreibung dieser Dokumentation.

---

## Phase 7 – Open Trivia DB-Integration & Publish-Workflow (9. Mai 2026)

Anbindung der externen Fragedatenbank „Open Trivia DB" als zweite Fragequelle
sowie Einführung eines zweistufigen Publish-Workflows über einen `out/`-Zwischenordner.

### 7.1  index.html – Open Trivia DB-Anbindung

**Datei:** `index.html`

Neue Quellenauswahl im Control Dock: Dropdown „Quelle" mit den Optionen **Lokal**
(bisheriger Betrieb) und **Open Trivia DB** (externe API).

Bei OTDB-Modus wird das Thema-Dropdown ausgeblendet und durch ein Kategorie-Dropdown
ersetzt, das die Kategorien der Open Trivia DB dynamisch lädt.

Neue JavaScript-Funktionen:
- `quelle_geaendert()` – schaltet zwischen lokalem und OTDB-Modus um
- `otdb_token_holen()` – holt einen Session-Token (wird in `sessionStorage` gecacht)
- `lade_otdb_kategorien()` – füllt das Kategorie-Dropdown per API
- `lade_otdb_fragen()` – ruft Fragen ab, übersetzt OTDB-Format in internes Format
- `htmlDecode()` – dekodiert HTML-Entities in OTDB-Antworttext
- `shuffle()` – mischt Antwortoptionen zufällig

TTS-Sprache wird pro Quelle gewählt: Englisch (`en-US`) für OTDB, Deutsch (`de-DE`)
für lokale Fragen. Das Control Dock Grid wurde auf 6 Spalten erweitert (Quelle,
Modus, Thema/Kategorie, Level, Anzahl, Start).

### 7.2  scripts/quiz_tool.py – publish-Befehl

**Datei:** `scripts/quiz_tool.py`

Neuer Befehl `publish`: befüllt den `out/`-Unterordner mit allen
webserver-relevanten Dateien (`index.html`, `Anpassungen.html`, `td_*.htm`,
`tq_*.htm`, Sounddateien, `media/`). Entwicklungs- und Build-Artefakte
(`.git`, `__pycache__`, Python-Skripte) bleiben im Projektstamm.

Aufruf: `python -B scripts\quiz_tool.py publish`

### 7.3  publish-to-weberding.ps1 – out/-Workflow

**Datei:** `publish-to-weberding.ps1`

Publish-Quelle ist jetzt der `out/`-Unterordner statt des Projektstamms.
Das Script bricht ab, wenn `out/` fehlt, und gibt einen Hinweis, zuerst
`quiz_tool.py publish` auszuführen. Der zweistufige Ablauf lautet:

1. `python -B scripts\quiz_tool.py publish` → befüllt `out/`
2. `.\publish-to-weberding.ps1` → kopiert `out/` nach `weberding\quiz`

### 7.4  README.md – Schreibweise

**Datei:** `README.md`

Tippfehler „Quatro" in zwei Überschriften und einem Befehlsbeispiel durch
die korrekte Schreibweise „Quattro" ersetzt.

---

## Phase 8 – Fragenkataloge überarbeitet (9. Mai 2026)

Ausgewählte Duo-Fragen in mehreren Katalogen wurden von `true` auf `false`
umgestellt, um eine bessere Balance zwischen korrekten und falschen Aussagen
zu erreichen. Die Quattro-Falschantworten im Auswahlverfahren-Katalog wurden
inhaltlich überarbeitet.

### 8.1  Duo-Kataloge – false-Answer-Diversifizierung

**Dateien:** `td_deutsch.htm`, `td_geschichte.htm`, `td_society.htm`, `td_auswahlverfahren.htm`

Bei zuvor rein wahren Aussagen (`"antwort": true`) wurde der Aussagetext so
verfälscht, dass die Aussage sachlich falsch ist, und `"antwort"` auf `false`
gesetzt. Ziel: ausgeglichene true/false-Verteilung in jedem Katalog.

| Datei | Umgestellte Fragen |
|---|---|
| `td_deutsch.htm` | 8 (Schreibung ß/ss, Wortarten, Satzanfang) |
| `td_geschichte.htm` | 6 (Ritter, Burgen, Mittelalter, Martin Luther) |
| `td_society.htm` | 6 (Begrüßung, Familie, Rathaus, Post, Demokratie) |
| `td_auswahlverfahren.htm` | 5 (Schulnoten, Auswahlprüfung, Verfahren, Vorstellungsgespräch, Mathematik) |

### 8.2  tq_auswahlverfahren.htm – Falschantworten überarbeitet

**Datei:** `tq_auswahlverfahren.htm`

Bei 4 Quattro-Fragen wurden Falschantworten durch realistischere Alternativen
ersetzt, die näher am tatsächlichen LPA-Verfahren formuliert sind und damit
schwerer durch Ausschlussverfahren zu erkennen sind. Eine Frageformulierung
wurde präzisiert.

---

## Phase 9 – Sprachliche Korrekturen check-lang (9. Mai 2026)

Vollständige Sprachprüfung (`/quiz all check-lang`) aller Kataloge: alle acht
Duo-Kataloge ohne Befund, zwei Quattro-Kataloge mit insgesamt sechs Fehlern behoben.

### 9.1  tq_auswahlverfahren.htm – fünf Korrekturen

**Datei:** `tq_auswahlverfahren.htm`

| Frage | Feld | Vorher | Nachher |
|---|---|---|---|
| 7 | antwort[1] | „Eine gültigen Reisepass" | „Einen gültigen Reisepass" |
| 11 | antwort[0] | „über 30 Prozent" | „Über 30 Prozent" |
| 11 | antwort[1] | „ca. 10 bis 20 Prozent" | „Etwa 10 bis 20 Prozent" |
| 17 | antwort[1] | „Nach Auslösen den Senden-Buttons ist automatisch angemeldet." | „Nach Auslösen des Senden-Buttons ist man automatisch angemeldet." |
| 19 | frage | „Muss man die Bewerbung beim Polizeivollzugsdienst…" | „Muss man beim Polizeivollzugsdienst…" |

### 9.2  tq_poolbillardregeln.htm – ein Platzhalter ersetzt

**Datei:** `tq_poolbillardregeln.htm`

Frage 3, antwort[2] enthielt Meta-Text aus dem Erstellungsprozess
(„Es gibt nur wahre und falsche Antworten."), der nie durch eine echte
Falschantwort ersetzt wurde. Ersetzt durch:
„Das Spiel endet, wenn zuerst die 9 versenkt wird."

---

## Phase 10 – GitHub-Publish & .gitignore (9. Mai 2026)

Erweiterung des Publish-Workflows um einen GitHub-Schritt sowie Pflege
der `.gitignore`.

### 10.1  SKILL.md – publish um Schritt 3 erweitert

**Datei:** `SKILL.md`

Der `publish`-Abschnitt hat jetzt drei statt zwei Schritte. Schritt 3 stagt
alle Quelldateien (ohne `out/` und `.claude/`), leitet eine kontextbasierte
Commit-Message aus dem Konversationsverlauf ab und pusht auf
`origin master` → `https://github.com/chrisgitti/quiz`.

### 10.2  .gitignore – out/ ausgeschlossen

**Datei:** `.gitignore`

`out/` als Build-Artefakt ergänzt, damit das befüllte Publish-Verzeichnis
nicht versehentlich ins Repository gelangt.

---

## Phase 11 – Online-Spiel-Modus (9. Mai 2026)

Realisierung des geplanten Echtzeit-Mehrspieler-Modus. Neues GitHub-Projekt `quiz-server` mit Node.js-WebSocket-Server sowie vollständige Integration in `index.html`.

### 11.1  quiz-server – Node.js + Socket.IO

**Verzeichnis:** `C:\Daten\Projects\quiz-server`

Neues Projekt mit `server.js`, `package.json`, `.gitignore`. Dependencies: `express ^4.19.2`, `socket.io ^4.7.5`. Deployment-Ziel: Render.com Free-Tier.

**Socket.IO-Ereignisse (Client → Server):**

| Event | Payload | Beschreibung |
|---|---|---|
| `raum_erstellen` | `{ modus, name }` | Host erstellt Raum, erhält 6-stelligen Code |
| `raum_beitreten` | `{ code, name }` | Gast tritt bei |
| `spiel_starten` | `{ fragen }` | Host sendet Fragen (max. 50), Spiel beginnt |
| `antwort_senden` | `{ antwort_index }` | Antwort eines Spielers |

**Socket.IO-Ereignisse (Server → Client):**

| Event | Payload | Beschreibung |
|---|---|---|
| `raum_erstellt` | `{ code }` | Bestätigung Raumcode |
| `raum_beigetreten` | `{ code, modus }` | Bestätigung Beitritt |
| `spieler_liste` | Array | Live-Spielerliste bei jeder Änderung |
| `frage` | `{ index, total, text, antworten, modus }` | Nächste Frage synchron an alle |
| `countdown` | `{ sekunden }` | Sekundenweise Countdown (15 s pro Frage) |
| `antwort_bestaetigt` | `{ korrekt, antwort_index }` | Antwort-Rückmeldung an Einzelspieler |
| `aufloesung` | `{ richtig_index, scores }` | Richtige Antwort + Zwischenstand |
| `spiel_ende` | `{ rangliste }` | Endrangliste, Raum wird gelöscht |
| `raum_geschlossen` | `{ meldung }` | Host hat verlassen |
| `fehler` | `{ meldung }` | Fehlermeldung |

**Spielmechanik:**
- Punkte: 1 000 Basispunkte + bis zu 500 Schnelligkeitsbonus (proportional zur Restzeit)
- Timer: 15 s pro Frage, serverseitig getaktet
- Auflösungspause: 3,5 s zwischen Fragen
- Räume ausschließlich im Arbeitsspeicher (keine Datenbank, keine Nutzerkonten)
- Rate-Limiting: max. 5 Räume/Min. pro IP
- Max. 8 Spieler pro Raum
- Inaktivitäts-Timeout: 30 Min.
- CORS: nur `weberding.de` und `localhost`

### 11.2  index.html – Online-Option und Overlay-UI

**Datei:** `index.html`

Dritte Quellenoption „Online" im Quelle-Dropdown. Beim Auswählen öffnet sich ein modales Overlay mit sechs Panels:

| Panel-ID | Beschreibung |
|---|---|
| `op_start` | Wahl: Raum erstellen oder beitreten |
| `op_host_erstellen` | Name eingeben, aktuelles Thema anzeigen, Raum erstellen |
| `op_host_warten` | Raumcode (groß, cyan), Live-Spielerliste, „Spiel starten"-Button |
| `op_gast_beitreten` | Code + Name eingeben, Beitreten-Button |
| `op_gast_warten` | Warteraum mit Live-Spielerliste |
| `op_rangliste` | Endrangliste mit Medaillen-Emojis 🥇🥈🥉 |

**Neue HTML-Elemente in `index.html`:**
- `timer_row` – farbiger Countdown-Balken unterhalb der Fortschrittsleiste (CSS-Transition)
- `live_score_panel` – Zwischenstand nach jeder Frage (sortiert nach Punkten)
- `online_overlay` – `position:fixed`, `backdrop-filter:blur`, außerhalb von `app_shell`

**Neue JS-Funktionen:**
- `online_verbinden()` – lädt Socket.IO 4.7.5 lazy vom CDN, stellt Verbindung her
- `registriere_socket_events()` – alle Server-Event-Handler (einmalig pro Socket)
- `op_host_erstellen()` – Verbindung + `raum_erstellen` senden
- `op_gast_beitreten()` – Code validieren, Verbindung + `raum_beitreten` senden
- `op_spiel_starten()` – Themendatei laden, Level/Anzahl-Filter anwenden, mischen, als Fragen-Array an Server senden
- `starte_online_timer(n)` / `stoppe_online_timer()` – CSS-Transition-Timer (requestAnimationFrame)
- `online_beenden()` / `online_beenden_still()` – Socket trennen, Overlays schließen, Quelle zurücksetzen
- `online_zeige_fehler(text)` – Fehlermeldung im Overlay, automatisch nach 5 s ausgeblendet

**Geänderte JS-Funktionen:**
- `starte_quiz()` – Online-Modus öffnet Overlay statt Quiz zu starten
- `quelle_geaendert()` – neuer `online`-Branch: Overlay öffnen, lokale Daten vorladen; `else`-Branch trennt Socket und schließt Overlays
- `pruefe_user_antwort()` – bei Online-Quelle: `antwort_senden` an Server statt lokaler Auswertung

**Server-URL (Konstante `ONLINE_SERVER_URL` in `index.html`):**
- `localhost` / `127.0.0.1` → `http://localhost:3010`
- Produktion → `https://quiz-server.onrender.com` *(nach Render-Deployment anpassen)*

</details>

---

## Sonstiges

_Raum für aktuelle Anmerkungen – kann jederzeit überschrieben werden._

### Render.com-Deployment – Status

✅ GitHub-Repo `chrisgitti/quiz-server` angelegt und gepusht  
✅ Render.com Web Service eingerichtet – Live-URL: `https://quiz-server-rjv7.onrender.com`  
✅ `ONLINE_SERVER_URL` in `index.html` auf Render-URL gesetzt  
✅ `/quiz publish` + GitHub-Push abgeschlossen  

### Offener Punkt: Render.com-Plan

Render.com Workspace Pro ($25/Monat) wurde gebucht, um den Timeout-on-first-Request der Billard-App zu vermeiden. Für den Quiz-Server (zweiter Webservice) wird noch ein Service-Plan gewählt ($0 Free / $7 Starter / $25 Standard).

Empfehlung: Starter ($7/Monat) pro Service, Hobby-Workspace (kostenlos) – ergibt $14/Monat statt $39/Monat. Prüfen ob Pro-Workspace wirklich benötigt wird.
