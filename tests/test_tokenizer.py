#!/usr/bin/env python3
"""
test_tokenizer.py

Validate query-topics TSV files before running an Elasticsearch prefilter.

This script has two layers:

1. Static TSV/Lucene-shape validation, which does not require Elasticsearch.
   It checks the file contract used by query_topics_*.tsv:

       query_topic<TAB>query
       medication_tier1<TAB>...
       medication_tier2<TAB>...
       medication_tier3<TAB>...

   or the analogous surgery_tier1..3 topics.

2. Optional live Elasticsearch checks with --live. These use the field analyzer
   and query_string parser to catch analyzer-sensitive terms such as:

       IL-12/23, 6-TGN, 6-MMP, 5-ASA, h/o, s/p, S1P, MTX, TDM, ATI

   The live checks report:
     * analyzer tokens for control terms;
     * analyzer tokens and match_phrase hit counts for suspect terms;
     * whole-tier query_string hit counts.

Typical static validation:

    python test_tokenizer.py --tsv query_topics_medication.tsv

Typical live validation:

    python test_tokenizer.py \
        --tsv query_topics_medication.tsv \
        --live \
        --hosts http://localhost:9200 \
        --index ibd_notes \
        --field note

Exit codes:
    0 = validation completed without errors
    1 = live Elasticsearch query/parser/check error
    2 = static TSV validation failed
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

EXPECTED_HEADER = ["query_topic", "query"]
TOPIC_RE = re.compile(r"^[a-z][a-z0-9_]*_tier[123][a-z]?$")
SMART_QUOTES = {"\u201c", "\u201d", "\u2018", "\u2019"}
BOOLEAN_WORDS = {"AND", "OR", "NOT", "TO"}
DEFAULT_FIELD_NAMES = {"note"}

# Quoted Lucene phrases, e.g. "anti-TNF".
QUOTED = re.compile(r'"((?:\\.|[^"\\])*)"')

# Bare Lucene-ish atoms. This intentionally includes punctuation often present
# in clinical shorthand and medication names; we filter operators/field names later.
BARE_ATOM = re.compile(r'(?<!["\\\w:])([A-Za-z0-9][A-Za-z0-9_./&+\-]*)(?!["\\\w\-])')

# Terms whose matching is especially analyzer-sensitive.
SUSPECT_PUNCT = re.compile(r"[/&'.-]")


@dataclass(frozen=True)
class StaticValidationResult:
    tiers: dict[str, str]
    errors: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class LiveValidationResult:
    errors: list[str]
    warnings: list[str]


def parse_expected_topics(raw: str | None, tsv_path: Path) -> set[str] | None:
    """Parse --expected-topics, or infer common project conventions from filename."""
    if raw is None or raw.strip().lower() == "auto":
        name = tsv_path.name.lower()
        if "medication" in name or "treatment" in name:
            return {"medication_tier1", "medication_tier2", "medication_tier3"}
        if "surgery" in name:
            return {"surgery_tier1", "surgery_tier2", "surgery_tier3"}
        return None

    if raw.strip().lower() in {"", "none", "off", "false"}:
        return None

    return {item.strip() for item in raw.split(",") if item.strip()}


def balanced_lucene_syntax(text: str) -> tuple[bool, str | None]:
    """Check balanced double quotes and parentheses, ignoring parentheses inside quotes."""
    depth = 0
    in_quote = False
    escaped = False

    for i, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False, f"unmatched ')' at character {i + 1}"

    if in_quote:
        return False, "unclosed double quote"
    if depth != 0:
        return False, f"unbalanced parentheses, final depth={depth}"
    return True, None


def query_scope_mode(query: str, field: str) -> str:
    """Return 'fielded', 'mixed', or 'unfielded' for a query row."""
    # A pragmatic convention check, not a full Lucene parser.
    fielded = bool(re.search(rf"\b{re.escape(field)}\s*:\s*\(", query))
    has_unfielded = bool(re.search(r"(^|\s|\()\(?\s*\"?\w", query)) and not query.strip().startswith(f"{field}:")
    if fielded and has_unfielded:
        return "mixed"
    if fielded:
        return "fielded"
    return "unfielded"


def validate_tsv_shape(
    tsv_path: Path,
    expected_topics: set[str] | None = None,
    field: str = "note",
) -> StaticValidationResult:
    """Validate TSV contract and basic Lucene syntax without touching ES."""
    errors: list[str] = []
    warnings: list[str] = []
    tiers: dict[str, str] = {}

    if not tsv_path.exists():
        return StaticValidationResult({}, [f"{tsv_path}: file does not exist"], [])

    try:
        with tsv_path.open("r", encoding="utf-8", newline="") as f:
            # Important: QUOTE_NONE preserves Lucene double quotes verbatim.
            reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            rows = list(reader)
    except UnicodeDecodeError as exc:
        return StaticValidationResult({}, [f"{tsv_path}: not valid UTF-8: {exc}"], [])
    except csv.Error as exc:
        return StaticValidationResult({}, [f"{tsv_path}: TSV parse error: {exc}"], [])

    if not rows:
        return StaticValidationResult({}, [f"{tsv_path}: empty file"], [])

    if rows[0] != EXPECTED_HEADER:
        errors.append(f"{tsv_path}: header must be exactly {EXPECTED_HEADER}, got {rows[0]!r}")

    seen: set[str] = set()
    scope_modes: dict[str, str] = {}

    for line_no, row in enumerate(rows[1:], start=2):
        if not row or all(not cell.strip() for cell in row):
            errors.append(f"{tsv_path}:{line_no}: blank row")
            continue

        if len(row) != 2:
            errors.append(f"{tsv_path}:{line_no}: expected exactly 2 TSV columns, got {len(row)}: {row!r}")
            continue

        topic = row[0].strip()
        query = row[1].strip()

        if not topic:
            errors.append(f"{tsv_path}:{line_no}: empty query_topic")
        elif not TOPIC_RE.match(topic):
            errors.append(f"{tsv_path}:{line_no}: invalid query_topic {topic!r}; expected {TOPIC_RE.pattern}")

        if topic in seen:
            errors.append(f"{tsv_path}:{line_no}: duplicate query_topic {topic!r}")
        seen.add(topic)

        if not query:
            errors.append(f"{tsv_path}:{line_no}: empty query")
        else:
            if any(ch in query for ch in SMART_QUOTES):
                errors.append(f"{tsv_path}:{line_no}: query contains smart quotes; use plain ASCII quotes")

            ok, reason = balanced_lucene_syntax(query)
            if not ok:
                errors.append(f"{tsv_path}:{line_no}: {reason}")

            # Lowercase boolean words are usually literal terms in Lucene query_string.
            # Warn rather than error because some users intentionally search for words.
            for bad in (" and ", " or ", " not "):
                if bad in f" {query} ":
                    warnings.append(
                        f"{tsv_path}:{line_no}: possible lowercase Lucene boolean operator {bad.strip()!r}"
                    )

            scope_modes[topic] = query_scope_mode(query, field=field)

        tiers[topic] = query

    if expected_topics is not None and seen != expected_topics:
        errors.append(
            f"{tsv_path}: topics mismatch; expected {sorted(expected_topics)}, got {sorted(seen)}"
        )

    modes = {mode for mode in scope_modes.values() if mode}
    if len(modes) > 1:
        warnings.append(
            f"{tsv_path}: mixed field-scoping styles detected by convention check: {scope_modes}"
        )

    return StaticValidationResult(tiers=tiers, errors=errors, warnings=warnings)


def unescape_lucene_quoted(text: str) -> str:
    """Lightweight unescape for quoted Lucene text."""
    return text.replace(r'\"', '"').replace(r"\\", "\\")


def extract_terms(query: str, field_names: Iterable[str]) -> list[str]:
    """
    Extract quoted phrases plus bare atoms for analyzer checks.

    This is deliberately not a full Lucene parser. It is meant to find terms that
    are worth sending to _analyze, especially short/punctuated clinical terms.
    """
    quoted = [unescape_lucene_quoted(m) for m in QUOTED.findall(query)]
    scrubbed = QUOTED.sub(" ", query)

    skip = set(field_names) | {name.lower() for name in field_names}
    bare: list[str] = []
    for token in BARE_ATOM.findall(scrubbed):
        if token.upper() in BOOLEAN_WORDS:
            continue
        if token in {"AND", "OR", "NOT"}:
            continue
        if token.lower() in skip:
            continue
        # Exclude pure integers from things like range syntax, but keep 5ASA/6MP.
        if token.isdigit():
            continue
        bare.append(token)

    # Preserve first-seen order while deduplicating.
    seen: set[str] = set()
    out: list[str] = []
    for term in quoted + bare:
        if term not in seen:
            out.append(term)
            seen.add(term)
    return out


def is_suspect(term: str) -> bool:
    """Terms whose matching is likely to be analyzer-sensitive."""
    stripped = term.strip()
    if not stripped:
        return False

    pieces = re.split(r"\s+", stripped)
    return (
        bool(SUSPECT_PUNCT.search(stripped))
        or len(stripped) <= 3
        or stripped[0].isdigit()
        or any(piece.isupper() and len(piece) <= 5 for piece in pieces)
        or any(any(ch.isdigit() for ch in piece) and any(ch.isalpha() for ch in piece) for piece in pieces)
    )


def spaced_variants(term: str, tokens: list[str]) -> set[str]:
    """Generate fallback spellings that often analyze equivalently."""
    return {
        term.replace("-", " "),
        term.replace("/", " "),
        term.replace("&", " and "),
        term.replace("-", ""),
        term.replace("/", ""),
        " ".join(tokens),
    }


def make_es_client(hosts: str) -> Any:
    try:
        from elasticsearch import Elasticsearch
    except ImportError as exc:
        raise RuntimeError("pip install elasticsearch") from exc

    # elasticsearch-py accepts a string URL in common 7.x and 8.x setups.
    return Elasticsearch(hosts)


def es_analyze(es: Any, index: str, field: str, text: str) -> list[str]:
    """Analyze text using ES7 body= style, with ES8 kwargs fallback."""
    try:
        resp = es.indices.analyze(index=index, body={"field": field, "text": text})
    except TypeError:
        resp = es.indices.analyze(index=index, field=field, text=text)
    return [tok["token"] for tok in resp.get("tokens", [])]


def total_hits(resp: dict[str, Any]) -> int:
    total = resp["hits"]["total"]
    return int(total["value"] if isinstance(total, dict) else total)


def es_phrase_count(es: Any, index: str, field: str, phrase: str) -> int:
    query = {"match_phrase": {field: phrase}}
    try:
        resp = es.search(index=index, body={"query": query, "size": 0, "track_total_hits": True})
    except TypeError:
        resp = es.search(index=index, query=query, size=0, track_total_hits=True)
    return total_hits(resp)


def es_query_string_count(es: Any, index: str, field: str, query_string: str) -> int:
    query = {"query_string": {"default_field": field, "query": query_string}}
    try:
        resp = es.search(index=index, body={"query": query, "size": 0, "track_total_hits": True})
    except TypeError:
        resp = es.search(index=index, query=query, size=0, track_total_hits=True)
    return total_hits(resp)


def run_live_checks(
    tiers: dict[str, str],
    hosts: str,
    index: str,
    field: str,
    controls: list[str],
    max_suspects: int,
    strict_live: bool,
) -> LiveValidationResult:
    """Run optional ES analyzer and hit-count checks."""
    errors: list[str] = []
    warnings: list[str] = []
    es = make_es_client(hosts)

    print("=" * 88)
    print("CONTROLS: known-common terms; nonzero suggests --index/--field/analyzer are wired correctly")
    print("=" * 88)
    zero_controls = 0
    for control in controls:
        try:
            toks = es_analyze(es, index, field, control)
            hits = es_phrase_count(es, index, field, control)
        except Exception as exc:  # ES exceptions vary by version.
            errors.append(f"control {control!r}: Elasticsearch error: {exc}")
            print(f"  {control!r:36} ERROR: {exc}")
            continue

        print(f"  {control!r:36} tokens={toks!r} hits={hits}")
        if hits == 0:
            zero_controls += 1
            msg = f"control {control!r} returned 0 hits; check --index/--field/analyzer or control choice"
            warnings.append(msg)
            print(f"    !! WARNING: {msg}")

    if strict_live and controls and zero_controls == len(controls):
        errors.append("all control terms returned 0 hits")

    topic_terms: dict[str, list[str]] = {
        topic: extract_terms(query, field_names=DEFAULT_FIELD_NAMES | {field})
        for topic, query in tiers.items()
    }

    print("\n" + "=" * 88)
    print("SUSPECT TERM ANALYSIS: analyzer-sensitive quoted phrases and bare atoms")
    print("=" * 88)
    analyzed_cache: dict[str, tuple[list[str], int]] = {}

    for topic, terms in topic_terms.items():
        suspects = [term for term in terms if is_suspect(term)]
        print("\n" + "-" * 88)
        print(f"{topic}: {len(terms)} extracted terms, {len(suspects)} analyzer-sensitive")
        print("-" * 88)

        if len(suspects) > max_suspects:
            warnings.append(
                f"{topic}: {len(suspects)} suspect terms; displaying first {max_suspects}. "
                "Increase --max-suspects to inspect all."
            )

        for term in suspects[:max_suspects]:
            try:
                if term not in analyzed_cache:
                    toks = es_analyze(es, index, field, term)
                    hits = es_phrase_count(es, index, field, term)
                    analyzed_cache[term] = (toks, hits)
                toks, hits = analyzed_cache[term]
            except Exception as exc:
                errors.append(f"[{topic}] {term!r}: Elasticsearch error: {exc}")
                print(f"  {term!r:40} ERROR: {exc}")
                continue

            flag = ""
            if not toks:
                msg = f"[{topic}] {term!r}: analyzer produced empty token stream; term can never match"
                warnings.append(msg)
                flag = "  <-- EMPTY TOKENS"
                if strict_live:
                    errors.append(msg)
            elif hits == 0:
                msg = f"[{topic}] {term!r}: match_phrase returned 0 hits; verify a fallback variant covers it"
                warnings.append(msg)
                flag = "  <-- 0 hits"
            print(f"  {term!r:40} -> {toks!r} hits={hits}{flag}")

    print("\n" + "=" * 88)
    print("PER-TIER query_string hit counts")
    print("=" * 88)
    for topic, query in tiers.items():
        try:
            hits = es_query_string_count(es, index, field, query)
            print(f"  {topic:28} hits={hits}")
            if hits == 0:
                msg = f"{topic}: whole-tier query_string returned 0 hits"
                warnings.append(msg)
                if strict_live:
                    errors.append(msg)
        except Exception as exc:
            errors.append(f"{topic}: query_string Elasticsearch error: {exc}")
            print(f"  {topic:28} ERROR: {exc}")

    print("\n" + "=" * 88)
    print("FALLBACK CHECK: split suspect terms with token-equivalent variants in the same tier")
    print("=" * 88)
    for topic, terms in topic_terms.items():
        term_set = set(terms)
        for term in [t for t in terms if is_suspect(t)]:
            try:
                toks, _hits = analyzed_cache.get(term, (es_analyze(es, index, field, term), -1))
            except Exception:
                continue
            if not toks:
                print(f"  [{topic}] {term!r}: EMPTY -- remove or rephrase")
                continue
            variants = spaced_variants(term, toks)
            covered = (variants & term_set) - {term}
            if len(toks) > 1 and not covered and any(len(tok) == 1 for tok in toks):
                print(
                    f"  [{topic}] {term!r} -> {toks!r}: contains single-character token; "
                    "confirm analyzer does not drop it in documents"
                )

    return LiveValidationResult(errors=errors, warnings=warnings)


def print_messages(title: str, messages: list[str], stream: Any = sys.stderr) -> None:
    if not messages:
        return
    print(title, file=stream)
    for msg in messages:
        print(f"  - {msg}", file=stream)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate query topics TSV files and optionally test Lucene tokenization against Elasticsearch."
    )
    parser.add_argument("--tsv", required=True, help="Path to query_topics_*.tsv")
    parser.add_argument(
        "--expected-topics",
        default="auto",
        help=(
            "Comma-separated required topics, 'auto' to infer from filename, or 'none' to disable. "
            "Example: medication_tier1,medication_tier2,medication_tier3"
        ),
    )
    parser.add_argument("--field", default="note", help="Analyzed text field targeted by the queries")
    parser.add_argument("--fail-on-warning", action="store_true", help="Exit nonzero for static warnings")

    parser.add_argument("--live", action="store_true", help="Run live Elasticsearch analyzer and hit-count checks")
    parser.add_argument("--hosts", default="http://localhost:9200", help="Elasticsearch host URL")
    parser.add_argument("--index", help="Elasticsearch index name; required with --live")
    parser.add_argument(
        "--controls",
        default="infliximab,colectomy,ulcerative colitis",
        help="Comma-separated control terms for live checks",
    )
    parser.add_argument(
        "--max-suspects",
        type=int,
        default=250,
        help="Maximum suspect terms to print per topic during live checks",
    )
    parser.add_argument(
        "--strict-live",
        action="store_true",
        help="Treat empty-token suspect terms, all-zero controls, and zero-hit tiers as errors",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tsv_path = Path(args.tsv)
    expected_topics = parse_expected_topics(args.expected_topics, tsv_path)

    static = validate_tsv_shape(tsv_path, expected_topics=expected_topics, field=args.field)

    print_messages("STATIC TSV VALIDATION WARNINGS", static.warnings)
    if static.errors:
        print_messages("STATIC TSV VALIDATION FAILED", static.errors)
        return 2
    if args.fail_on_warning and static.warnings:
        return 2

    print(f"STATIC TSV VALIDATION PASSED: {tsv_path} ({len(static.tiers)} query topics)")

    if not args.live:
        return 0

    if not args.index:
        print("--index is required with --live", file=sys.stderr)
        return 1

    controls = [item.strip() for item in args.controls.split(",") if item.strip()]
    live = run_live_checks(
        tiers=static.tiers,
        hosts=args.hosts,
        index=args.index,
        field=args.field,
        controls=controls,
        max_suspects=args.max_suspects,
        strict_live=args.strict_live,
    )

    print_messages("LIVE VALIDATION WARNINGS", live.warnings)
    if live.errors:
        print_messages("LIVE VALIDATION FAILED", live.errors)
        return 1

    print("LIVE VALIDATION COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
