"""
Chokri ↔ English Translation Interface
Phase 2: Supabase backend + reviewer mode

Environment variables:
  SUPABASE_URL        — Supabase project URL (falls back to local CSV if unset)
  SUPABASE_KEY        — Supabase service-role key
  REVIEWER_PASSWORD   — password for the reviewer tab (default: change-me)
  HF_MODEL_ID         — HuggingFace model repo (e.g. yourname/chokri-nllb)
                        used on Spaces; local model_best/ takes priority if present

Run locally: python 5_app.py  →  http://localhost:7860
"""
import csv
import os
from datetime import datetime, timezone

import gradio as gr
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ── Config ─────────────────────────────────────────────────────────────────
CHOKRI_TOKEN      = "lus_Latn"
ENGLISH_TOKEN     = "eng_Latn"
MAX_LEN           = 128
MASTER_CSV        = "chokri_english_MASTER.csv"
CONTRIB_CSV       = "user_contributions.csv"
REVIEWER_PASSWORD = os.getenv("REVIEWER_PASSWORD", "change-me")

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "knbliss/chokri-nllb-finetuned")
MODEL_PATH  = (
    "model_best"
    if os.path.isdir("model_best")
    else (HF_MODEL_ID or "facebook/nllb-200-distilled-600M")
)

# ── Supabase (optional — falls back to CSV if env vars not set) ─────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
sb = None

if USE_SUPABASE:
    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase.")
    except ImportError:
        USE_SUPABASE = False
        print("supabase package not found — using CSV fallback.")

# ── Load model ─────────────────────────────────────────────────────────────
print(f"Loading model from: {MODEL_PATH}")
device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)
model.eval()
print(f"Model ready on {device}.")

# ── CSV fallback: ensure file + header exist ───────────────────────────────
CSV_FIELDS = ["id", "chokri", "english", "type", "note",
              "submitted_at", "status", "reviewed_by", "reviewer_notes", "reviewed_at"]

