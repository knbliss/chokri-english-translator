#!/usr/bin/env python3
"""Build the bundled flashcard deck JSON for beginner learners.

Reads ../../data/chokri_english_MASTER.csv and produces a small, curated
deck instead of the full ~8.5k-verse Bible corpus, split into two types
the app lets the learner pick between:

  - "word"     - a single Chokri word and its meaning (e.g. "Vorichi" ->
                 "Come"). Pulled from the project's non-Bible sources (a
                 Chokri textbook extract and languageshome.com), with
                 grammar-terminology entries filtered out.
  - "sentence" - a full Chokri sentence and its translation. Combines the
                 non-Bible multi-word phrases with a curated supplement of
                 short, concrete narrative lines from the Bible corpus
                 (e.g. "He entered and was passing through Jericho"),
                 filtered to exclude doctrinal/abstract vocabulary,
                 genealogies, and sentence fragments. Biblical person and
                 place names in that supplement are swapped for generic
                 English names/places (see anonymize_names.py) so these
                 read like ordinary everyday sentences rather than
                 recognizably-Bible verses.

Requires the `wordfreq` package (pip install wordfreq) to score how
common each English word is, used to drop obscure/jargon entries.
"""
import csv
import json
import re
from pathlib import Path

from wordfreq import zipf_frequency

from anonymize_names import anonymize

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "data" / "chokri_english_MASTER.csv"
OUT = ROOT / "assets" / "data" / "deck.json"

WORD_RE = re.compile(r"[A-Za-z']+")
CHOKRI_WORD_RE = re.compile(r"[A-Za-zÀ-ÿüöäÜÖÄ']+")

# --- "word"/non-Bible-sentence filter (non-Bible sources) ------------------

NON_BIBLE_SOURCES = {"book_extracted", "languageshome.com"}

GRAMMAR_JARGON_RE = re.compile(
    r"\b(adjectives?|adverbs?|nouns?|verbs?|pronouns?|prepositions?|"
    r"conjunctions?|conjuctions?|tenses?|voice|syllables?|affixes?|prefixes?|"
    r"suffixes?|infixes?|articles?|clauses?|antonyms?|synonyms?|idioms?|"
    r"consonants?|vowels?|certificate|heading|magazine|interrogatives?|"
    r"exclamations?|subject|object|grammar|tone|abbreviations?)\b",
    re.IGNORECASE,
)

MIN_SINGLE_WORD_ZIPF = 3.0

# A few specific textbook/document-structure labels that slip past the
# regex above (not grammar jargon, but not conversational either).
EVERYDAY_EXACT_BLOCKLIST = {
    "question words",
    "sender's address",
    "senders address",
    "body of the letter",
    "receiver's address",
    "receivers address",
    "singular number",
    "plural number",
    "dual number",
}

# --- "sentence" filter for the Bible corpus ---------------------------------

NARRATIVE_VERBS_RE = re.compile(
    r"\b(said|says|saying|asked|answered|replied|told|went|go|goes|going|came|"
    r"comes|coming|arose|rose|departed|left|leaves|enter(?:ed|s)?|saw|see|sees|"
    r"took|takes?|taking|gave|gives?|giving|sat|sits?|sitting|stood|stand|"
    r"stands?|standing|walked|walks?|walking|called|calls?|calling|heard|"
    r"hears?|hearing|followed|follows?|following|returned|returns?|returning|"
    r"brought|brings?|bringing|found|finds?|finding|ate|eats?|eating|drank|"
    r"drinks?|drinking|slept|sleeps?|sleeping|woke|wakes?|waking|wept|weeps?|"
    r"weeping|laughed|laughs?|laughing|ran|runs?|running|knocked|opened|"
    r"opens?|opening|closed|closes?|closing|carried|carries|carrying)\b",
    re.IGNORECASE,
)

