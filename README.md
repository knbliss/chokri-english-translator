# Chokri–English Neural Machine Translation

The first open-source machine translation system for **Chokri**, a Tibeto-Burman
language spoken by ~50,000 people in Phek district, Nagaland, northeast India.

**Live demo:** [huggingface.co/spaces/YOUR_HF_USERNAME/chokri-english-translator](https://huggingface.co/spaces/YOUR_HF_USERNAME/chokri-english-translator)

---

## Why this matters

Chokri has no existing digital translation tools. This project creates the first
one — and more importantly, builds the community infrastructure to keep improving it.

---

## Dataset

| Version | Pairs | Sources |
|---------|-------|---------|
| v1.0 | 8,245 | Bible (Nagamese script), Bielenberg 2001 linguistics paper |
| v1.1 | _in progress_ | + community contributions (reviewed) |

The dataset is in [`chokri_english_MASTER.csv`](chokri_english_MASTER.csv).
Each row: `book, chapter, verse, chokri, english, source`.

### Download

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/chokri-english-translator
```

Or download just the dataset:
[`chokri_english_MASTER.csv`](chokri_english_MASTER.csv)

---

## Model

Fine-tuned from [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M)
on the 8,245-pair Chokri corpus.

Hosted on HuggingFace Hub: `YOUR_HF_USERNAME/chokri-nllb-finetuned`

---

## Repository structure

```
├── chokri_english_MASTER.csv   ← full dataset (8,245+ pairs)
├── data/
│   ├── train.csv               ← 80% training split
│   ├── val.csv                 ← 10% validation split
│   └── test.csv                ← 10% test split
├── 1_update_to_web.py          ← scrape additional Bible data
├── 2_clean_split.py            ← clean + train/val/test split
├── 3_finetune.py               ← fine-tune NLLB-200
├── 4_evaluate.py               ← BLEU score evaluation
├── 5_app.py                    ← Gradio web app (deploy to HF Spaces as app.py)
├── requirements.txt
├── collaboration/
│   ├── 1_SHEET_SETUP_GUIDE.md  ← set up the community review Google Sheet
│   ├── 2_CONTRIBUTOR_INVITE.md ← email template for recruiting reviewers
│   └── merge_verified_pairs.py ← merge reviewer-approved pairs into MASTER
└── deployment/
    ├── PHASE2_DEPLOYMENT_GUIDE.md
    └── hf_spaces_README.md
```

---

## How to contribute

There are two ways to help:

### As a Chokri speaker (no technical skills needed)
Use the live app at the link above:
- **Correct** a wrong translation the model produced
- **Add** a sentence pair you know (proverb, everyday phrase, story)

All submissions go through a reviewer before entering the training corpus.

### As a technical contributor
1. Fork this repo
2. Improve the training pipeline, the app, or the data cleaning scripts
3. Open a pull request

---

## Running locally

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/chokri-english-translator
cd chokri-english-translator
pip install -r requirements.txt
python 5_app.py
# → open http://localhost:7860
```

The app falls back to `facebook/nllb-200-distilled-600M` if `model_best/` is not present,
so you can run it without the fine-tuned weights.

---

## Versioned releases

Dataset releases are published as [GitHub Releases](../../releases):

- **v1.0** — 8,245 pairs (Bible + Bielenberg corpus)
- **v1.1** — _upcoming_ — + community contributions

Each release includes the full CSV, the train/val/test splits, and a model checkpoint.

---

## Contributors

| Role | Names |
|------|-------|
| Project lead | _your name_ |
| Reviewers | _to be added_ |
| Data sources | Bible (Nagamese Bible Society), Bielenberg (2001) |

Community contributors are listed in the release notes for each dataset version.

---

## License

- **Code**: MIT
- **Dataset**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use with attribution
- **Model weights**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## Citation

```bibtex
@misc{chokri-translator-2025,
  title  = {Chokri--English Neural Machine Translation},
  author = {YOUR NAME},
  year   = {2025},
  url    = {https://github.com/YOUR_GITHUB_USERNAME/chokri-english-translator}
}
```