if not USE_SUPABASE and not os.path.exists(CONTRIB_CSV):
    with open(CONTRIB_CSV, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

# ── Translation ────────────────────────────────────────────────────────────
def _translate(text: str, src_token: str, tgt_token: str, beams: int) -> str:
    text = text.strip()
    if not text:
        return ""
    tokenizer.src_lang = src_token
    tgt_id = tokenizer.convert_tokens_to_ids(tgt_token)
    inputs = tokenizer(text, truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            forced_bos_token_id=tgt_id,
            max_new_tokens=MAX_LEN,
            num_beams=beams,
            no_repeat_ngram_size=3,   # block repeated 3-grams (stops tɛ̄-tɛ̄-tɛ̄ loops)
            repetition_penalty=1.5,   # discourage repeating tokens
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)

def chokri_to_english(text, beams):
    return _translate(text, CHOKRI_TOKEN, ENGLISH_TOKEN, int(beams))

def english_to_chokri(text, beams):
    return _translate(text, ENGLISH_TOKEN, CHOKRI_TOKEN, int(beams))

# ── Contribution helpers ───────────────────────────────────────────────────
def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def _csv_all_rows():
    if not os.path.exists(CONTRIB_CSV):
        return []
    with open(CONTRIB_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _csv_write_rows(rows):
    with open(CONTRIB_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)

def save_contribution(chokri: str, english: str, kind: str, note: str) -> str:
    chokri  = chokri.strip()
    english = english.strip()
    if not chokri or not english:
        return "Both Chokri and English fields are required."
    if USE_SUPABASE:
        sb.table("contributions").insert({
            "chokri": chokri, "english": english,
            "type": kind, "note": note.strip(), "status": "pending",
        }).execute()
        count = sb.table("contributions").select("id", count="exact").execute().count
        return f"Saved! Total contributions: {count}"
    else:
        rows = _csv_all_rows()
        new_id = f"C-{len(rows)+1:04d}"
        rows.append({
            "id": new_id, "chokri": chokri, "english": english,
            "type": kind, "note": note.strip(),
            "submitted_at": _now_iso(), "status": "pending",
            "reviewed_by": "", "reviewer_notes": "", "reviewed_at": "",
        })
        _csv_write_rows(rows)
        return f"Saved! Total contributions: {len(rows)}"

def submit_correction(src, mt, corrected, direction, note):
    if direction == "Chokri → English":
        chokri, english = src.strip(), corrected.strip()
    else:
        english, chokri = src.strip(), corrected.strip()
    return save_contribution(chokri, english, "correction", note)

def submit_new_pair(chokri, english, note):
    return save_contribution(chokri, english, "new_pair", note)

# ── Stats & table ──────────────────────────────────────────────────────────
def get_stats() -> str:
    if USE_SUPABASE:
        def count(status):
            return sb.table("contributions").select("id", count="exact").eq("status", status).execute().count
        p, v, r = count("pending"), count("verified"), count("rejected")
    else:
        rows = _csv_all_rows()
        p = sum(1 for r in rows if r.get("status") == "pending")
        v = sum(1 for r in rows if r.get("status") == "verified")
        r = sum(1 for r in rows if r.get("status") == "rejected")
    return f"Pending: {p}  |  Verified: {v}  |  Rejected: {r}"

def load_recent():
    if USE_SUPABASE:
        res = sb.table("contributions").select("*").order("submitted_at", desc=True).limit(50).execute()
        return [[r["chokri"], r["english"], r["type"], r.get("note",""),
                 r.get("submitted_at",""), r["status"]] for r in res.data]
    else:
        rows = _csv_all_rows()
        return [[r["chokri"], r["english"], r["type"], r.get("note",""),
                 r.get("submitted_at",""), r.get("status","pending")] for r in reversed(rows[-50:])]

# ── Reviewer helpers ───────────────────────────────────────────────────────
def _next_pending():
    if USE_SUPABASE:
        res = sb.table("contributions").select("*").eq("status", "pending").order("submitted_at").limit(1).execute()
        return res.data[0] if res.data else None
    else:
        for row in _csv_all_rows():
            if row.get("status", "pending") == "pending":
                return row
        return None

def _item_to_outputs(item):
    """Convert a contribution dict to the 6 reviewer-panel output values."""
    if item is None:
        return (
            gr.update(value="", interactive=False),
            gr.update(value="", interactive=False),
            "",
            "",
            "No pending items.",
            "",
        )
    return (
        gr.update(value=item["chokri"], interactive=True),
        gr.update(value=item["english"], interactive=True),
        item.get("type", ""),
        item.get("note", ""),
        f"Reviewing ID: {item.get('id', item.get('submitted_at', '?'))}",
        item.get("id", item.get("submitted_at", "")),
    )

def load_review_item():
    return _item_to_outputs(_next_pending())

def _set_status(item_id, new_status, reviewer_name, reviewer_notes,
                new_chokri=None, new_english=None):
    if USE_SUPABASE:
        update = {
            "status": new_status,
            "reviewed_by": reviewer_name,
            "reviewer_notes": reviewer_notes,
            "reviewed_at": _now_iso(),
        }
        if new_chokri:
            update["chokri"] = new_chokri
        if new_english:
            update["english"] = new_english
        sb.table("contributions").update(update).eq("id", item_id).execute()
    else:
        rows = _csv_all_rows()
        for row in rows:
            if row.get("id") == item_id or row.get("submitted_at") == item_id:
                row["status"]         = new_status
                row["reviewed_by"]    = reviewer_name
                row["reviewer_notes"] = reviewer_notes
                row["reviewed_at"]    = _now_iso()
                if new_chokri:
                    row["chokri"] = new_chokri
                if new_english:
                    row["english"] = new_english
                break
        _csv_write_rows(rows)

def approve_item(item_id, chokri, english, reviewer_name, reviewer_notes):
    if not item_id:
        return ("No item loaded.",) + _item_to_outputs(None)
    _set_status(item_id, "verified", reviewer_name, reviewer_notes, chokri, english)
    msg = f"Approved! {get_stats()}"
    return (msg,) + _item_to_outputs(_next_pending())

def reject_item(item_id, reviewer_name, reviewer_notes):
    if not item_id:
        return ("No item loaded.",) + _item_to_outputs(None)
    _set_status(item_id, "rejected", reviewer_name, reviewer_notes)
    msg = f"Rejected. {get_stats()}"
    return (msg,) + _item_to_outputs(_next_pending())

def download_verified():
    if USE_SUPABASE:
        res = sb.table("contributions").select(
            "chokri,english,type,reviewer_notes"
        ).eq("status", "verified").execute()
        rows = res.data
    else:
        rows = [r for r in _csv_all_rows() if r.get("status") == "verified"]
    if not rows:
        return None
    path = "/tmp/chokri_verified_pairs.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["chokri", "english", "type", "reviewer_notes"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return path

# ── UI ─────────────────────────────────────────────────────────────────────
_backend = "Supabase" if USE_SUPABASE else "Local CSV"

with gr.Blocks(title="Chokri ↔ English Translator", theme=gr.themes.Soft()) as demo:

    gr.Markdown("# Chokri ↔ English Translator")
    gr.Markdown(
        f"Model: `{MODEL_PATH}` &nbsp;|&nbsp; Device: `{device}` &nbsp;|&nbsp; "
        f"Backend: `{_backend}`"
    )
    gr.Markdown(
        "> ⚠️ **Early-stage prototype.** Translations are based on an unofficial dialect "
        "version of Chokri and should **not** be used as a reference for correct Chokri "
        "spelling, grammar, or translation. We are working with the "
        "**Chokri Chakhesang Literary Board (CCLB)** to adopt the officially accepted "
        "Chokri standard in a future version."
    )

    # ── Tab 1: Translate ───────────────────────────────────────────────────
    with gr.Tab("Translate"):
        gr.Markdown(
            "_English → Chokri translation is coming in a future version. "
            "Currently supported: Chokri → English._"
        )
        with gr.Row():
            beams = gr.Slider(1, 8, value=4, step=1,
                              label="Beam width (higher = more accurate, slower)")
        with gr.Row():
            with gr.Column():
                src_box = gr.Textbox(label="Chokri (source)",
                                     placeholder="Enter Chokri text here…", lines=5)
                translate_btn = gr.Button("Translate → English", variant="primary")
            with gr.Column():
                tgt_box = gr.Textbox(label="English (translation)", lines=5,
                                     interactive=False)

        translate_btn.click(fn=lambda text, b: chokri_to_english(text, b),
                            inputs=[src_box, beams], outputs=tgt_box)
        src_box.submit(fn=lambda text, b: chokri_to_english(text, b),
                       inputs=[src_box, beams], outputs=tgt_box)

        gr.Examples(
            label="Example sentences",
            examples=[
                ["Abraham nu David, David nuo Jisu Khrista shühye lüsida;", 4],
                ["í lɘ̄vā tì-vá", 4],
                ["ʧɛ̄kʰa̋ kʰa̋-tɛ̄", 4],
            ],
            inputs=[src_box, beams],
        )

    # ── Tab 2: Correct a translation ──────────────────────────────────────
    with gr.Tab("Correct a Translation"):
        gr.Markdown(
            "If the model produced a wrong translation, paste it here and provide the "
            "correct version. Corrections go to reviewers before entering the training set."
        )
        with gr.Row():
            with gr.Column():
                corr_src = gr.Textbox(label="Original Chokri text", lines=3)
                corr_mt  = gr.Textbox(label="Model's translation (wrong)", lines=3)
            with gr.Column():
                corr_fix  = gr.Textbox(label="Your corrected translation", lines=3)
                corr_note = gr.Textbox(label="Optional note (e.g. 'wrong tense')", lines=1)
        with gr.Row():
            corr_dir = gr.Radio(
                ["Chokri → English", "English → Chokri"],
                value="Chokri → English", label="Direction",
            )
        corr_btn    = gr.Button("Submit Correction", variant="primary")
        corr_status = gr.Textbox(label="Status", interactive=False)
        corr_btn.click(
            fn=submit_correction,
            inputs=[corr_src, corr_mt, corr_fix, corr_dir, corr_note],
            outputs=corr_status,
        )

    # ── Tab 3: Add new pair ────────────────────────────────────────────────
    with gr.Tab("Add New Pair"):
        gr.Markdown(
            "Know a Chokri sentence and its English translation? Add it here — "
            "a reviewer will verify it before it enters the training corpus."
        )
        with gr.Row():
            with gr.Column():
                new_chokri  = gr.Textbox(label="Chokri sentence", lines=3)
            with gr.Column():
                new_english = gr.Textbox(label="English translation", lines=3)
        new_note   = gr.Textbox(label="Optional note (source, context, dialect…)", lines=1)
        add_btn    = gr.Button("Add Pair", variant="primary")
        add_status = gr.Textbox(label="Status", interactive=False)
        add_btn.click(fn=submit_new_pair,
                      inputs=[new_chokri, new_english, new_note], outputs=add_status)

    # ── Tab 4: Contributions ──────────────────────────────────────────────
    with gr.Tab("Contributions"):
        stats_box   = gr.Textbox(label="Contribution stats", interactive=False)
        refresh_btn = gr.Button("Refresh")
        contrib_tbl = gr.Dataframe(
            headers=["Chokri", "English", "Type", "Note", "Submitted", "Status"],
            datatype=["str"] * 6, interactive=False, wrap=True,
        )

        def _refresh():
            return get_stats(), load_recent()

        refresh_btn.click(fn=_refresh, outputs=[stats_box, contrib_tbl])
        demo.load(fn=_refresh, outputs=[stats_box, contrib_tbl])

    # ── Tab 5: Review (password-gated) ────────────────────────────────────
    with gr.Tab("Review"):
        _logged_in  = gr.State(False)
        _current_id = gr.Textbox(visible=False)   # holds UUID / timestamp of current item

        # — Login panel —
        with gr.Column(visible=True) as login_col:
            gr.Markdown("### Reviewer Login")
            gr.Markdown("This tab is for appointed reviewers only.")
            pwd_input = gr.Textbox(label="Password", type="password", lines=1)
            login_btn = gr.Button("Login")
            login_msg = gr.Textbox(label="", interactive=False)

        # — Review panel (hidden until logged in) —
        with gr.Column(visible=False) as review_col:
            gr.Markdown("### Review Pending Contributions")
            gr.Markdown(
                "Edit Chokri/English if needed, add your name and any notes, "
                "then **Approve** or **Reject**. The next pending item loads automatically."
            )
            review_status = gr.Textbox(label="Current item", interactive=False)
            load_btn      = gr.Button("Load next pending item")

            with gr.Row():
                with gr.Column():
                    rev_chokri  = gr.Textbox(label="Chokri", lines=3)
                with gr.Column():
                    rev_english = gr.Textbox(label="English", lines=3)
            with gr.Row():
                rev_type = gr.Textbox(label="Type", interactive=False)
                rev_note = gr.Textbox(label="Submitter note", interactive=False)

            reviewer_name  = gr.Textbox(label="Your name", lines=1)
            reviewer_notes = gr.Textbox(label="Reviewer notes (optional)", lines=1)

            with gr.Row():
                approve_btn = gr.Button("Approve", variant="primary")
                reject_btn  = gr.Button("Reject",  variant="stop")

            action_msg = gr.Textbox(label="Result", interactive=False)

            gr.Markdown("---")
            gr.Markdown("**Download verified pairs** as CSV for local retraining:")
            download_btn  = gr.Button("Download verified pairs")
            verified_file = gr.File(label="Download", interactive=False)
            download_btn.click(fn=download_verified, outputs=verified_file)

        # — Wiring —
        _REVIEW_OUTPUTS = [rev_chokri, rev_english, rev_type, rev_note,
                           review_status, _current_id]

        def _do_login(password, state):
            if password == REVIEWER_PASSWORD:
                return True, gr.update(visible=False), gr.update(visible=True), "Logged in."
            return False, gr.update(visible=True), gr.update(visible=False), "Incorrect password."

        login_btn.click(
            fn=_do_login,
            inputs=[pwd_input, _logged_in],
            outputs=[_logged_in, login_col, review_col, login_msg],
        )

        load_btn.click(fn=load_review_item, outputs=_REVIEW_OUTPUTS)

        approve_btn.click(
            fn=approve_item,
            inputs=[_current_id, rev_chokri, rev_english, reviewer_name, reviewer_notes],
            outputs=[action_msg] + _REVIEW_OUTPUTS,
        )

        reject_btn.click(
            fn=reject_item,
            inputs=[_current_id, reviewer_name, reviewer_notes],
            outputs=[action_msg] + _REVIEW_OUTPUTS,
        )

demo.launch()
