# Chokri Flashcards

A simple React Native (Expo) flashcard app for beginners learning Chokri ↔
English, built from the project's verified sentence-pair dataset.

## Data

Cards are generated from `../data/chokri_english_MASTER.csv` by
`scripts/build_deck.py`, which curates a small beginner-friendly deck
instead of bundling the full ~8.5k-verse Bible corpus, split into the two
types the app lets the learner pick between:

- **Single Word Meanings** (~190 cards) — one Chokri word and its English
  meaning, pulled from the project's non-Bible sources (a Chokri textbook
  extract and languageshome.com).
- **Sentence Flashcards** (~365 cards) — full everyday sentences, combining
  non-Bible multi-word phrases (greetings, family, food, numbers,
  days/months, simple questions) with a curated supplement of short,
  concrete narrative lines from the Bible translation (e.g. "He entered
  and was passing through Oakridge"), filtered to exclude doctrinal
  vocabulary, genealogies, and sentence fragments. Grammar-terminology
  entries that leaked in from the textbook (e.g. "Transitive Verb") are
  filtered out of both decks.

Biblical person and place names in the Bible-derived sentences (Jesus,
Jerusalem, Pilate, etc.) are swapped for generic English names/places via
`scripts/anonymize_names.py`, applied identically to both the Chokri and
English text, so they read like ordinary daily sentences rather than
recognizably-Bible verses, and so the Chokri and English sides stay
consistent with each other.

Requires `pip install wordfreq` (used to score how common an English word
is, to drop obscure/jargon entries). Regenerate after the master CSV
changes:

```bash
python3 scripts/build_deck.py
```

## Running the app

```bash
npm install
npm run web      # quickest way to try it in a browser
npm run ios      # requires Xcode / iOS Simulator
npm run android  # requires Android Studio / emulator
```

Or scan the QR code from `npm start` with the Expo Go app on a phone.

## Features

- Choose "Sentence Flashcards" or "Single Word Meanings" from the home screen
- Tap a card to flip between Chokri and English
- Swipe left/right (or use Prev/Next) to move through the deck
- Shuffle button for randomized review
- Toggle card direction (Chokri→English or English→Chokri)
- "Mark known" progress tracking, saved on-device (AsyncStorage)

## Notes

- This is a static, offline-first app — no backend required. To add new
  sentence pairs, review them into `chokri_english_MASTER.csv` as usual
  and re-run `build_deck.py` before shipping an update.