DOCTRINAL_BLOCK_RE = re.compile(
    r"\b(faith|grace|sins?|salvation|righteous(?:ness)?|spirits?|glory|"
    r"kingdoms?|eternal|believe[sd]?|blessed|blessings?|holy|worthy|christ|"
    r"covenants?|promise[sd]?|commandments?|repent(?:ance)?|forgive(?:ness|n)?|"
    r"gospels?|prophe(?:cy|cies|t|ts|sied)|resurrection|sacrifice[sd]?|baptiz\w*|"
    r"circumcis\w*|disciples?|apostles?|churc(?:h|hes)|sanctif\w*|redeem\w*|"
    r"atonement|doctrines?|scriptures?|testaments?|mercy|wrath|judgment|"
    r"temples?|altars?|priests?|preach\w*|miracles?|heal(?:ed|ing)?|demons?|"
    r"devils?|satan|angels?|heaven[sly]*|hell|souls?|flesh|law of moses|"
    r"pharisees?|sadducees?|elders?|hallelujah|gods?|lords?|saints?|blasphem\w*|"
    r"assembl(?:y|ies)|denari\w*|cloaks?|brass|jeopardy|paralytic)\b",
    re.IGNORECASE,
)

# Discourse markers and relative-clause constructions typical of formal,
# literary Bible-translation English (archaic register), filtered
# separately from DOCTRINAL_BLOCK_RE since these aren't about religious
# subject matter -- a sentence can mention none of "faith/sin/God" and
# still read as formal/archaic because of its phrasing.
FORMAL_REGISTER_RE = re.compile(
    r"\b(behold|moreover|thus|hence|verily|indeed|therefore|whosoever|"
    r"whoever|wherefore|hereby|thereof|thereby|herein|notwithstanding|"
    r"whence|whereupon|forsooth|aught|nigh|amongst|midst|betwixt|yonder|"
    r"hither|thither|forthwith|anon|peradventure|exceedingly|greatly|"
    r"multitudes?|notable|decrees?|decreed|summon(?:ed|s)?|reasoned|"
    r"astonish\w*|marvel\w*|countenance|raiment|girded|sojourn\w*|tarried|"
    r"no small|not a little|"
    r"he who|she who|him who|her who|those who|that they|to whom|of whom|"
    r"in whom|for whom|with whom|whose|which he|which she|which they|"
    r"which is|which was)\b",
    re.IGNORECASE,
)

# A sentence opening with a capitalized present-participle ("Seeing the
# multitudes...", "Having said these things...") is a fronted participial
# clause -- a formal/literary construction common in this translation's
# style, rare in ordinary spoken English.
FRONTED_PARTICIPLE_RE = re.compile(r'^"?[A-Z]\w*ing\b')

# Stopwords/pronouns excluded when scoring how "everyday" the vocabulary of
# a sentence is -- these are common regardless of register, so they'd mask
# the formal/archaic content words we actually want to detect.
_SIMPLICITY_STOPWORDS = frozenset(
    "a an the of to in on at by for with from into onto up down out over "
    "under again further then once here there when where why how all any "
    "both each few more most other some such no nor not only own same so "
    "than too very s t can will just don now i me my myself we our ours "
    "ourselves you your yours yourself yourselves he him his himself she "
    "her hers herself it its itself they them their theirs themselves "
    "what which who whom this that these those am is are was were be "
    "been being have has had having do does did doing and but if or "
    "because as until while".split()
)

BIBLE_MIN_AVG_ZIPF = 4.4
BIBLE_MIN_WORD_ZIPF = 3.3


def bible_simplicity_score(eng: str):
    """Average and minimum word-commonness (zipf) of content words,
    skipping stopwords and likely proper nouns (capitalized, not
    sentence-initial). Checking the minimum (not just the average) catches
    a sentence that's simple overall except for one obscure/archaic word."""
    scores = []
    for i, w in enumerate(WORD_RE.findall(eng)):
        lw = w.lower()
        if lw in _SIMPLICITY_STOPWORDS:
            continue
        if i > 0 and w[0].isupper():
            continue
        scores.append(zipf_frequency(lw, "en"))
    if not scores:
        return None
    return sum(scores) / len(scores), min(scores)

GENEALOGY_RE = re.compile(
    r"\b(begat|genealogy|the father of|the son of|the daughter of|generations?)\b",
    re.IGNORECASE,
)

# Chokri words for "God"/"Lord" (Jihova, Niepoo/Nyepoo/Nyiepoo, Poo/Nepoo,
# Rüo and their simple suffixed forms). Needed because some verses name God
# or the Lord in the Chokri text even where the English gloss paraphrases
# around it (e.g. "blasphemes" for a line that names God directly).
CHOKRI_DEITY_RE = re.compile(
    r"\b(jihova\w*|n?y?i?e?poo\w*|apoo|upoo|rüo)\b",
    re.IGNORECASE,
)

