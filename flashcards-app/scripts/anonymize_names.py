"""Replace biblical person & place names with generic English ones.

Used by build_deck.py on the curated Bible-sentence supplement so those
lines read like ordinary everyday sentences rather than recognizably-Bible
verses. Each map entry's key is a spelling variant as it actually appears
in the source data (English spelling, and separately any differing Chokri
transliteration); the same replacement is used for every variant of a
given person/place, and identically on both the Chokri and English side.

The same replacement is applied to both languages because this Bible
translation already borrows proper nouns into Chokri largely unchanged
(e.g. "Jerusalem", "Pilate", "Mary" appear verbatim in the Chokri text).
Chokri attaches grammatical suffixes directly onto those borrowed nouns
(e.g. "Jericholü" = Jericho + locative "-lü"), so the replacement is done
by matching the proper-noun root and keeping whatever follows it, which
preserves Chokri grammar: "Jericholü" -> "Oakridgelü".
"""
import re

PERSON_MAP = {
    "Jesus": "Daniel", "Jisu": "Daniel",
    "John": "Henry",
    "Peter": "Oliver",
    "James": "Charlie",
    "Mark": "George",
    "Paul": "Nathan", "Saul": "Nathan",
    "David": "Edward",
    "Moses": "Arthur", "Mosae": "Arthur",
    "Pilate": "Frank",
    "Barabbas": "Victor",
    "Lazarus": "Walter",
    "Magdalene": "Baker", "Magdaline": "Baker",
    "Mary": "Anna",
    "Trophimus": "Samuel", "Trofima": "Samuel",
    "Apollos": "Patrick", "Apollo": "Patrick",
    "Barnabas": "Leonard",
    "Nicodemus": "Gregory",
    "Zacharias": "Vincent", "Zecharia": "Vincent",
    "Erastus": "Russell", "Evasta": "Russell",
    "Thomas": "Simon",
}

PLACE_MAP = {
    "Jerusalem": "Millbrook",
    "Galilee": "Lakeview",
    "Judea": "Fernvalley",
    "Jericho": "Oakridge",
    "Capernaum": "Fairview", "Capernaun": "Fairview",
    "Nazareth": "Elmwood", "Nazerath": "Elmwood",
    "Gennesaret": "Crystalton", "Genezaret": "Crystalton",
    "Syria": "Westland",
    "Cilicia": "Eastfield",
    "Antioch": "Northgate",
    "Corinth": "Southport", "Korinthia": "Southport", "Kornif": "Southport",
    "Athens": "Brookside",
    "Tarsus": "Rosedale",
    "Mysia": "Dunmore",
    "Pamphylia": "Ashford",
    "Pisidia": "Hartwell",
    "Troas": "Westbury",
    "Miletus": "Thornton", "Mileto": "Thornton",
    "Israel": "Riverdale",
    "Judah": "Ashgrove",
}

ALL_MAP = {**PERSON_MAP, **PLACE_MAP}

# Longest variants first so no shorter key can shadow part of a longer one.
_VARIANTS = sorted(ALL_MAP.keys(), key=len, reverse=True)
_PATTERN = re.compile(r"\b(" + "|".join(re.escape(v) for v in _VARIANTS) + r")([\w'-]*)")


def anonymize(text: str) -> str:
    def repl(m: re.Match) -> str:
        root, suffix = m.group(1), m.group(2)
        replacement = ALL_MAP[root]
        # "Jesus'" (bare apostrophe possessive, valid since "Jesus" ends in
        # "s") needs an extra "s" once the root no longer ends in "s".
        if suffix == "'" and not replacement.endswith("s"):
            suffix = "'s"
        return replacement + suffix

    return _PATTERN.sub(repl, text)
