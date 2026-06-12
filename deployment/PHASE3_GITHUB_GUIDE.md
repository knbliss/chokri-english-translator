# Phase 3 — GitHub Repository Setup

---

## Step 1 — Create the repository

1. Go to [github.com](https://github.com) → **New repository**
2. Name: **chokri-english-translator**
3. Description: *The first open-source machine translation system for Chokri (Nagaland, India)*
4. Visibility: **Public**
5. Do NOT initialise with a README (we already have one)
6. Click **Create repository**

---

## Step 2 — Push the project

```bash
cd /Users/kuyinienu/Documents/Claude/Chokri_English

git init
git add \
  README.md \
  requirements.txt \
  chokri_english_MASTER.csv \
  data/ \
  1_update_to_web.py \
  2_clean_split.py \
  3_finetune.py \
  4_evaluate.py \
  5_app.py \
  collaboration/ \
  deployment/ \
  supabase_setup.sql

git commit -m "Initial release: v1.0 — 8,245 Chokri–English pairs + fine-tuned NLLB model"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/chokri-english-translator.git
git push -u origin main
```

> Do NOT add `model_best/` to git — the model is large (~1.2 GB) and already hosted
> on HuggingFace Hub. Add it to `.gitignore` instead.

---

## Step 3 — Create a .gitignore

Create this file before your first commit:

```
# Model weights (hosted on HF Hub instead)
model_best/
checkpoints/
*.zip

# Python
__pycache__/
*.pyc
chokri-env/
.env

# Local data files
user_contributions.csv
page_source.html
```

---

## Step 4 — Publish v1.0 as a release

1. In your GitHub repo → **Releases** → **Create a new release**
2. Tag: `v1.0`
3. Title: `v1.0 — 8,040 Chokri–English sentence pairs`
4. Description (copy-paste this):

```
## Chokri–English Dataset v1.0

**8,040 sentence pairs** — the first versioned, publicly released Chokri corpus.

### Sources
- Chokri New Testament (Bible Society of India, sourced from bible.com)
- Bielenberg (2001) linguistics reference paper

### Files
- `chokri_english_MASTER.csv` — full dataset
- `data/train.csv` — 80% training split (~6,432 pairs)
- `data/val.csv` — 10% validation split (~804 pairs)
- `data/test.csv` — 10% test split (~804 pairs)

### Model
Fine-tuned NLLB-200-distilled-600M checkpoint available at:
`huggingface.co/YOUR_HF_USERNAME/chokri-nllb-finetuned`

### Live demo
`huggingface.co/spaces/YOUR_HF_USERNAME/chokri-english-translator`
```

5. Attach the CSV files as release assets (optional but good for discoverability)
6. Click **Publish release**

---

## Step 5 — Update README placeholders

In `README.md`, replace:
- `YOUR_HF_USERNAME` → your actual HF username
- `YOUR_GITHUB_USERNAME` → your actual GitHub username
- `_your name_` → your name in the Contributors table

---

## After v1.1 (community contributions)

Once you have a batch of reviewer-approved pairs merged into MASTER:
1. Run `2_clean_split.py` to re-split
2. Re-run `3_finetune.py` for the updated model
3. Upload new model to HF Hub
4. Create a new GitHub release `v1.1` with the updated CSV and split counts
5. Credit contributors by name or initials in the release notes
