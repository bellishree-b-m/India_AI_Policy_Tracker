import pandas as pd

input_file = "data/ai_policy_review.csv"
output_file = "data/ai_policy_final.csv"

df = pd.read_csv(input_file)

# Standardise column names
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Check required review column
if "review_decision" not in df.columns:
    raise ValueError("Could not find review_decision column.")

# Find the verified-source column
possible_names = [
    "verified_source",
    "verification_source",
    "veification_source"
]

verified_col = next(
    (name for name in possible_names if name in df.columns),
    None
)

if verified_col is None:
    raise ValueError("Could not find the verified source column.")

# Keep only included records with a verified source
final_df = df[
    (df["review_decision"].astype(str).str.strip().str.lower() == "include") &
    (df[verified_col].astype(str).str.strip().str.lower() == "yes")
].copy()

final_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("Final dataset created!")
print("Included records:", len(final_df))
print("Saved to:", output_file)

if len(final_df) < 16:
    print("Note: Some included records have not been marked verified_source = Yes.")