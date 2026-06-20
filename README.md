---
title: Chokri English Translator
emoji: 🌏
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.0.0"
app_file: 5_app.py
pinned: false
---

# Chokri–English Neural Machine Translation

The first open-source machine translation system for **Chokri**, a Tibeto-Burman
language spoken by ~50,000 people in Phek district, Nagaland, northeast India.

**Live demo:** [huggingface.co/spaces/knbliss/chokri-english-translator](https://huggingface.co/spaces/knbliss/chokri-english-translator)

> **Note:** This is an early-stage prototype. Translations are based on an unofficial dialect version of Chokri and should not be treated as linguistically accurate. We are working with the CCLB to adopt the officially accepted Chokri standard.

---

## Why this matters

My children grew up in Australia and understand only a little Chokri — my mother tongue. They struggle to speak with their grandparents and the older people in our village who do not speak English. This gap is common among Chakhesang families living outside Nagaland, where passing the language on to the next generation is a real challenge.

This project is one small step toward bridging that gap — making Chokri more accessible across distance and generations.

On the technical side, Chokri is absent from every major translation platform (Google, Microsoft, DeepL) and from Meta's NLLB-200, despite it covering 200+ languages. This is the first open-source translation tool for Chokri.

---

## Dataset

| Version | Pairs | Sources |
|---------|-------|---------|
| v1.0 | 8,040 | Chokri New Testament (Bible Society of India), Bielenberg 2001 linguistics paper |
| v1.1 | _in progress_ | + community contributions (reviewed) |

The dataset is maintained privately to protect the integrity of community contributions
and ensure the Chokri-speaking community retains stewardship over their language data.
The trained model and tools are open-source; the underlying corpus is not publicly distributed.

> **Important — dataset and translation accuracy:** This tool is currently trained on a Bible translation that has **not** been accepted by the **Chokri Chakhesang Literary Board (CCLB)** — the official authority on Chokri language and literature. The version used contains accents and dialect features from a specific region, and does not represent standard Chokri.
>
> We do not want this tool to be used as a reference for correct Chokri spelling, grammar, or translation. It is an early-stage prototype, and we are actively working to replace the current dataset with the CCLB-accepted version. Until then, please treat all translations as approximate and unverified against the official standard.
>
> If you are from the CCLB or can help us access the official Chokri texts, please get in touch.

---

## Model

Fine-tuned from [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M)
on the 8,040-pair Chokri corpus.

Hosted on HuggingFace Hub: `knbliss/chokri-nllb-finetuned`

> **Current limitation — English → Chokri:**
> Because Chokri is not in NLLB's language list, we use an existing language token as a stand-in
> for Chokri during training. The base model's strong prior association with that token's original
> language currently overrides the fine-tuning in the English → Chokri direction, causing it to
> produce the wrong output language. The Chokri → English direction is available in the current
> version. We are working on a solution for a future release.

---

## Repository structure

```
├── 2_clean_split.py            ← clean + train/val/test split
├── 3_finetune.py               ← fine-tune NLLB-200
├── 4_evaluate.py               ← BLEU score evaluation
├── 5_app.py                    ← Gradio web app (deploy to HF Spaces as app.py)
├── requirements.txt
├── collaboration/
│   ├── 1_SHEET_SETUP_GUIDE.md  ← set up the community review Google Sheet
│   ├── 2_CONTRIBUTOR_INVITE.md ← email template for recruiting reviewers
│   ├── 3_ORTHOGRAPHY_GUIDE.md  ← Chokri spelling and orthography reference
│   └── merge_verified_pairs.py ← merge reviewer-approved pairs into corpus
```

---

## How to contribute

There are two ways to help:

### As a Chokri speaker (no technical skills needed)

There are two ways to submit a sentence pair:

**Option 1 — Google Form** (easiest, no account needed):
Fill in the [Contributor Form](https://forms.gle/rqhZSiRm2VTY23t49). Submissions sync automatically into the review queue every hour.

**Option 2 — Translator app** (directly in the tool):
Use the **Add New Pair** tab or the **Correct a Translation** tab at the [live demo](https://huggingface.co/spaces/knbliss/chokri-english-translator).

All submissions go through an appointed reviewer before entering the training corpus.

### As a technical contributor
1. Fork this repo
2. Improve the training pipeline, the app, or the data cleaning scripts
3. Open a pull request

---

## Running locally

```bash
git clone https://github.com/knbliss/chokri-english-translator
cd chokri-english-translator
pip install -r requirements.txt
python 5_app.py
# → open http://localhost:7860
```

The app falls back to `facebook/nllb-200-distilled-600M` if `model_best/` is not present,
so you can run it without the fine-tuned weights.

---

## Contributors

| Role | Names |
|------|-------|
| Project lead | Kuyi |
| Reviewers | _to be added_ |
| Data sources | Chokri New Testament (Bible Society of India), Bielenberg (2001) |

Community contributors are listed in the release notes for each dataset version.

---

## License

- **Code**: MIT
- **Model weights**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

## Citation

```bibtex
@misc{chokri-translator-2025,
  title  = {Chokri--English Neural Machine Translation},
  author = {Kuyi},
  year   = {2025},
  url    = {https://github.com/knbliss/chokri-english-translator}
}
```
