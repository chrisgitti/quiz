#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

GRADES = {"leicht", "mittel", "schwer"}
ROOT = Path(__file__).resolve().parents[1]

_DOUBLE_SPACE = re.compile(r"  +")
_PLACEHOLDER  = re.compile(r"\[\.\.\.?\]|XXX|TODO", re.I)
_HTML_TAG     = re.compile(r"<[^>]+>")


def slugify(value):
    value = value.strip().lower()
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def extract_questions(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r'<div[^>]+id=["\']question_data["\'][^>]*>([\s\S]*?)</div>', text, re.I)
    if not match:
        raise ValueError("question_data Container nicht gefunden")
    return json.loads(match.group(1).strip())


def render(questions):
    return '<div id="question_data">\n' + json.dumps(questions, ensure_ascii=False, indent=4) + '\n</div>\n'


def normalize(text):
    text = re.sub(r"\s+", " ", str(text).strip().lower())
    return re.sub(r"[^\wäöüß ]+", "", text, flags=re.I)


def detect_mode(path):
    name = path.name.lower()
    if name.startswith("tq_"):
        return "quattro"
    if name.startswith("td_"):
        return "duo"
    return "duo"


def topic_path(topic, mode="duo"):
    slug = slugify(topic)
    if not slug:
        raise SystemExit("ERROR: Thema ist leer oder enthaelt keine gueltigen Zeichen.")
    prefix = "tq" if mode == "quattro" else "td"
    return ROOT / f"{prefix}_{slug}.htm"


def all_topic_files(mode=None):
    patterns = []
    if mode in (None, "duo"):
        patterns.append("td_*.htm")
    if mode in (None, "quattro"):
        patterns.append("tq_*.htm")
    files = []
    for pattern in patterns:
        files.extend(ROOT.glob(pattern))
    return sorted(files, key=lambda p: p.name.lower())


# ---------------------------------------------------------------------------
# Heuristic language lint
# ---------------------------------------------------------------------------

def lint_text(text, prefix, label, role=None):
    """Heuristic language checks for a single text field.

    role:
      'aussage' – Duo statement (should end with . or !)
      'frage'   – Quattro question (should end with ?)
      'antwort' – Quattro answer option (no strict punctuation rule)
      None      – generic text
    """
    warnings = []
    t = text.strip()
    if _HTML_TAG.search(t):
        warnings.append(f"{prefix}: {label} enthaelt HTML-Tags")
    if _PLACEHOLDER.search(t):
        warnings.append(f"{prefix}: {label} enthaelt Platzhaltertext")
    if _DOUBLE_SPACE.search(t):
        warnings.append(f"{prefix}: {label} enthaelt doppelte Leerzeichen")
    if t and not t[0].isupper():
        warnings.append(f"{prefix}: {label} beginnt nicht mit Grossbuchstaben")
    if len(t) < 10:
        warnings.append(f"{prefix}: {label} ist sehr kurz ({len(t)} Zeichen)")
    if len(t) > 250:
        warnings.append(f"{prefix}: {label} ist sehr lang ({len(t)} Zeichen)")
    if role == "frage" and not t.endswith("?"):
        warnings.append(f"{prefix}: {label} (Frage) sollte mit '?' enden")
    if role == "aussage" and not t.endswith("?") and not re.search(r"[.!]$", t):
        # '?' case is already caught by the structural check; here we flag missing . or !
        warnings.append(f"{prefix}: {label} sollte mit '.' oder '!' enden")
    return warnings


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_duo(questions, label, min_count=None, require_100=False, lint=False):
    errors, warnings, seen = [], [], {}
    if not isinstance(questions, list):
        return [f"{label}: question_data ist kein JSON-Array"], warnings
    if require_100 and len(questions) != 100:
        errors.append(f"{label}: erwartet 100 Fragen, gefunden {len(questions)}")
    elif min_count and len(questions) < min_count:
        errors.append(f"{label}: mindestens {min_count} Fragen erwartet, gefunden {len(questions)}")
    elif len(questions) != 100:
        warnings.append(f"{label}: {len(questions)} Fragen gefunden, Zielwert fuer neue Themen ist 100")
    true_count = 0
    for i, item in enumerate(questions, 1):
        prefix = f"{label} Frage {i}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: Eintrag ist kein Objekt")
            continue
        aussage = item.get("aussage")
        antwort = item.get("antwort")
        grad    = item.get("grad")
        if not isinstance(aussage, str) or not aussage.strip():
            errors.append(f"{prefix}: aussage muss ein nichtleerer Text sein")
        else:
            key = normalize(aussage)
            if key in seen:
                errors.append(f"{prefix}: doppelte Aussage wie Frage {seen[key]}")
            seen[key] = i
            if aussage.strip().endswith("?"):
                warnings.append(f"{prefix}: Duo-Aussage endet als Frage")
            if lint:
                warnings.extend(lint_text(aussage, prefix, "aussage", role="aussage"))
        if not isinstance(antwort, bool):
            errors.append(f"{prefix}: antwort muss true oder false sein")
        elif antwort:
            true_count += 1
        if grad not in GRADES:
            errors.append(f"{prefix}: grad muss leicht, mittel oder schwer sein")
    if questions:
        ratio = true_count / len(questions)
        if ratio < 0.4 or ratio > 0.6:
            warnings.append(
                f"{label}: Antwortbalance auffaellig "
                f"({true_count} true, {len(questions) - true_count} false)"
            )
    return errors, warnings


