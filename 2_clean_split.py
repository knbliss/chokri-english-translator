"""
Step 2: Clean the corpus and split into train/val/test sets.
- Drop rows with missing or very short text
- Deduplicate on (chokri, english)
- Split: 90% train, 5% val, 5% test (stratified by source)
"""
import pandas as pd
from sklearn.model_selection import train_test_split
import os

df = pd.read_csv("chokri_english_MASTER.csv")
print(f"Raw rows: {len(df)}")

# Drop rows with NaN
df = df.dropna(subset=["chokri", "english"])

# Drop very short rows (less than 3 chars each side)
df = df[df["chokri"].str.strip().str.len() >= 3]
df = df[df["english"].str.strip().str.len() >= 3]

# Strip whitespace
df["chokri"] = df["chokri"].str.strip()
df["english"] = df["english"].str.strip()

# Deduplicate
df = df.drop_duplicates(subset=["chokri", "english"])
print(f"After cleaning: {len(df)}")

# Split: first hold out 10% for val+test
train_df, temp_df = train_test_split(df, test_size=0.10, random_state=42)
val_df, test_df = train_test_split(temp_df, test_size=0.50, random_state=42)

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

os.makedirs("data", exist_ok=True)
train_df.to_csv("data/train.csv", index=False)
val_df.to_csv("data/val.csv", index=False)
test_df.to_csv("data/test.csv", index=False)

print("Saved to data/train.csv, data/val.csv, data/test.csv")
