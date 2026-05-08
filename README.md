# Quiz

Eigenstaendige statische Richtig/Falsch-Quiz-App fuer mehrere Themenkataloge.

## Lokal starten

```powershell
cd C:\Daten\Projects\quiz
python -m http.server 4174
```

Danach im Browser oeffnen:

```text
http://localhost:4174/
```

## Themen

Themen liegen als `t_[thema].htm` im Projektordner. Jede Themendatei enthaelt ein JSON-Array im Container `question_data`:

```html
<div id="question_data">
[
  {
    "aussage": "Eine pruefbare Aussage.",
    "antwort": true,
    "grad": "leicht"
  }
]
</div>
```

Erlaubte Schwierigkeitsgrade sind `leicht`, `mittel` und `schwer`.

## Pflege

```powershell
python -B scripts\quiz_tool.py all check
python -B scripts\quiz_tool.py bayern check count:100
```

Neue Themen werden ueber den lokalen `/quiz`-Skill erstellt oder geprueft.

## Website veroeffentlichen

Die Website `weberding.de` bleibt ein Deployment-Ziel. Nach Aenderungen im eigenstaendigen Projekt kann die aktuelle Quiz-Version nach `C:\Daten\Projects\weberding\quiz` kopiert werden:

```powershell
.\publish-to-weberding.ps1
```

Das Script synchronisiert die App-Dateien und laesst Git-Metadaten sowie lokale Cache-Dateien aus.
