# Quiz

Eigenstaendige statische Quiz-App mit zwei Modi:

- **Duo**: Richtig/Falsch-Fragen aus `td_[thema].htm`
- **Quattro**: Multiple-Choice-Fragen mit vier Antworten aus `tq_[thema].htm`

## Lokal starten

```powershell
cd C:\Daten\Projects\quiz
python -m http.server 4174
```

Danach im Browser oeffnen:

```text
http://localhost:4174/
```

## Duo-Themen

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

## Quattro-Themen

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

Erlaubte Schwierigkeitsgrade sind `leicht`, `mittel` und `schwer`.

## Pflege

```powershell
python -B scripts\quiz_tool.py all check
python -B scripts\quiz_tool.py duo all check
python -B scripts\quiz_tool.py quattro all check
python -B scripts\quiz_tool.py duo bayern check count:100
```

Neue Themen werden ueber den lokalen `/quiz`-Skill erstellt oder geprueft.

## Website veroeffentlichen

```powershell
.\publish-to-weberding.ps1
```

Das Script synchronisiert die aktuelle Quiz-Version nach `C:\Daten\Projects\weberding\quiz`.
