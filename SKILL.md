---
name: quiz
description: Work with the local true/false quiz web app in the repository subfolder quiz. Use when the user invokes /quiz or asks to create a new quiz topic file, generate German richtig/falsch questions for a topic, validate or extend existing t_[thema].htm question catalogs including count:nnn minimum question counts, or explain the quiz skill parameters including "?".
---

# Quiz

## Aufruf

- `/quiz ?`: Zweck und Parameter erklaeren.
- `/quiz [thema] create`: Neue Themendatei mit 100 Fragen erstellen.
- `/quiz [thema] check`: Bestehende Themendatei oder den Katalog pruefen.
- `/quiz [thema] check count:nnn`: Pruefen, ob mindestens `nnn` Fragen vorhanden sind; fehlende Fragen passend ergaenzen.

`[thema]` ist der Dateisuffix ohne Prefix, z. B. `bayern`, `deutsch` oder `auswahlverfahren`.
Neue Dateien als `t_[thema].htm` anlegen.

## Web-App

Die App liegt in diesem Skill-Ordner:

- `index.html`: Quiz-Oberflaeche fuer Richtig/Falsch-Fragen.
- `t_[thema].htm`: Themenkataloge.
- `correct.mp3`, `wrong.mp3`, `media/`: Audioausgabe.

`index.html` ermittelt Themen per Verzeichnislisting aus Dateien `t_*.htm`. Falls der Webserver keine Verzeichnisliste liefert, verwendet die App `fallback_themen` in `index.html`. Bei neuen Themen diese Liste ebenfalls aktualisieren.

## Datenstruktur

Eine Themendatei enthaelt genau ein JSON-Array im Container:

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

Pflichtfelder pro Frage:

- `aussage`: Nichtleerer deutscher Satz. Als Behauptung formulieren, nicht als Frage.
- `antwort`: Boolean `true` oder `false`.
- `grad`: Einer der Werte `leicht`, `mittel`, `schwer`.

## create

Bei `/quiz [thema] create`:

1. Thema normalisieren: Kleinbuchstaben, Umlaute transliterieren, Leerzeichen/Sonderzeichen zu `-`, nur `a-z0-9-`.
2. Genau 100 fachlich belastbare, altersneutral formulierte Richtig/Falsch-Aussagen auf Deutsch erstellen.
3. Antworten ausgewogen mischen; als Ziel 45 bis 55 wahre Aussagen verwenden.
4. Schwierigkeitsgrade breit verteilen, ungefaehr ein Drittel je Grad.
5. Keine doppelten oder nahezu identischen Aussagen verwenden.
6. Die Fragen als JSON-Array speichern und mit `scripts/quiz_tool.py [thema] create --questions <jsondatei>` in eine Themendatei schreiben.
7. Danach `scripts/quiz_tool.py [thema] check` ausfuehren.

Wenn fuer aktuelle, potenziell veraenderliche Fakten recherchiert werden muss, vor dem Generieren aktuelle Quellen pruefen.

## check

Bei `/quiz [thema] check`:

- `scripts/quiz_tool.py [thema] check` ausfuehren.
- Fuer den gesamten Katalog `scripts/quiz_tool.py all check` ausfuehren.
- Fehler beheben, wenn JSON ungueltig ist, Pflichtfelder fehlen, `antwort` kein Boolean ist, `grad` ungueltig ist, Texte leer sind oder Duplikate vorkommen.
- Warnungen zu Laenge, Antwortbalance oder Gradverteilung fachlich bewerten und bei Bedarf korrigieren.

Bei `/quiz [thema] check count:nnn`:

1. `scripts/quiz_tool.py [thema] check count:nnn` ausfuehren.
2. Wenn die Ausgabe `NEEDED` meldet, genau die fehlende Anzahl neuer Fragen zum Thema erzeugen.
3. Die in `NEEDED` genannte Gradverteilung einhalten, z. B. `leicht:4, mittel:3, schwer:4`.
4. Neue Fragen fachlich passend, nicht redundant und als Behauptungen formulieren.
5. Die neuen Fragen als JSON-Array in eine temporaere Datei schreiben.
6. Mit `scripts/quiz_tool.py [thema] append --questions <jsondatei> --count nnn` anhaengen.
7. Danach erneut `scripts/quiz_tool.py [thema] check count:nnn` ausfuehren.

Wenn der Bestand bereits mindestens `nnn` Fragen enthaelt, keine Fragen ergaenzen.

## ? Ausgabe

Bei `/quiz ?` kurz erklaeren:

```text
/quiz [thema] create  erstellt quiz/t_[thema].htm mit 100 Richtig/Falsch-Fragen.
/quiz [thema] check   prueft quiz/t_[thema].htm.
/quiz [thema] check count:nnn prueft mindestens nnn Fragen und ergaenzt fehlende.
/quiz all check       prueft alle Themenkataloge.
/quiz ?               zeigt diese Hilfe.
```
