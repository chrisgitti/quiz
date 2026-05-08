#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

GRADES = {"leicht", "mittel", "schwer"}
ROOT = Path(__file__).resolve().parents[1]


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
        return "quatro"
    if name.startswith("td_"):
        return "duo"
    return "duo"


def topic_path(topic, mode="duo"):
    slug = slugify(topic)
    if not slug:
        raise SystemExit("ERROR: Thema ist leer oder enthaelt keine gueltigen Zeichen.")
    prefix = "tq" if mode == "quatro" else "td"
    return ROOT / f"{prefix}_{slug}.htm"


def all_topic_files(mode=None):
    patterns = []
    if mode in (None, "duo"):
        patterns.append("td_*.htm")
    if mode in (None, "quatro"):
        patterns.append("tq_*.htm")
    files = []
    for pattern in patterns:
        files.extend(ROOT.glob(pattern))
    return sorted(files, key=lambda p: p.name.lower())


def validate_duo(questions, label, min_count=None, require_100=False):
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
        aussage, antwort, grad = item.get("aussage"), item.get("antwort"), item.get("grad")
        if not isinstance(aussage, str) or not aussage.strip():
            errors.append(f"{prefix}: aussage muss ein nichtleerer Text sein")
        else:
            key = normalize(aussage)
            if key in seen:
                errors.append(f"{prefix}: doppelte Aussage wie Frage {seen[key]}")
            seen[key] = i
            if aussage.strip().endswith("?"):
                warnings.append(f"{prefix}: Duo-Aussage endet als Frage")
        if not isinstance(antwort, bool):
            errors.append(f"{prefix}: antwort muss true oder false sein")
        elif antwort:
            true_count += 1
        if grad not in GRADES:
            errors.append(f"{prefix}: grad muss leicht, mittel oder schwer sein")
    if questions:
        ratio = true_count / len(questions)
        if ratio < 0.4 or ratio > 0.6:
            warnings.append(f"{label}: Antwortbalance auffaellig ({true_count} true, {len(questions)-true_count} false)")
    return errors, warnings


def validate_quatro(questions, label, min_count=None, require_100=False):
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
        frage, antworten, richtig, grad = item.get("frage"), item.get("antworten"), item.get("richtig"), item.get("grad")
        if not isinstance(frage, str) or not frage.strip():
            errors.append(f"{prefix}: frage muss ein nichtleerer Text sein")
        else:
            key = normalize(frage)
            if key in seen:
                errors.append(f"{prefix}: doppelte Frage wie Frage {seen[key]}")
            seen[key] = i
        if not isinstance(antworten, list) or len(antworten) != 4 or not all(isinstance(a, str) and a.strip() for a in antworten):
            errors.append(f"{prefix}: antworten muss ein Array mit vier nichtleeren Texten sein")
        elif len({normalize(a) for a in antworten}) != 4:
            errors.append(f"{prefix}: Antwortoptionen muessen eindeutig sein")
        if not isinstance(richtig, int) or richtig < 0 or richtig > 3:
            errors.append(f"{prefix}: richtig muss ein Index von 0 bis 3 sein")
        if grad not in GRADES:
            errors.append(f"{prefix}: grad muss leicht, mittel oder schwer sein")
    return errors, warnings


def validate(questions, path, min_count=None, require_100=False):
    if detect_mode(path) == "quatro":
        return validate_quatro(questions, path.name, min_count, require_100)
    return validate_duo(questions, path.name, min_count, require_100)


def parse_count(argv):
    count = None
    rest = []
    for arg in argv:
        m = re.fullmatch(r"count:(\d+)", arg, re.I)
        if m:
            count = int(m.group(1))
        else:
            rest.append(arg)
    return count, rest


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv == ["?"]:
        print("""Quiz-Tool
python scripts/quiz_tool.py all check
python scripts/quiz_tool.py duo all check
python scripts/quiz_tool.py quatro all check
python scripts/quiz_tool.py duo bayern check count:100
python scripts/quiz_tool.py quatro poolbillardregeln check
""")
        return 0
    token_count, argv = parse_count(argv)
    mode = None
    if argv and argv[0] in {"duo", "quatro"}:
        mode = argv.pop(0)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("topic")
    parser.add_argument("action", choices=["check", "create"])
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--count", type=int, default=token_count)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.action == "check":
        paths = all_topic_files(mode) if args.topic == "all" else [topic_path(args.topic, mode or "duo")]
        failed = False
        for path in paths:
            if not path.exists():
                print(f"ERROR: {path.name} existiert nicht")
                failed = True
                continue
            try:
                questions = extract_questions(path)
                errors, warnings = validate(questions, path, args.count)
            except Exception as exc:
                errors, warnings = [f"{path.name}: {exc}"], []
            for error in errors:
                print(f"ERROR: {error}")
            for warning in warnings:
                print(f"WARN: {warning}")
            print(f"OK: {path.name}" + (" mit Warnungen" if warnings and not errors else "")) if not errors else None
            failed = failed or bool(errors)
        return 1 if failed else 0
    if not mode:
        print("ERROR: create benoetigt Modus duo oder quatro")
        return 2
    path = topic_path(args.topic, mode)
    if path.exists() and not args.force:
        print(f"ERROR: {path.name} existiert bereits. Mit --force ueberschreiben.")
        return 2
    if not args.questions:
        print("ERROR: create benoetigt --questions <jsondatei>")
        return 2
    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    errors, warnings = validate(questions, path, require_100=True)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        return 1
    path.write_text(render(questions), encoding="utf-8")
    print(f"OK: {path.name} erstellt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
