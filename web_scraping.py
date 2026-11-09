
import feedparser
import pandas as pd
from urllib.parse import quote
from datetime import datetime
import os
import re
import hashlib

# --------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------

START_DATE = "2024-01-01"
END_DATE = "2026-11-10"

STATE_QUERIES = {
    "Karnataka": [
        '"Karnataka AI policy"',
        '"Karnataka artificial intelligence government"',
        '"Karnataka AI centre of excellence"',
        '"Karnataka AI mission partnership"'
    ],

    "Tamil Nadu": [
        '"Tamil Nadu Safe and Ethical AI Policy"',
        '"Tamil Nadu AI Mission"',
        '"Tamil Nadu artificial intelligence government"',
        '"Tamil Nadu AI centre of excellence"'
    ],

    "Maharashtra": [
        '"Maharashtra AI Policy"',
        '"MahaAgri AI Policy"',
        '"Maharashtra artificial intelligence government"',
        '"Maharashtra AI centre of excellence"'
    ]
}

CATEGORIES = {
    "AI Policy": [
        "ai policy", "artificial intelligence policy",
        "policy framework"
    ],
    "AI Mission": [
        "ai mission", "artificial intelligence mission"
    ],
    "Centre of Excellence": [
        "centre of excellence", "center of excellence"
    ],
    "Government Partnership / MoU": [
        "mou", "memorandum of understanding",
        "partnership", "collaboration"
    ],
    "AI Deployment": [
        "deployment", "implemented", "implementation",
        "launched", "public services"
    ],
    "AI Funding / Budget": [
        "funding", "budget", "investment",
        "crore", "allocation"
    ],
    "AI Ethics / Governance": [
        "ethical ai", "responsible ai",
        "ai governance", "ai ethics"
    ]
}


# --------------------------------
# 2. CLASSIFICATION
# --------------------------------

def classify_category(text):

    text = text.lower()

    for category, keywords in CATEGORIES.items():

        if any(keyword in text for keyword in keywords):
            return category

    return "Other AI Activity"


def classify_status(text):

    text = text.lower()

    if any(word in text for word in [
        "implemented", "operational", "deployed",
        "launched", "inaugurated"
    ]):
        return "Implemented / Launched"

    if any(word in text for word in [
        "proposed", "plans to", "proposes",
        "will establish", "planning"
    ]):
        return "Proposed"

    if any(word in text for word in [
        "announced", "approved", "signed",
        "notified", "adopted"
    ]):
        return "Announced / Approved"

    return "Needs verification"


# --------------------------------
# 3. COLLECT NEWS
# --------------------------------

def collect_news():

    records = []

    for state, queries in STATE_QUERIES.items():

        print(f"\nCollecting news for {state}...")

        for query in queries:

            search_query = (
                f'{query} after:{START_DATE} '
                f'before:{END_DATE}'
            )

            rss_url = (
                "https://news.google.com/rss/search?q="
                + quote(search_query)
                + "&hl=en-IN&gl=IN&ceid=IN:en"
            )

            feed = feedparser.parse(rss_url)

            for entry in feed.entries:

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                url = entry.get("link", "")

                combined_text = (
                    title + " " + summary
                )

                # Keep relevant AI-related results
                if not any(term in combined_text.lower()
                           for term in ["ai", "artificial intelligence"]):
                    continue

                if not url:
                    continue

                category = classify_category(combined_text)

                record_id = hashlib.sha256(
                    url.encode("utf-8")
                ).hexdigest()[:12]

                source = entry.get("source", {})
                source_name = (
                    source.get("title", "")
                    if hasattr(source, "get") else ""
                )

                records.append({

                    "record_id": record_id,
                    "state": state,
                    "date": entry.get("published", ""),
                    "title": title,
                    "category": category,
                    "status": classify_status(combined_text),
                    "description": re.sub(
                        r"<[^>]+>", "", summary
                    )[:500],
                    "source": source_name,
                    "source_url": url,
                    "evidence": "RSS headline and snippet",
                    "confidence": "Needs review",
                    "verified": "No"

                })

    return records


# --------------------------------
# 4. CLEAN AND SAVE DATA
# --------------------------------

def main():

    records = collect_news()

    if not records:

        print("No records found. Check internet connection.")
        return

    df = pd.DataFrame(records)

    # Remove duplicate articles
    df = df.drop_duplicates(subset=["source_url"])

    # Remove empty headlines
    df = df[df["title"].str.strip() != ""]

    # Sort by date
    df = df.sort_values(
        by="date",
        ascending=False
    )

    os.makedirs("data", exist_ok=True)

    output_file = "data/ai_policy_news.csv"

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n--------------------------------")
    print("NEWS COLLECTION COMPLETED")
    print("--------------------------------")

    print("Total records:", len(df))

    print("\nState-wise records:")
    print(df["state"].value_counts())

    print("\nCategory-wise records:")
    print(df["category"].value_counts())

    print("\nSaved to:", output_file)


if __name__ == "__main__":
    main()
