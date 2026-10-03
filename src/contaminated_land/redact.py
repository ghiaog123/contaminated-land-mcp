"""Reversible redaction for the OpenRouter hop.

Pass 1: exact, case-insensitive match of every client_name, site_address and site_id in sites.yaml (the main
defence). Pass 2: Presidio NER (spaCy en_core_web_sm) for PERSON / ORGANIZATION / LOCATION, plus a regex
recognizer for site-id-like tokens. Numbers are never redacted. The placeholder map lives in the caller's hands
only (one call, memory); nothing is written or logged.
"""

import re

PLACEHOLDER = re.compile(r"<[A-Z]+_\d+>")
_NER = {"PERSON": "PERSON", "ORGANIZATION": "ORG", "LOCATION": "LOCATION", "SITE_ID": "SITE"}
_analyzer = None


def _get_analyzer():
    """Lazy, once per process (spaCy load is ~2 s)."""
    global _analyzer
    if _analyzer is None:
        from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        nlp = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
        ).create_engine()
        _analyzer = AnalyzerEngine(nlp_engine=nlp, supported_languages=["en"])
        _analyzer.registry.add_recognizer(
            PatternRecognizer(supported_entity="SITE_ID", patterns=[Pattern("site_id", r"\b[A-Z]{2,}-\d+\b", 0.9)])
        )
    return _analyzer


class Redactor:
    def __init__(self, sites: list[dict], keep: tuple[str, ...] = ()):
        """sites: rows of data/lab/sites.yaml. Their client_name, site_address and site_id are always redacted
        (exact match). keep: strings (analyte names, criteria ids); an NER span that is a whole word or phrase
        inside one is left alone."""
        known = [
            (r[k], t)
            for r in sites
            for k, t in (("client_name", "CLIENT"), ("site_address", "ADDRESS"), ("site_id", "SITE"))
            if r.get(k)
        ]
        known.sort(key=lambda kt: -len(kt[0]))
        self._types = {v.lower(): t for v, t in known}
        self._exact = re.compile("|".join(re.escape(v) for v, _ in known), re.I) if known else None
        self._keep = {k.lower() for k in keep}

    def redact(self, text: str, ner: bool = True) -> tuple[str, dict[str, str]]:
        """Return (redacted_text, mapping placeholder -> original). Placeholders like <CLIENT_1>, <ADDRESS_1>.
        Same exact text gets the same placeholder within one call."""
        spans = []  # (start, end, type)
        if self._exact:
            spans += [(m.start(), m.end(), self._types[m.group().lower()]) for m in self._exact.finditer(text)]
        if ner:
            taken = spans + [(m.start(), m.end(), "") for m in PLACEHOLDER.finditer(text)]
            for r in sorted(
                _get_analyzer().analyze(text=text, language="en", entities=list(_NER)), key=lambda r: -(r.end - r.start)
            ):
                end = r.start + len(text[r.start : r.end].rstrip(".,;:"))
                # whole-word match: "Mercury" inside "Mercury (inorganic)" is kept, "Ben" inside "benzene" is not
                word = re.compile(r"(?<!\w)" + re.escape(text[r.start : end].lower()) + r"(?!\w)")
                if any(word.search(k) for k in self._keep) or any(r.start < e and s < end for s, e, _ in taken):
                    continue
                spans.append((r.start, end, _NER[r.entity_type]))
                taken.append(spans[-1])
        spans.sort()
        mapping, seen, counts, out, pos = {}, {}, {}, [], 0
        for s, e, t in spans:
            orig = text[s:e]
            if (t, orig) not in seen:
                counts[t] = counts.get(t, 0) + 1
                seen[(t, orig)] = f"<{t}_{counts[t]}>"
                mapping[seen[(t, orig)]] = orig
            out += [text[pos:s], seen[(t, orig)]]
            pos = e
        return "".join(out) + text[pos:], mapping

    def restore(self, text: str, mapping: dict[str, str]) -> str:
        return PLACEHOLDER.sub(lambda m: mapping.get(m.group(), m.group()), text)
