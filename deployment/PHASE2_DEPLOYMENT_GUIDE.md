# Phase 2 Deployment Guide

Three steps: set up Supabase → upload the model to HuggingFace Hub → create the HF Space.

---

## Step 1 — Supabase (database for contributions)

### 1a. Create a project
1. Go to [supabase.com](https://supabase.com) → **Start your project** → **New project**
2. Give it a name: **chokri-translator**
3. Set a database password (save it somewhere safe — you won't need it directly)
4. Choose a region close to you → **Create new project** (takes ~2 min)

### 1b. Create the contributions table
1. In your project dashboard → **SQL Editor** → **New query**
2. Paste the contents of `supabase_setup.sql` (in the root of this project)
3. Click **Run**
4. You should see "Success. No rows returned."

### 1c. Get your keys

**Project URL:**
1. Go to **Project Settings** (gear icon) → **General**
2. Copy the **Reference ID** line — your URL is `https://<reference-id>.supabase.co`

**Secret key (for `SUPABASE_KEY`):**
1. Go to **Project Settings** → **API Keys**
2. You will see two tabs: *"Publishable and secret API keys"* (new UI) and *"Legacy anon, service_role API keys"*
3. On the **Publishable and secret API keys** tab, scroll to **Secret keys**
4. Copy the key starting with `sb_secret_…`

> Use the **secret key** (`sb_secret_…`) for `SUPABASE_KEY` — not the publishable key.
> The secret key allows reviewer approve/reject (UPDATE) actions.
> The publishable key only allows INSERT (submissions), which is not enough for the reviewer tab.

---

## Step 2 — Upload model to HuggingFace Hub

The fine-tuned model lives in `model_best/`. Upload it once so your HF Space can load it.

### 2a. Install the HF CLI (if not already installed)
```bash
pip install huggingface_hub
huggingface-cli login   # paste your HF token when prompted
```

### 2b. Create a model repository
1. Go to [huggingface.co](https://huggingface.co) → your profile → **New Model**
2. Name it: **chokri-nllb-finetuned**
3. Set visibility to **Public** (so the Space can load it freely)
4. Click **Create model**

### 2c. Upload the model files
```bash
cd /path/to/your/project

python - <<'EOF'
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path="model_best",
    repo_id="YOUR_HF_USERNAME/chokri-nllb-finetuned",
    repo_type="model",
)
print("Upload complete.")
EOF
```

Replace `YOUR_HF_USERNAME` with your actual HF username.

> The upload takes a few minutes (model is ~1.2 GB). Once done, confirm you can see the
> files at `huggingface.co/YOUR_HF_USERNAME/chokri-nllb-finetuned`.

---

## Step 3 — Create the HuggingFace Space

### 3a. Create the Space
1. Go to [huggingface.co](https://huggingface.co) → **New Space**
2. Name: **chokri-english-translator**
3. SDK: **Gradio**
4. Visibility: **Public**
5. Click **Create Space**

### 3b. Add the app files
In your Space repository, upload these files from this project:
- `5_app.py` → rename it to **`app.py`** in the Space
- `requirements.txt`
- `deployment/hf_spaces_README.md` → rename it to **`README.md`** in the Space

You can do this via the HF web UI (drag and drop) or via Git:
```bash
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/chokri-english-translator
cd chokri-english-translator
cp /path/to/project/5_app.py app.py
cp /path/to/project/requirements.txt .
cp /path/to/project/deployment/hf_spaces_README.md README.md
git add app.py requirements.txt README.md
git commit -m "Initial deployment"
git push
```

### 3c. Set environment variables (Secrets)
In your Space → **Settings** → **Variables and secrets** → **New secret**:

| Name | Value |
|------|-------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase **service_role** key |
| `REVIEWER_PASSWORD` | A strong password for your reviewers |
| `HF_MODEL_ID` | `YOUR_HF_USERNAME/chokri-nllb-finetuned` |

> Never put these in the code or commit them to git.

### 3d. Verify the Space builds
1. Go to your Space URL — the build log appears on the first run
2. Watch for "Model ready" and "Connected to Supabase" in the logs
3. Try a translation to confirm it works
4. Try the Review tab with your password

---

## After deployment

**Give reviewers the app URL** and the reviewer password. They use the **Review** tab to
approve or reject pending contributions.

**Download verified pairs for retraining:**
1. Log in to the Review tab
2. Click **Download verified pairs** — saves a CSV
3. Run locally: `python collaboration/merge_verified_pairs.py` (or use the merge script)
4. Re-run `2_clean_split.py` and `3_finetune.py` to train a new model version
5. Upload the new `model_best/` to HF Hub → Space reloads automatically
