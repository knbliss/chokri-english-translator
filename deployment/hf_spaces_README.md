---
title: Chokri English Translator
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.0"
app_file: app.py
pinned: true
license: cc-by-4.0
---

# Chokri ↔ English Translator

The first machine-learning translation tool for **Chokri** (a Tibeto-Burman language
spoken in Nagaland, northeast India), built on a fine-tuned
[NLLB-200](https://huggingface.co/facebook/nllb-200-distilled-600M) model.

Trained on **8,245 sentence pairs** from the Bible (Nagamese script) and a
linguistics reference corpus. Community contributions are continuously reviewed
and merged to improve accuracy.

---

## How to use

| Tab | What it does |
|-----|-------------|
| **Translate** | Enter Chokri or English text and get a translation |
| **Correct a Translation** | Fix a wrong model output — your correction goes to reviewers |
| **Add New Pair** | Contribute a Chokri–English sentence pair you know |
| **Contributions** | See all community submissions and their review status |
| **Review** | *(Reviewers only)* Approve or reject pending submissions |

---

## About the language

Chokri is spoken by approximately 50,000 people in Phek district, Nagaland.
It belongs to the Tibeto-Burman family and has limited digital resources.
This project aims to change that.

## Contributing

If you speak Chokri, you can help by:
- Using the **Correct a Translation** tab when the model makes a mistake
- Using the **Add New Pair** tab to contribute sentences from everyday life,
  proverbs, or stories

Contributions are reviewed by appointed community reviewers before entering the
training corpus.

## Dataset

- v1.0 — 8,245 pairs (Bible + linguistics paper)
- v1.1+ — community contributions (in progress)

## Citation

If you use this tool in research, please cite:
```
@misc{chokri-translator-2025,
  title  = {Chokri–English Neural Machine Translation},
  year   = {2025},
  url    = {https://huggingface.co/spaces/YOUR_HF_USERNAME/chokri-english-translator}
}
```
