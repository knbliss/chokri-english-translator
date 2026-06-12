"""
Step 3: Fine-tune NLLB-200 distilled 600M on the Chokri–English corpus.
Bidirectional: trains both Chokri→English AND English→Chokri simultaneously.

For each pair (chokri, english) in the corpus, two training examples are created:
  Forward : src_lang=zho_Hant (Chokri proxy), tgt_lang=eng_Latn
  Reverse : src_lang=eng_Latn,                tgt_lang=zho_Hant (Chokri proxy)

This teaches the model to both READ and WRITE Chokri text.
"""
import os, csv, random, math, time, argparse
os.environ.setdefault("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.0")

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, get_linear_schedule_with_warmup

# ── Config ───────────────────────────────────────────────────────────────────
CHECKPOINT    = "facebook/nllb-200-distilled-600M"
CHOKRI_TOKEN  = "zho_Hant"   # proxy token for Chokri
ENGLISH_TOKEN = "eng_Latn"

MAX_SRC_LEN  = 64
MAX_TGT_LEN  = 64
BATCH_SIZE   = 2
GRAD_ACCUM   = 16           # effective batch = 32
EPOCHS       = 8            # more epochs since we have 2× training signal
LR           = 3e-5
WARMUP_STEPS = 300
SAVE_STEPS   = 500

TRAIN_CSV = "data/train.csv"
VAL_CSV   = "data/val.csv"
CKPT_DIR  = "checkpoints"
BEST_DIR  = "model_best"

# ── Device ───────────────────────────────────────────────────────────────────
def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda"), True
    if torch.backends.mps.is_available():
        return torch.device("mps"), False
    return torch.device("cpu"), False

# ── Dataset ──────────────────────────────────────────────────────────────────
def load_pairs(csv_path):
    """Load pairs and return both forward and reverse directions."""
    forward, reverse = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            chokri  = row["chokri"].strip()
            english = row["english"].strip()
            if chokri and english:
                forward.append((CHOKRI_TOKEN,  chokri,  ENGLISH_TOKEN, english))
                reverse.append((ENGLISH_TOKEN, english, CHOKRI_TOKEN,  chokri))
    # Interleave forward and reverse so each batch sees both directions
    combined = []
    for f, r in zip(forward, reverse):
        combined.append(f)
        combined.append(r)
    return combined


class BilingualDataset(Dataset):
    def __init__(self, examples):
        self.examples = examples   # (src_lang, src_text, tgt_lang, tgt_text)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


def collate_fn(batch, tokenizer):
    src_langs, srcs, tgt_langs, tgts = zip(*batch)

    # Each item in the batch may have a different src/tgt lang.
    # Tokenize one at a time to handle mixed directions.
    all_input_ids, all_attention, all_labels = [], [], []
    pad_id = tokenizer.pad_token_id

    for src_lang, src, tgt_lang, tgt in zip(src_langs, srcs, tgt_langs, tgts):
        tokenizer.src_lang = src_lang
        enc = tokenizer(src, max_length=MAX_SRC_LEN, truncation=True, return_tensors="pt")
        all_input_ids.append(enc["input_ids"][0])
        all_attention.append(enc["attention_mask"][0])

        tokenizer.src_lang = tgt_lang
        lab = tokenizer(tgt, max_length=MAX_TGT_LEN, truncation=True, return_tensors="pt")
        label_ids = lab["input_ids"][0].clone()
        label_ids[label_ids == pad_id] = -100
        all_labels.append(label_ids)

    # Pad to longest in batch
    def pad_seq(seqs, pad_val):
        max_len = max(s.size(0) for s in seqs)
        return torch.stack([
            torch.cat([s, torch.full((max_len - s.size(0),), pad_val, dtype=s.dtype)])
            for s in seqs
        ])

    return {
        "input_ids":      pad_seq(all_input_ids, pad_id),
        "attention_mask": pad_seq(all_attention, 0),
        "labels":         pad_seq(all_labels, -100),
    }

# ── Evaluation ───────────────────────────────────────────────────────────────
def evaluate(model, loader, device):
    model.eval()
    total_loss, n = 0.0, 0
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            total_loss += model(**batch).loss.item()
            n += 1
    return total_loss / max(n, 1)

# ── Training ─────────────────────────────────────────────────────────────────
def train(args):
    device, use_fp16 = get_device()
    print(f"Device: {device}  fp16: {use_fp16}")

    print("Loading tokenizer and model …")
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model     = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT)
    model.gradient_checkpointing_enable()
    model.to(device)

    train_examples = load_pairs(TRAIN_CSV)
    val_examples   = load_pairs(VAL_CSV)
    print(f"Train examples: {len(train_examples)} ({len(train_examples)//2} pairs × 2 directions)")
    print(f"Val examples:   {len(val_examples)}")

    collate = lambda b: collate_fn(b, tokenizer)

    train_loader = DataLoader(
        BilingualDataset(train_examples),
        batch_size=BATCH_SIZE, shuffle=True,
        collate_fn=collate, num_workers=0,
    )
    val_loader = DataLoader(
        BilingualDataset(val_examples),
        batch_size=BATCH_SIZE, shuffle=False,
        collate_fn=collate, num_workers=0,
    )

    total_steps = math.ceil(len(train_loader) / GRAD_ACCUM) * EPOCHS
    optimizer   = torch.optim.AdamW(model.parameters(), lr=LR)
    scheduler   = get_linear_schedule_with_warmup(optimizer, WARMUP_STEPS, total_steps)
    scaler      = torch.cuda.amp.GradScaler() if use_fp16 else None

    os.makedirs(CKPT_DIR, exist_ok=True)
    best_val_loss = float("inf")
    global_step   = 0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        epoch_loss, n_batches = 0.0, 0
        optimizer.zero_grad()
        t0 = time.time()

        for step, batch in enumerate(train_loader, 1):
            batch = {k: v.to(device) for k, v in batch.items()}

            if use_fp16:
                with torch.cuda.amp.autocast():
                    loss = model(**batch).loss / GRAD_ACCUM
                scaler.scale(loss).backward()
            else:
                loss = model(**batch).loss / GRAD_ACCUM
                loss.backward()

            epoch_loss += loss.item() * GRAD_ACCUM
            n_batches  += 1

            if step % GRAD_ACCUM == 0:
                if use_fp16:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                global_step += 1

                if global_step % SAVE_STEPS == 0:
                    ckpt_path = f"{CKPT_DIR}/step_{global_step}"
                    model.save_pretrained(ckpt_path)
                    tokenizer.save_pretrained(ckpt_path)
                    print(f"  Checkpoint → {ckpt_path}")

        val_loss  = evaluate(model, val_loader, device)
        avg_train = epoch_loss / max(n_batches, 1)
        print(
            f"Epoch {epoch}/{EPOCHS}  "
            f"train={avg_train:.4f}  val={val_loss:.4f}  "
            f"time={time.time()-t0:.0f}s"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            model.save_pretrained(BEST_DIR)
            tokenizer.save_pretrained(BEST_DIR)
            print(f"  ✓ Best model saved (val_loss={best_val_loss:.4f})")

    print(f"\nTraining complete. Best val loss: {best_val_loss:.4f}")
    print(f"Best model saved to: {BEST_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",     type=int,   default=EPOCHS)
    parser.add_argument("--batch_size", type=int,   default=BATCH_SIZE)
    parser.add_argument("--lr",         type=float, default=LR)
    args = parser.parse_args()
    EPOCHS     = args.epochs
    BATCH_SIZE = args.batch_size
    LR         = args.lr
    train(args)
