"""
Step 4: Evaluate the fine-tuned model on the test set using BLEU score.
Compares fine-tuned model vs. the base NLLB-200 (no fine-tuning).
"""
import csv, torch, sacrebleu
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

SRC_LANG  = "zho_Hant"
TGT_LANG  = "eng_Latn"
TEST_CSV  = "data/test.csv"
BEST_DIR  = "model_best"
BASE_CKPT = "facebook/nllb-200-distilled-600M"
BATCH_SIZE = 16
MAX_SRC_LEN = 128
MAX_NEW_TOKENS = 128


def load_test(csv_path):
    srcs, refs = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            srcs.append(row["chokri"].strip())
            refs.append(row["english"].strip())
    return srcs, refs


def translate_batch(model, tokenizer, texts, device):
    tokenizer.src_lang = SRC_LANG
    tgt_id = tokenizer.convert_tokens_to_ids(TGT_LANG)
    inputs = tokenizer(
        texts,
        max_length=MAX_SRC_LEN,
        truncation=True,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            forced_bos_token_id=tgt_id,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=4,
        )
    return tokenizer.batch_decode(out, skip_special_tokens=True)


def evaluate_model(name, model_path, srcs, refs, device):
    print(f"\nLoading {name} …")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)
    model.eval()

    hypotheses = []
    for i in range(0, len(srcs), BATCH_SIZE):
        batch = srcs[i : i + BATCH_SIZE]
        hyps  = translate_batch(model, tokenizer, batch, device)
        hypotheses.extend(hyps)
        if (i // BATCH_SIZE + 1) % 5 == 0:
            print(f"  {i + len(batch)}/{len(srcs)} translated …")

    bleu = sacrebleu.corpus_bleu(hypotheses, [refs])
    print(f"\n{name} BLEU: {bleu.score:.2f}")

    # Print a few examples
    print("\nSample translations:")
    for j in range(min(5, len(srcs))):
        print(f"  Chokri : {srcs[j]}")
        print(f"  Reference: {refs[j]}")
        print(f"  Hypothesis: {hypotheses[j]}")
        print()

    return bleu.score, hypotheses


if __name__ == "__main__":
    import os
    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Device: {device}")

    srcs, refs = load_test(TEST_CSV)
    print(f"Test set size: {len(srcs)}")

    results = {}

    # Fine-tuned model
    if os.path.isdir(BEST_DIR):
        score, hyps = evaluate_model("Fine-tuned NLLB-200", BEST_DIR, srcs, refs, device)
        results["finetuned"] = score
        # Save outputs
        with open("eval_outputs.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["chokri", "reference", "hypothesis"])
            for s, r, h in zip(srcs, refs, hyps):
                w.writerow([s, r, h])
        print("Detailed outputs saved to eval_outputs.csv")
    else:
        print(f"No fine-tuned model found at {BEST_DIR}/ — skipping.")

    # Base model (for comparison)
    print("\nEvaluating base model for comparison …")
    base_score, _ = evaluate_model("Base NLLB-200 (no fine-tuning)", BASE_CKPT, srcs, refs, device)
    results["base"] = base_score

    print("\n── Summary ─────────────────────────────")
    for k, v in results.items():
        print(f"  {k:20s}: BLEU {v:.2f}")
