# Chokri–English Neural Machine Translation

The first open-source machine translation system for **Chokri**, a Tibeto-Burman
language spoken by ~50,000 people in Phek district, Nagaland, northeast India.

**Live demo:** [huggingface.co/spaces/knbliss/chokri-english-translator](https://huggingface.co/spaces/knbliss/chokri-english-translator)

---

## Why this matters

Chokri is not supported by any major translation platform (Google, Microsoft, DeepL)
and is absent from Meta's NLLB-200, despite it covering 200+ languages. This project
creates the first open-source translation tool for Chokri — and more importantly,
builds the community infrastructure to keep improving it.

---

## Dataset

| Version | Pairs | Sources |
|---------|-------|---------|
| v1.0 | 8,040 | Chokri New Testament (Bible Society of India), Bielenberg 2001 linguistics paper |
| v1.1 | _in progress_ | + community contributions (reviewed) |

The dataset is maintained privately to protect the integrity of community contributions
and ensure the Chokri-speaking community retains stewardship over their language data.
The trained model and tools are open-source; the underlying corpus is not publicly distributed.

---

## Model

Fine-tuned from [`facebook/nllb-200-distilled-600M`](https://huggingface.co/facebook/nllb-200-distilled-600M)
on the 8,040-pair Chokri corpus.

Hosted on HuggingFace Hub: `knbliss/chokri-nllb-finetuned`

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
