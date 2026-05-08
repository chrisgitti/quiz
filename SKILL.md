---
name: quiz
description: Work with the standalone quiz web app in C:\Daten\Projects\quiz. Use when the user invokes /quiz, creates or checks Duo true/false catalogs td_[thema].htm, creates or checks Quatro multiple-choice catalogs tq_[thema].htm, validates count:nnn minimums, or asks for quiz skill help.
---

# Quiz

## Aufruf

- `/quiz ?`: Zweck, Modi und Parameter erklaeren.
- `/quiz duo [thema] create`: Neue Duo-Datei `td_[thema].htm` mit 100 Richtig/Falsch-Fragen erstellen.
- `/quiz quatro [thema] create`: Neue Quatro-Datei `tq_[thema].htm` mit 100 Multiple-Choice-Fragen erstellen.
- `/quiz [duo|quatro] [thema] check`: Einzelnen Fragenkatalog pruefen.
- `/quiz [duo|quatro] [thema] check count:nnn`: Pruefen, ob mindestens `nnn` Fragen vorhanden sind.
- `/quiz all check`: Alle Duo- und Quatro-Kataloge pruefen.

`[thema]` ist der Dateisuffix ohne Prefix, z. B. `bayern`, `poolbillardregeln` oder `auswahlverfahren`.

## Web-App

Die App liegt im eigenstaendigen Projektordner `C:\Daten\Projects\quiz`.

- `index.html`: Quiz-Oberflaeche mit Moduswahl Duo/Quatro.
- `td_[thema].htm`: Duo-Themenkataloge mit zwei Antworten `Richtig` und `Falsch`.
- `tq_[thema].htm`: Quatro-Themenkataloge mit vier Antwortmoeglichkeiten A-D.
- `scripts/quiz_tool.py`: Validierung und Katalogpflege.
- `publish-to-weberding.ps1`: Synchronisiert die App nach `C:\Daten\Projects\weberding\quiz`.

## Duo-Datenstruktur

```html
<div id="question_data">
[
  {
    "aussage": "Eine klare, faktisch pruefbare Aussage.",
    "antwort": true,
    "grad": "leicht"
  }
]
</div>
```

Pflichtfelder: `aussage` als Behauptung, `antwort` als Boolean, `grad` als `leicht`, `mittel` oder `schwer`.

## Quatro-Datenstruktur

```html
<div id="question_data">
[
  {
    "frage": "Welche Antwort ist richtig?",
    "antworten": ["A", "B", "C", "D"],
    "richtig": 0,
    "grad": "leicht"
  }
]
</div>
```

Pflichtfelder: `frage`, vier eindeutige `antworten`, `richtig` als Index 0-3, `grad` als `leicht`, `mittel` oder `schwer`.

## create

Bei `create`:

1. Thema normalisieren: Kleinbuchstaben, Umlaute transliterieren, Sonderzeichen zu `-`.
2. Genau 100 fachlich belastbare deutsche Fragen erzeugen.
3. Schwierigkeitsgrade moeglichst ausgeglichen verteilen.
4. Keine doppelten oder nahezu identischen Fragen verwenden.
5. Bei Duo Antworten zwischen `true` und `false` ausbalancieren.
6. Bei Quatro vier plausible, eindeutige Antwortoptionen erzeugen; nur eine Antwort darf korrekt sein.
7. Aktuelle oder rechtlich/fachlich veraenderliche Fakten vorab aus verlaesslichen Quellen pruefen.
8. Mit `scripts/quiz_tool.py duo|quatro [thema] create --questions <jsondatei>` schreiben und danach checken.

## check

- Alle Kataloge: `python -B scripts\quiz_tool.py all check`
- Nur Duo: `python -B scripts\quiz_tool.py duo all check`
- Nur Quatro: `python -B scripts\quiz_tool.py quatro all check`
- Einzelthema: `python -B scripts\quiz_tool.py duo bayern check count:100`
- Quatro-Einzelthema: `python -B scripts\quiz_tool.py quatro poolbillardregeln check`

Fehler in JSON, Pflichtfeldern, Datentypen, Antwortanzahl, richtigen Indizes oder Duplikaten beheben.

## ? Ausgabe

```text
/quiz duo [thema] create          erstellt td_[thema].htm mit 100 Richtig/Falsch-Fragen.
/quiz quatro [thema] create       erstellt tq_[thema].htm mit 100 Multiple-Choice-Fragen.
/quiz [duo|quatro] [thema] check  prueft einen Katalog.
/quiz [duo|quatro] all check      prueft alle Kataloge eines Modus.
/quiz all check                   prueft alle Duo- und Quatro-Kataloge.
/quiz ?                           zeigt diese Hilfe.
```
