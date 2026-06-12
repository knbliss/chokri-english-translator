"""
Step 1: Replace KJV English with WEB (World English Bible) translations
in the master corpus, where available. Non-Bible rows are kept as-is.
"""
import pandas as pd
import re

BOOK_ABBR_TO_NUM = {
    "GEN":1,"EXO":2,"LEV":3,"NUM":4,"DEU":5,"JOS":6,"JDG":7,"RUT":8,
    "1SA":9,"2SA":10,"1KI":11,"2KI":12,"1CH":13,"2CH":14,"EZR":15,
    "NEH":16,"EST":17,"JOB":18,"PSA":19,"PRO":20,"ECC":21,"SNG":22,
    "ISA":23,"JER":24,"LAM":25,"EZK":26,"DAN":27,"HOS":28,"JOL":29,
    "AMO":30,"OBA":31,"JON":32,"MIC":33,"NAM":34,"HAB":35,"ZEP":36,
    "HAG":37,"ZEC":38,"MAL":39,"MAT":40,"MRK":41,"LUK":42,"JHN":43,
    "ACT":44,"ROM":45,"1CO":46,"2CO":47,"GAL":48,"EPH":49,"PHP":50,
    "COL":51,"1TH":52,"2TH":53,"1TI":54,"2TI":55,"TIT":56,"PHM":57,
    "HEB":58,"JAS":59,"1PE":60,"2PE":61,"1JN":62,"2JN":63,"3JN":64,
    "JUD":65,"REV":66,
    # aliases
    "PSM":"PSA","PS":"PSA","SOS":"SNG","EZE":"EZK","PHI":"PHP",
    "JDE":"JUD","JDT":"JUD",
}

def clean_web_text(t):
    """Remove WEB footnote markers like {footnote text}."""
    return re.sub(r'\{[^}]*\}', '', str(t)).strip()

master = pd.read_csv("chokri_english_MASTER.csv")
web = pd.read_csv("web_bible.csv")

# Build WEB lookup: (book_num, chapter, verse) -> text
web["text_clean"] = web["t"].apply(clean_web_text)
web_lookup = {}
for _, row in web.iterrows():
    web_lookup[(int(row["b"]), int(row["c"]), int(row["v"]))] = row["text_clean"]

replaced = 0
not_found = 0
skipped = 0

new_english = []
for _, row in master.iterrows():
    if row["source"] != "Bible_NAG5BSI_KJV":
        new_english.append(row["english"])
        skipped += 1
        continue

    book_key = str(row["book"]).upper().strip()
    book_num = BOOK_ABBR_TO_NUM.get(book_key)
    if book_num is None:
        new_english.append(row["english"])
        not_found += 1
        continue

    key = (book_num, int(row["chapter"]), int(row["verse"]))
    web_text = web_lookup.get(key)
    if web_text:
        new_english.append(web_text)
        replaced += 1
    else:
        new_english.append(row["english"])
        not_found += 1

master["english"] = new_english
master["source"] = master["source"].replace("Bible_NAG5BSI_KJV", "Bible_NAG5BSI_WEB")
master.to_csv("chokri_english_MASTER.csv", index=False)

print(f"Done.")
print(f"  Replaced with WEB: {replaced}")
print(f"  Not found in WEB:  {not_found}")
print(f"  Non-Bible kept:    {skipped}")
print(f"  Total rows:        {len(master)}")
