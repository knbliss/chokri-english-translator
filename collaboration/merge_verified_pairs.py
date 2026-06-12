"""
Merge VERIFIED contributions from the Google Sheet export into the master corpus.

Usage:
    1. In the Google Sheet: File → Download → CSV
    2. Save it as collaboration/sheet_export.csv
    3. Run:  python collaboration/merge_verified_pairs.py

Only rows with status == 'verified' are merged. Duplicates are skipped.
A backup of the master corpus is made before writing.
"""
import csv, os, shutil
from datetime import datetime

# Paths (relative to project root)
ROOT        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEET_CSV   = os.path.join(ROOT, "collaboration", "sheet_export.csv")
MASTER_CSV  = os.path.join(ROOT, "chokri_english_MASTER.csv")
BACKUP_DIR  = os.path.join(ROOT, "collaboration", "backups")


def main():
    if not os.path.exists(SHEET_CSV):
        print(f"ERROR: {SHEET_CSV} not found.")
        print("Download the Google Sheet as CSV and save it there first.")
        return

    # ── Load existing master pairs (for dedup) ────────────────────────────
    existing = set()
    master_rows = []
    with open(MASTER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            master_rows.append(row)
            existing.add((row["chokri"].strip(), row["english"].strip()))

    # ── Read sheet export, keep only verified rows ────────────────────────
    added, skipped_dup, skipped_unverified, skipped_empty = 0, 0, 0, 0
    with open(SHEET_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Be tolerant of column-name variations / casing
            status  = (row.get("status") or "").strip().lower()
            chokri  = (row.get("chokri") or "").strip()
            english = (row.get("english") or "").strip()
            contributor = (row.get("submitted_by") or "community").strip()

            if status != "verified":
                skipped_unverified += 1
                continue
            if not chokri or not english:
                skipped_empty += 1
                continue
            key = (chokri, english)
            if key in existing:
                skipped_dup += 1
                continue

            master_rows.append({
                "book": "", "chapter": "", "verse": "",
                "chokri": chokri,
                "english": english,
                "source": f"Community_{contributor}".replace(" ", "_")[:50],
            })
            existing.add(key)
            added += 1

    if added == 0:
        print("No new verified pairs to add.")
        print(f"  (skipped: {skipped_unverified} unverified, "
              f"{skipped_dup} duplicates, {skipped_empty} empty)")
        return

    # ── Backup then write ─────────────────────────────────────────────────
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"master_backup_{stamp}.csv")
    shutil.copy(MASTER_CSV, backup_path)

    with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(master_rows)

    print(f"✅ Merged {added} new verified pairs into the master corpus.")
    print(f"   Total corpus size: {len(master_rows)} pairs")
    print(f"   Backup saved to: {backup_path}")
    print(f"   (skipped: {skipped_unverified} unverified, "
          f"{skipped_dup} duplicates, {skipped_empty} empty)")
    print()
    print("Next steps:")
    print("   1. python 2_clean_split.py     # regenerate train/val/test")
    print("   2. Re-run training on Colab     # with the larger corpus")


if __name__ == "__main__":
    main()