def validate_quattro(questions, label, min_count=None, require_100=False, lint=False):
    errors, warnings, seen = [], [], {}
    if not isinstance(questions, list):
        return [f"{label}: question_data ist kein JSON-Array"], warnings
    if require_100 and len(questions) != 100:
        errors.append(f"{label}: erwartet 100 Fragen, gefunden {len(questions)}")
    elif min_count and len(questions) < min_count:
        errors.append(f"{label}: mindestens {min_count} Fragen erwartet, gefunden {len(questions)}")
    for i, item in enumerate(questions, 1):
        prefix = f"{label} Frage {i}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: Eintrag ist kein Objekt")
            continue
        frage    = item.get("frage")
        antworten = item.get("antworten")
        richtig  = item.get("richtig")
        grad     = item.get("grad")
        if not isinstance(frage, str) or not frage.strip():
            errors.append(f"{prefix}: frage muss ein nichtleerer Text sein")
        else:
            key = normalize(frage)
            if key in seen:
                errors.append(f"{prefix}: doppelte Frage wie Frage {seen[key]}")
            seen[key] = i
            if lint:
                warnings.extend(lint_text(frage, prefix, "frage", role="frage"))
        if (
            not isinstance(antworten, list)
            or len(antworten) != 4
            or not all(isinstance(a, str) and a.strip() for a in antworten)
        ):
            errors.append(f"{prefix}: antworten muss ein Array mit vier nichtleeren Texten sein")
        else:
            if len({normalize(a) for a in antworten}) != 4:
                errors.append(f"{prefix}: Antwortoptionen muessen eindeutig sein")
            if lint:
                for j, ans in enumerate(antworten):
                    warnings.extend(lint_text(ans, prefix, f"antwort[{j}]", role="antwort"))
        if not isinstance(richtig, int) or richtig < 0 or richtig > 3:
            errors.append(f"{prefix}: richtig muss ein Index von 0 bis 3 sein")
        if grad not in GRADES:
            errors.append(f"{prefix}: grad muss leicht, mittel oder schwer sein")
    return errors, warnings


def validate(questions, path, min_count=None, require_100=False, lint=False):
    if detect_mode(path) == "quattro":
        return validate_quattro(questions, path.name, min_count, require_100, lint)
    return validate_duo(questions, path.name, min_count, require_100, lint)


# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------

#: Dateimuster, die in out/ kopiert werden (relativ zu ROOT)
_WEB_FILES = ["index.html", "Anpassungen.html"]
_WEB_GLOBS = ["td_*.htm", "tq_*.htm", "*.mp3"]
_WEB_DIRS  = ["media"]