BIBLE_MIN_WORDS = 3
BIBLE_MAX_WORDS = 12


def word_count(s: str) -> int:
    return len(WORD_RE.findall(s))


def chokri_word_count(s: str) -> int:
    return len(CHOKRI_WORD_RE.findall(s))


def looks_like_sentence(eng: str) -> bool:
    s = eng.strip().strip('"').strip("'").strip()
    if not s:
        return False
    if not s[0].isupper():
        return False
    if s[-1] not in ".!?\"'":
        return False
    return True


def keep_everyday(row: dict) -> bool:
    eng = row["english"]
    if eng.strip().lower() in EVERYDAY_EXACT_BLOCKLIST:
        return False
    if GRAMMAR_JARGON_RE.search(eng):
        return False
    words = WORD_RE.findall(eng)
    if not words:
        return False
    if len(words) == 1:
        if zipf_frequency(words[0].lower(), "en") < MIN_SINGLE_WORD_ZIPF:
            return False
    return True


def keep_bible_simple(row: dict) -> bool:
    eng = row["english"]
    chokri = row["chokri"]
    if GENEALOGY_RE.search(eng):
        return False
    if DOCTRINAL_BLOCK_RE.search(eng):
        return False
    if CHOKRI_DEITY_RE.search(chokri):
        return False
    if FORMAL_REGISTER_RE.search(eng):
        return False
    if FRONTED_PARTICIPLE_RE.match(eng):
        return False
    if not NARRATIVE_VERBS_RE.search(eng):
        return False
    n = word_count(eng)
    if n < BIBLE_MIN_WORDS or n > BIBLE_MAX_WORDS:
        return False
    if not looks_like_sentence(eng):
        return False
    score = bible_simplicity_score(eng)
    if score is None:
        return False
    avg_zipf, min_zipf = score
    if avg_zipf < BIBLE_MIN_AVG_ZIPF or min_zipf < BIBLE_MIN_WORD_ZIPF:
        return False
    return True


TYPE_META = {
    "word": {
        "name": "Single Word Meanings",
        "description": "One Chokri word at a time, with its English meaning.",
    },
    "sentence": {
        "name": "Sentence Flashcards",
        "description": "Full everyday sentences in Chokri and English.",
    },
}


def main():
    rows = []
    with open(SRC, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("quality") != "good":
                continue
            chokri = (row.get("chokri") or "").strip()
            english = (row.get("english") or "").strip()
            if not chokri or not english:
                continue
            row["chokri"] = chokri
            row["english"] = english
            rows.append(row)

    # Stable-sort so Bible-derived rows end up last in the deck (the Bible
    # rows happen to come first in the source CSV otherwise). Non-Bible
    # rows keep their original relative order; Bible rows keep theirs too,
    # just moved after everything else.
    rows.sort(key=lambda r: r.get("source") == "Bible_NAG5BSI_WEB")

    cards = []
    type_counts = {"word": 0, "sentence": 0}

    for i, row in enumerate(rows):
        source = row.get("source", "")
        chokri = row["chokri"]
        english = row["english"]

        if source in NON_BIBLE_SOURCES:
            if not keep_everyday(row):
                continue
            card_type = "word" if chokri_word_count(chokri) == 1 else "sentence"
        elif source == "Bible_NAG5BSI_WEB":
            if not keep_bible_simple(row):
                continue
            chokri = anonymize(chokri)
            english = anonymize(english)
            card_type = "sentence"
        else:
            continue

        card = {
            "id": f"{card_type}-{i}",
            "type": card_type,
            "chokri": chokri,
            "english": english,
        }
        cards.append(card)
        type_counts[card_type] += 1

    deck = {
        "generatedFrom": "data/chokri_english_MASTER.csv",
        "count": len(cards),
        "types": [
            {
                "id": type_id,
                "name": TYPE_META[type_id]["name"],
                "description": TYPE_META[type_id]["description"],
                "count": type_counts[type_id],
            }
            for type_id in ("sentence", "word")
        ],
        "cards": cards,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=0, separators=(",", ":"))

    print(f"Wrote {len(cards)} cards to {OUT}")
    for type_id, n in type_counts.items():
        print(f"  {type_id}: {n}")


if __name__ == "__main__":
    main()
