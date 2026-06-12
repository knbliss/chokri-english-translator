# Chokri Spelling Guide for Contributors

**Please read this before adding or reviewing sentence pairs.**

To build a translation tool that works well, every Chokri sentence in our
dataset must use **one consistent spelling system**. This short guide explains
which system we use and why.

---

## The rule: use the practical (Bible) romanization

We use the **everyday written form of Chokri** — the same spelling found in the
Chokri Bible and in school materials. This is the form most Chokri people
actually read and write.

✅ **Use letters like:** a, e, i, o, u, **ü**, **ö**, and ordinary consonants
(b, ch, d, h, k, l, m, n, p, r, s, t, v, y, z, etc.)

❌ **Do NOT use phonetic (IPA) symbols** such as: ɔ, ɛ, ə, ɘ, ŋ, ɲ, ʃ, ʒ, ʧ,
or tone marks above letters (◌̄ ◌́ ◌̌ ◌̀).

---

## Examples

| ✅ Correct (use this) | ❌ Avoid (IPA — do not use) |
|----------------------|----------------------------|
| `Vorichi` | `vɔ́rí-ʧì` |
| `chekha kha-te` | `ʧɛ̄kʰa̋ kʰa̋-tɛ̄` |
| `thüma kemezhe tüyo va` | `tʰə̄mà kə̄vɛ̋ tɘ́-lə̄ vɔ́-jɔ̄` |
| `Abraham nu David` | (already correct) |

> The IPA system (used in some linguistics papers) is precise for describing
> sounds, but it is **not** how Chokri is written in daily life. Mixing the two
> confuses the translation model, so we use only the practical spelling.

---

## Why this matters

When we tested the model, sentences written in the everyday spelling translated
well, but the same sentences written in IPA failed — the computer treated them
as if they were a different language. Keeping one consistent spelling makes the
tool dramatically more accurate.

---

## Quick checklist before submitting a pair

- [ ] Chokri sentence uses **everyday spelling** (ü, ö are fine; no ɔ, ɛ, ŋ, etc.)
- [ ] No tone marks floating above letters
- [ ] Spelling matches how you would write it in a letter or text message
- [ ] English translation is natural and complete
- [ ] If unsure about a spelling, add a note for the reviewer

---

## A note on dialect

Chokri has regional variations. If your sentence uses a specific village or
dialect form, that is welcome — just **mention the dialect in the notes column**
so reviewers know it is intentional and not a typo.

---

## For reviewers

When verifying a pair:
1. Check the Chokri uses practical romanization (reject/correct IPA)
2. Confirm the spelling is consistent with the Bible/school standard
3. Make sure the English meaning is accurate and natural
4. If a good sentence arrives in IPA, you may **transliterate it** into the
   practical spelling rather than rejecting it — good content is worth keeping.

> We have a separate file of ~205 useful sentences currently in IPA
> (`ipa_pairs_for_transliteration.csv`) that need converting to practical
> spelling. Reviewers who are comfortable with both systems can help convert
> these — they contain valuable everyday grammar (questions, commands, tenses)
> that our Bible-heavy dataset lacks.