def cmd_publish():
    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)

    copied = []

    for name in _WEB_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
            copied.append(name)
        else:
            print(f"WARN:  {name} nicht gefunden, wird übersprungen")

    for pattern in _WEB_GLOBS:
        for src in sorted(ROOT.glob(pattern)):
            shutil.copy2(src, out_dir / src.name)
            copied.append(src.name)

    for dirname in _WEB_DIRS:
        src = ROOT / dirname
        if src.is_dir():
            dst = out_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(f"{dirname}/")
        else:
            print(f"WARN:  {dirname}/ nicht gefunden, wird übersprungen")

    print(f"OK:    out/ befüllt – {len(copied)} Einträge")
    for item in copied:
        print(f"       {item}")
    return 0


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def parse_count(argv):
    count = None
    rest  = []
    for arg in argv:
        m = re.fullmatch(r"count:(\d+)", arg, re.I)
        if m:
            count = int(m.group(1))
        else:
            rest.append(arg)
    return count, rest


def run_check(paths, min_count, lint):
    failed = False
    for path in paths:
        if not path.exists():
            print(f"ERROR: {path.name} existiert nicht")
            failed = True
            continue
        try:
            questions = extract_questions(path)
            errors, warnings = validate(questions, path, min_count, lint=lint)
        except Exception as exc:
            errors, warnings = [f"{path.name}: {exc}"], []
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARN:  {warning}")
        if not errors:
            suffix = " mit Warnungen" if warnings else ""
            print(f"OK:    {path.name}{suffix}")
        failed = failed or bool(errors)
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

HELP = """\
Quiz-Tool – Verwendung:

  python -B scripts\\quiz_tool.py all check
  python -B scripts\\quiz_tool.py all check --lint
  python -B scripts\\quiz_tool.py duo all check
  python -B scripts\\quiz_tool.py quattro all check
  python -B scripts\\quiz_tool.py duo     <thema> check [count:N] [--lint]
  python -B scripts\\quiz_tool.py quattro  <thema> check [count:N] [--lint]
  python -B scripts\\quiz_tool.py duo     <thema> create --questions <datei.json>
  python -B scripts\\quiz_tool.py quattro  <thema> create --questions <datei.json> [--force]
  python -B scripts\\quiz_tool.py publish

Flags:
  count:N   Mindestanzahl an Fragen (z. B. count:100)
  --lint    Heuristischer Sprachlint: Grossschreibung, Satzzeichen,
            Laenge, Platzhalter, HTML-Tags
  --force   Vorhandene Datei beim create ueberschreiben

publish:
  Befuellt out/ mit allen webserver-relevanten Dateien:
  index.html, Anpassungen.html, td_*.htm, tq_*.htm, *.mp3, media/
"""


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv == ["?"]:
        print(HELP)
        return 0

    if argv and argv[0] == "publish":
        return cmd_publish()

    token_count, argv = parse_count(argv)

    mode = None
    if argv and argv[0] in {"duo", "quattro"}:
        mode = argv.pop(0)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("topic")
    parser.add_argument("action", choices=["check", "create"])
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--count", type=int, default=token_count)
    parser.add_argument("--force",  action="store_true")
    parser.add_argument("--lint",   action="store_true",
                        help="Heuristischer Sprachlint (Gross-/Kleinschreibung, Satzzeichen, Laenge)")
    args = parser.parse_args(argv)

    if args.action == "check":
        paths = (
            all_topic_files(mode)
            if args.topic == "all"
            else [topic_path(args.topic, mode or "duo")]
        )
        return run_check(paths, args.count, lint=args.lint)

    # --- create ---
    if not mode:
        print("ERROR: create benoetigt Modus duo oder quattro")
        return 2
    path = topic_path(args.topic, mode)
    if path.exists() and not args.force:
        print(f"ERROR: {path.name} existiert bereits. Mit --force ueberschreiben.")
        return 2
    if not args.questions:
        print("ERROR: create benoetigt --questions <jsondatei>")
        return 2
    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    errors, warnings = validate(questions, path, require_100=True, lint=True)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN:  {warning}")
    if errors:
        return 1
    path.write_text(render(questions), encoding="utf-8")
    print(f"OK:    {path.name} erstellt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
