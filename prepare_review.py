import pandas as pd

df = pd.read_csv("data/ai_policy_news.csv")

# Add columns for your manual review
df["review_decision"] = "Pending"
df["verified_source"] = ""


df.to_csv(
    "data/ai_policy_review.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Review file created!")
print("Records to review:", len(df))
print(df["state"].value_counts())