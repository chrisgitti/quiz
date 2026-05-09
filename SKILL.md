---
name: quiz
description: Work with the standalone quiz web app in C:\Daten\Projects\quiz. Use when the user invokes /quiz, creates or checks Duo true/false catalogs td_[thema].htm, creates or checks Quattro multiple-choice catalogs tq_[thema].htm, validates count:nnn minimums, checks language quality (spelling, grammar, punctuation), publishes to weberding, or asks for quiz skill help.
---

# Quiz

## Aufruf

| Befehl | Wirkung |
|--------|---------|
| `/quiz ?` | Hilfe anzeigen |
| `/quiz duo [thema] create` | Neue Duo-Datei `td_[thema].htm` mit 100 Richtig/Falsch-Fragen erstellen |
| `/quiz quattro [thema] create` | Neue Quattro-Datei `tq_[thema].htm` mit 100 Multiple-Choice-Fragen erstellen |
| `/quiz [duo\|quattro] [thema] check` | Einzelnen Katalog strukturell prüfen |
| `/quiz [duo\|quattro] [thema] check count:nnn` | Strukturprüfung mit Mindestanzahl `nnn` Fragen |
| `/quiz [duo\|quattro] all check` | Alle Kataloge eines Modus strukturell prüfen |
| `/quiz all check` | Alle Duo- und Quattro-Kataloge strukturell prüfen |
| `/quiz [duo\|quattro] [thema] check-lang` | Einen Katalog sprachlich prüfen (Rechtschreibung, Grammatik, Interpunktion) |
| `/quiz all check-lang` | Alle Kataloge sprachlich prüfen |
| `/quiz publish` | Quiz-App nach `weberding\quiz` synchronisieren und auf GitHub pushen |
| `/quiz update` | Geänderte SKILL.md-Dateien ins globale Plugin-Verzeichnis übertragen |

`[thema]` ist der Dateiname-Suffix ohne Prefix, z. B. `bayern`, `poolbillardregeln` oder `auswahlverfahren`.

## Web-App

Die App liegt im eigenständigen Projektordner `C:\Daten\Projects\quiz`.

- `index.html` – Quiz-Oberfläche mit Moduswahl Duo/Quattro
- `td_[thema].htm` – Duo-Themenkataloge (Richtig/Falsch)
- `tq_[thema].htm` – Quattro-Themenkataloge (vier Antwortmöglichkeiten A–D)
- `scripts/quiz_tool.py` – Validierung und Katalogpflege
- `publish-to-weberding.ps1` – Synchronisiert die App nach `C:\Daten\Projects\weberding\quiz`

## Datenstruktur Duo

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

Pflichtfelder: `aussage` (Behauptung, kein Fragesatz), `antwort` (Boolean), `grad` (`leicht`, `mittel` oder `schwer`).

## Datenstruktur Quattro

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

Pflichtfelder: `frage` (Fragesatz, endet mit `?`), `antworten` (Array mit genau vier eindeutigen Texten), `richtig` (Index 0–3 der korrekten Antwort), `grad`.

## create

Bei `create`:

1. Thema normalisieren: Kleinbuchstaben, Umlaute transliterieren, Sonderzeichen zu `-`.
2. Genau 100 fachlich belastbare deutsche Fragen erzeugen.
3. Schwierigkeitsgrade möglichst gleichmäßig verteilen (je ~33 je Stufe).
4. Keine doppelten oder nahezu identischen Fragen verwenden.
5. Duo: Antworten zwischen `true` und `false` ausbalancieren (40–60 %).
6. Quattro: Vier plausible, eindeutige Antwortoptionen; nur eine korrekt.
7. Aktuelle oder rechtlich/fachlich veränderliche Fakten vorab aus verlässlichen Quellen prüfen.
8. Sprachliche Qualität beim Erzeugen sicherstellen (→ Abschnitt *check-lang*).
9. Fragen als JSON-Datei speichern, dann mit dem Tool schreiben:
   ```
   python -B scripts\quiz_tool.py duo|quattro [thema] create --questions <datei.json>
   ```
   `create` aktiviert automatisch den Sprachlint; Fehler vor dem Schreiben beheben.

## check (strukturelle Validierung)

Ruft `quiz_tool.py` auf und prüft:

- JSON-Struktur, Pflichtfelder, Datentypen
- Fragenanzahl (Zielwert 100 oder `count:nnn`)
- Duplikate (normalisierter Textvergleich)
- Duo: Warnung wenn `aussage` auf `?` endet; Antwortbalance 40–60 %
- Quattro: Eindeutigkeit der vier Antwortoptionen; korrekter Richtig-Index

Mit Flag `--lint` zusätzlich heuristischer Sprachlint:

- Großschreibung am Satzanfang
- Duo-Aussagen enden mit `.` oder `!` (nicht `?`)
- Quattro-Fragen enden mit `?`
- Keine doppelten Leerzeichen
- Keine HTML-Tags im Text
- Kein Platzhaltertext (`[...]`, `XXX`, `TODO`)
- Textlänge: Warnung unter 10 Zeichen oder über 250 Zeichen

Befehle:

```
python -B scripts\quiz_tool.py all check
python -B scripts\quiz_tool.py all check --lint
python -B scripts\quiz_tool.py duo all check
python -B scripts\quiz_tool.py quattro all check
python -B scripts\quiz_tool.py duo [thema] check count:100
python -B scripts\quiz_tool.py duo [thema] check --lint
python -B scripts\quiz_tool.py quattro [thema] check count:100 --lint
```

Gefundene Fehler direkt in JSON, Pflichtfeldern, Datentypen, Antwortanzahl, Indizes oder Duplikaten beheben.

