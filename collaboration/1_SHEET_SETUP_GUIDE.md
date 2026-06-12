# Phase 1 Setup Guide — Chokri Corpus Collaboration Sheet

This guide walks you through setting up the Google Sheet + Google Form that
contributors and reviewers will use. Total setup time: ~20 minutes.

---

## Part A — Create the Google Sheet (the master database)

### 1. Import the template
1. Go to [sheets.google.com](https://sheets.google.com) → **Blank spreadsheet**
2. **File → Import → Upload** → select `chokri_corpus_sheet_template.csv`
3. Choose **"Replace current sheet"** → Import data
4. Rename the file at the top to: **Chokri–English Corpus (Master)**

### 2. Understand the columns

| Column | Who fills it | Purpose |
|--------|-------------|---------|
| `id` | Auto / you | Unique ID (e.g. C-0001). Helps track each pair. |
| `chokri` | Contributor | The Chokri sentence |
| `english` | Contributor | The English translation |
| `category` | Contributor | Bible / Everyday / Proverb / Story / School, etc. |
| `submitted_by` | Contributor | Name or initials of who added it |
| `date_submitted` | Auto | When it was added |
| `status` | **Reviewer** | `pending` → `verified` or `rejected` |
| `reviewed_by` | **Reviewer** | Which reviewer checked it |
| `date_reviewed` | **Reviewer** | When it was reviewed |
| `reviewer_notes` | **Reviewer** | Corrections, comments, reason for rejection |

> Keep the 3 `EX-` example rows at the top so everyone sees the expected format.

### 3. Add colour-coding (so reviewers can see status at a glance)
1. Select column `G` (status)
2. **Format → Conditional formatting**
3. Add three rules:
   - Text is exactly `pending` → **yellow** background
   - Text is exactly `verified` → **green** background
   - Text is exactly `rejected` → **red** background

### 4. Lock down the review columns (optional but recommended)
So general contributors don't accidentally mark their own work "verified":
1. Select columns `G:J` (status through reviewer_notes)
2. **Data → Protect sheets and ranges**
3. Set permission to **only your trusted reviewers** can edit

### 5. Add a dropdown for `status` and `category` (prevents typos)
1. Select column `G` → **Data → Data validation**
   - Criteria: *Dropdown* → add `pending`, `verified`, `rejected`
2. Select column `D` → **Data → Data validation**
   - Criteria: *Dropdown* → add `Bible`, `Everyday`, `Proverb`, `Story`, `School`, `Other`

---

## Part B — Create the Google Form (for casual contributors)

The Form keeps general contributors from touching the master Sheet directly.
Their submissions land in a separate tab, and reviewers promote good ones.

### 1. Create the form
1. Go to [forms.google.com](https://forms.google.com) → **Blank form**
2. Title: **Contribute a Chokri–English Sentence Pair**
3. Description: *"Thank you for helping build the first Chokri translation tool!
   Add a Chokri sentence and its English meaning below."*

### 2. Add these questions

| # | Question | Type | Required? |
|---|----------|------|-----------|
| 1 | Your name (or initials) | Short answer | Yes |
| 2 | Chokri sentence | Paragraph | Yes |
| 3 | English translation | Paragraph | Yes |
| 4 | Category | Multiple choice: Bible / Everyday / Proverb / Story / School / Other | Yes |
| 5 | Any notes? (optional — dialect, context, source) | Paragraph | No |
| 6 | Are you a fluent Chokri speaker? | Multiple choice: Yes, native / Yes, learned / Learning | No |

### 3. Link the form to your Sheet
1. In the Form, go to the **Responses** tab
2. Click the green **Sheets icon** → "Create new spreadsheet" OR
   **"Select existing spreadsheet"** → choose your *Chokri–English Corpus (Master)*
3. This creates a **"Form Responses 1"** tab — submissions appear here automatically

### 4. Reviewer workflow
- New submissions appear in **Form Responses 1** tab
- A reviewer reads each, then **copies good rows** into the master tab and sets
  `status = verified` (correcting the English/Chokri if needed)
- Bad/duplicate ones are marked `rejected` with a note (or just left in the responses tab)

---

## Part C — Appoint your reviewers

You chose the **"trusted reviewers approve"** model. Here's how to set it up:

1. Identify 2–4 people who know Chokri authoritatively (elders, teachers, linguists)
2. Share the **master Sheet** with them as **Editors**
3. Share the contributor **Form link** widely (general speakers, students, church groups)
4. Give reviewers this one rule: *"Only you change the `status`, `reviewed_by`,
   and `reviewer_notes` columns. Verify the spelling and meaning before marking
   `verified`."*

---

## Part D — When you're ready to retrain

Once you have a batch of `verified` rows:
1. **File → Download → CSV** (the master tab)
2. Send it to me (or run the merge script) — verified pairs get added to
   `chokri_english_MASTER.csv`, then re-split and retrain.

A script `collaboration/merge_verified_pairs.py` is provided to automate this.

---

## Quick-start checklist

- [ ] Import CSV template into Google Sheets
- [ ] Add conditional formatting (status colours)
- [ ] Add dropdowns for status + category
- [ ] Protect review columns
- [ ] Create the Google Form with 6 questions
- [ ] Link Form responses to the Sheet
- [ ] Share Sheet with reviewers (as Editors)
- [ ] Share Form link with contributors
- [ ] Recruit 2–4 reviewers
