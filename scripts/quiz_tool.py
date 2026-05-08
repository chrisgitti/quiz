#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

GRADES = {"leicht", "mittel", "schwer"}
GRADE_ORDER = ("leicht", "mittel", "schwer")
ROOT = Path(__file__).resolve().parents[1]


def slugify(value):
    value = value.strip().lower()
    value = value.replace("\u00e4", "ae").replace("\u00f6", "oe")
    value = value.replace("\u00fc", "ue").replace("\u00df", "ss")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def topic_title(slug):
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug) if part)


def topic_paths(topic):
    slug = slugify(topic)
    if not slug:
        raise SystemExit("ERROR: Thema ist leer oder enthaelt keine gueltigen Zeichen.")
    return slug, ROOT / f"t_{slug}.htm"


def find_topic_file(topic):
    slug, htm_path = topic_paths(topic)
    return slug, htm_path


def extract_questions(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<div[^>]+id=["\']question_data["\'][^>]*>([\s\S]*?)</div>',
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("question_data Container nicht gefunden")
    return json.loads(match.group(1).strip())


def normalize_statement(value):
    value = re.sub(r"\s+", " ", value.strip().lower())
    return re.sub(r"[^\w\u00e4\u00f6\u00fc\u00df ]+", "", value, flags=re.IGNORECASE)


def grade_counts_for(questions):
    counts = {grade: 0 for grade in GRADE_ORDER}
    for item in questions:
        if isinstance(item, dict) and item.get("grad") in counts:
            counts[item["grad"]] += 1
    return counts


def recommended_grades(existing_questions, target_count):
    counts = grade_counts_for(existing_questions)
    result = []
    while len(existing_questions) + len(result) < target_count:
        next_grade = min(GRADE_ORDER, key=lambda grade: (counts[grade], GRADE_ORDER.index(grade)))
        result.append(next_grade)
        counts[next_grade] += 1
    return result


def validate_questions(questions, path_label, require_100=False, min_count=None):
    errors = []
    warnings = []

    if not isinstance(questions, list):
        return [f"{path_label}: question_data ist kein JSON-Array"], warnings

    if require_100 and len(questions) != 100:
        errors.append(f"{path_label}: erwartet 100 Fragen, gefunden {len(questions)}")
    elif min_count is not None and len(questions) < min_count:
        missing = min_count - len(questions)
        errors.append(f"{path_label}: mindestens {min_count} Fragen erwartet, gefunden {len(questions)}, fehlen {missing}")
    elif len(questions) != 100:
        warnings.append(f"{path_label}: {len(questions)} Fragen gefunden, Zielwert fuer neue Themen ist 100")

    seen = {}
    true_count = 0
    grade_counts = {grade: 0 for grade in GRADE_ORDER}

    for index, item in enumerate(questions, start=1):
        prefix = f"{path_label} Frage {index}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: Eintrag ist kein Objekt")
            continue

        statement = item.get("aussage")
        answer = item.get("antwort")
        grade = item.get("grad")
        extra_keys = sorted(set(item) - {"aussage", "antwort", "grad"})
        missing_keys = sorted({"aussage", "antwort", "grad"} - set(item))

        if missing_keys:
            errors.append(f"{prefix}: Pflichtfeld(er) fehlen: {', '.join(missing_keys)}")
        if extra_keys:
            warnings.append(f"{prefix}: unbekannte Feld(er): {', '.join(extra_keys)}")
        if not isinstance(statement, str) or not statement.strip():
            errors.append(f"{prefix}: aussage muss ein nichtleerer Text sein")
        else:
            key = normalize_statement(statement)
            if key in seen:
                errors.append(f"{prefix}: doppelte/identische Aussage wie Frage {seen[key]}")
            else:
                seen[key] = index
            if statement.strip().endswith("?"):
                warnings.append(f"{prefix}: Aussage endet als Frage")
        if not isinstance(answer, bool):
            errors.append(f"{prefix}: antwort muss true oder false sein")
        elif answer:
            true_count += 1
        if grade not in GRADES:
            errors.append(f"{prefix}: grad muss leicht, mittel oder schwer sein")
        else:
            grade_counts[grade] += 1

    if questions:
        ratio = true_count / len(questions)
        if ratio < 0.4 or ratio > 0.6:
            warnings.append(f"{path_label}: Antwortbalance auffaellig ({true_count} true, {len(questions) - true_count} false)")
        for grade, count in grade_counts.items():
            if count == 0:
                warnings.append(f"{path_label}: keine Fragen mit grad={grade}")

    return errors, warnings


def render_topic_html(questions):
    payload = json.dumps(questions, ensure_ascii=False, indent=4)
    return f'<div id="question_data">\n{payload}\n</div>\n'


def update_fallback_index(slug, filename):
    index_path = ROOT / "index.html"
    if not index_path.exists():
        return

    text = index_path.read_text(encoding="utf-8")
    if filename in text:
        return

    title = topic_title(slug)
    entry = f"        {{ datei: '{filename}', titel: '{title}' }},\n"
    pattern = r"(    const fallback_themen = \[\n)([\s\S]*?)(    \];)"
    match = re.search(pattern, text)
    if not match:
        print("WARN: fallback_themen in index.html nicht gefunden; bitte manuell ergaenzen.", file=sys.stderr)
        return

    body = match.group(2)
    body = body.rstrip()
    if body.endswith("}"):
        body += ","
    replacement = match.group(1) + body + "\n" + entry.rstrip(",\n") + "\n" + match.group(3)
    index_path.write_text(text[: match.start()] + replacement + text[match.end() :], encoding="utf-8")


def all_topic_files():
    files = sorted(ROOT.glob("t_*.htm"))
    return sorted(files, key=lambda path: path.name.lower())


def parse_count_tokens(tokens):
    count = None
    rest = []
    for token in tokens:
        match = re.fullmatch(r"count:(\d+)", token, flags=re.IGNORECASE)
        if match:
            count = int(match.group(1))
        else:
            rest.append(token)
    return count, rest


def print_help():
    print(
        """Quiz-Skill

/quiz [thema] create            erstellt quiz/t_[thema].htm mit 100 Richtig/Falsch-Fragen.
/quiz [thema] check             prueft quiz/t_[thema].htm.
/quiz [thema] check count:nnn   prueft mindestens nnn Fragen und ergaenzt fehlende Fragen.
/quiz all check                 prueft alle Themenkataloge.
/quiz ?                         zeigt diese Hilfe.

Technischer Helfer:
python scripts/quiz_tool.py [thema] create --questions fragen.json
python scripts/quiz_tool.py [thema] check --count nnn
python scripts/quiz_tool.py [thema] append --questions neue-fragen.json --count nnn
python scripts/quiz_tool.py all check
"""
    )


def report_validation(path, questions, errors, warnings, count=None):
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if not errors and not warnings:
        print(f"OK: {path.name}")
    elif not errors:
        print(f"OK: {path.name} mit Warnungen")
    if count is not None and len(questions) < count:
        grades = recommended_grades(questions, count)
        counts = ", ".join(f"{grade}:{grades.count(grade)}" for grade in GRADE_ORDER)
        print(f"NEEDED: {path.name} benoetigt {len(grades)} neue Fragen ({counts})")


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv == ["?"]:
        print_help()
        return 0

    count_from_token, argv = parse_count_tokens(argv)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("topic")
    parser.add_argument("action", choices=["create", "check", "append"])
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--count", type=int, default=count_from_token)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.count is not None and args.count < 1:
        print("ERROR: count muss groesser als 0 sein")
        return 2

    if args.action == "check":
        paths = all_topic_files() if args.topic.lower() == "all" else [find_topic_file(args.topic)[1]]
        had_errors = False
        for path in paths:
            if not path.exists():
                print(f"ERROR: {path.name} existiert nicht")
                had_errors = True
                continue
            try:
                questions = extract_questions(path)
                errors, warnings = validate_questions(questions, path.name, min_count=args.count)
            except Exception as exc:
                questions = []
                errors, warnings = [f"{path.name}: {exc}"], []
            report_validation(path, questions, errors, warnings, args.count)
            had_errors = had_errors or bool(errors)
        return 1 if had_errors else 0

    slug, htm_path = topic_paths(args.topic)

    if args.action == "append":
        if not htm_path.exists():
            print(f"ERROR: {htm_path.name} existiert nicht")
            return 2
        if not args.questions:
            print("ERROR: append benoetigt --questions <jsondatei> mit neuen Fragen.")
            return 2

        existing_questions = extract_questions(htm_path)
        new_questions = json.loads(args.questions.read_text(encoding="utf-8"))
        if not isinstance(new_questions, list):
            print("ERROR: --questions muss ein JSON-Array enthalten.")
            return 2

        target_count = args.count or (len(existing_questions) + len(new_questions))
        missing = max(0, target_count - len(existing_questions))
        selected_questions = new_questions[:missing] if missing else new_questions
        if missing and len(selected_questions) < missing:
            print(f"ERROR: Es fehlen {missing} Fragen, aber --questions enthaelt nur {len(new_questions)}.")
            return 1

        combined_questions = existing_questions + selected_questions
        errors, warnings = validate_questions(combined_questions, htm_path.name, min_count=target_count)
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARN: {warning}")
        if errors:
            return 1

        htm_path.write_text(render_topic_html(combined_questions), encoding="utf-8")
        print(f"OK: {htm_path.name} enthaelt jetzt {len(combined_questions)} Fragen")
        return 0

    if not args.questions:
        print("ERROR: create benoetigt --questions <jsondatei> mit genau 100 Fragen.")
        return 2
    if htm_path.exists() and not args.force:
        print(f"ERROR: {htm_path.name} existiert bereits. Mit --force ueberschreiben.")
        return 2

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    errors, warnings = validate_questions(questions, htm_path.name, require_100=True)
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        return 1

    htm_path.write_text(render_topic_html(questions), encoding="utf-8")
    update_fallback_index(slug, htm_path.name)
    print(f"OK: {htm_path.name} erstellt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