## check-lang (sprachliche Qualitätsprüfung)

Bei `/quiz [duo|quattro] [thema] check-lang` oder `/quiz all check-lang`:

**Schritt 1 – Heuristischer Lint:**

```
python -B scripts\quiz_tool.py [duo|quattro] [thema] check --lint
```

Alle `WARN`- und `ERROR`-Meldungen auswerten und beheben.

**Schritt 2 – Inhaltlich-sprachliche Prüfung durch Claude:**

Datei(en) lesen und jeden Fragetext prüfen:

*Rechtschreibung*
- Korrekte Schreibweise aller Wörter, einschließlich Fachbegriffe
- Korrekte Umlaute (ä, ö, ü, ß) – keine Umschreibungen wie ae, oe außer in Eigennamen
- Keine Tippfehler oder fehlende Buchstaben

*Grammatik*
- Korrekte Satzkonstruktion, Kasus, Numerus, Genus
- Duo-Aussagen: vollständige Aussagesätze (kein Fragesatz, kein Fragment)
- Quattro-Fragen: vollständige Fragesätze, enden mit `?`
- Quattro-Antworten: grammatisch parallel und konsistent innerhalb einer Frage

*Interpunktion*
- Duo-Aussagen enden mit `.` oder `!`
- Quattro-Fragen enden mit `?`
- Kein fehlendes Leerzeichen nach `,`, `;`, `:`
- Keine überflüssigen Leerzeichen vor Satzzeichen
- Korrekte Anführungszeichen (`„…"` für Deutsch), Gedankenstriche, Klammern

**Schritt 3 – Korrekturen:**
- Eindeutige Fehler direkt mit dem Edit-Tool in der Datei korrigieren
- Mehrdeutige Fälle (Stilentscheidungen, Fachbegriffe) erst vorlegen und bestätigen lassen
- Alle Änderungen mit Frage-Nummer und Feldname auflisten

## publish

Bei `/quiz publish` alle drei Schritte ausführen:

**Schritt 1 – `out/` befüllen:**

```
python -B scripts\quiz_tool.py publish
```

Kopiert alle webserver-relevanten Dateien in das Verzeichnis `out/`:

| Quelle | Beschreibung |
|--------|--------------|
| `index.html` | Quiz-Oberfläche |
| `Anpassungen.html` | Entwicklungsdokumentation |
| `td_*.htm` | Alle Duo-Themenkataloge |
| `tq_*.htm` | Alle Quattro-Themenkataloge |
| `*.mp3` | Sounddateien im Projektstamm |
| `media/` | Komplettes Sounddateien-Verzeichnis |

**Schritt 2 – Synchronisieren:**

```powershell
.\publish-to-weberding.ps1
```

Überträgt `out/` nach `C:\Daten\Projects\weberding\quiz` per robocopy.
Gibt Erfolgsmeldung oder Fehlercode aus. Bricht mit Fehler ab, wenn `out/` fehlt.

**Schritt 3 – GitHub:**

Geänderte Quelldateien stagen, committen und pushen. `out/` und `.claude/`
gehören **nicht** ins Repository.

```powershell
git add README.md SKILL.md agents/openai.yaml index.html .gitignore
git add publish-to-weberding.ps1 scripts/quiz_tool.py
git add Anpassungen.md Anpassungen.html
git add td_*.htm tq_*.htm
```

Commit-Message aus dem Konversationsverlauf ableiten – kurze, prägnante
Beschreibung der Änderungen in dieser Session (analog zu den bisherigen
Commit-Messages: „Add Duo and Quattro quiz modes", „Fix German umlauts …").

```
git commit -m "<beschreibende Commit-Message>"
git push origin master
```

Nach erfolgreichem Push die URL als Bestätigung ausgeben:
`https://github.com/chrisgitti/quiz`

## update

Bei `/quiz update` die geänderten Skill-Dateien aus dem Projekt in das globale Plugin-Verzeichnis kopieren, damit Claude Code beim nächsten Start die aktuellen Versionen lädt:

```powershell
$src = "C:\Daten\Projects\quiz"
$dst = "C:\Users\Christian\.claude\plugins\marketplaces\claude-plugins-official\plugins"

Copy-Item "$src\SKILL.md" "$dst\quiz\skills\quiz\SKILL.md" -Force
Copy-Item "$src\.claude\skills\quiz-anpassungen\SKILL.md" "$dst\quiz-anpassungen\skills\quiz-anpassungen\SKILL.md" -Force

Write-Host "OK: Skills aktualisiert. Claude Code neu starten, um die Änderungen zu laden."
```

Danach Claude Code neu starten, damit die aktualisierten Skills erkannt werden.

## ? Ausgabe

```text
/quiz duo [thema] create                  erstellt td_[thema].htm mit 100 Richtig/Falsch-Fragen
/quiz quattro [thema] create               erstellt tq_[thema].htm mit 100 Multiple-Choice-Fragen
/quiz [duo|quattro] [thema] check          prüft Struktur, Felder und Datentypen
/quiz [duo|quattro] [thema] check count:nnn  prüft mit Mindestanzahl nnn Fragen
/quiz [duo|quattro] all check              prüft alle Kataloge eines Modus strukturell
/quiz all check                           prüft alle Duo- und Quattro-Kataloge strukturell
/quiz [duo|quattro] [thema] check-lang     prüft Rechtschreibung, Grammatik, Interpunktion
/quiz all check-lang                      prüft alle Kataloge sprachlich
/quiz publish                             synchronisiert nach weberding\quiz und pusht auf GitHub
/quiz update                              kopiert SKILL.md-Dateien ins Plugin-Verzeichnis
/quiz ?                                   zeigt diese Hilfe
```
