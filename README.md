# Chokri–English Neural Machine Translation

The first open-source machine translation system for **Chokri**, a Tibeto-Burman
language spoken by ~50,000 people in Phek district, Nagaland, northeast India.

**Live demo:** [huggingface.co/spaces/knbliss/chokri-english-translator](https://huggingface.co/spaces/knbliss/chokri-english-translator)

> **Note:** The model is currently being retrained. Additionally, the training data is not yet based on the officially accepted Chokri standard — translations may reflect regional dialect variations. We are committed to adopting the official CCLB dataset when available.

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

> **Note on dataset quality:** The Bible translation currently used as training data is not the version accepted by the **Chokri Chakhesang Literary Board (CCLB)** — the official body for Chokri language and literature. The current version contains accents and dialect features specific to a particular region of the Chokri-speaking population, which means translations may not reflect standard Chokri. The CCLB is working on an official dictionary and an accepted Bible translation. This project intends to adopt that official dataset when it becomes available, at which point translation quality will improve significantly.

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
- **Submit a sentence pair** via the [Contributor Form](https://forms.gle/rqhZSiRm2VTY23t49) — no account needed
- **Correct** a wrong translation using the live app above
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
