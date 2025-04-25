import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

client = OpenAI(api_key="xx")


def rank_hotels(filters, user_query):
    if isinstance(filters, str):
        if filters.strip().lower() == "irrelevant":
            print("🚫 Message marked as irrelevant by LLM.")
            raise ValueError("❌ That doesn't seem to be a hotel-related request.")
        else:
            raise TypeError(f"❌ Unexpected filter type (str): {filters}")

    if not isinstance(filters, dict):
        raise TypeError(f"❌ Filters must be a dictionary. Got: {type(filters)}")

    df = pd.read_csv("hotel_data_with_embeddings.csv")
    df["embedding"] = df["embedding"].apply(eval)

    print("📥 Filters received:", filters)

    try:
        query_embed = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_query
        ).data[0].embedding
    except Exception as e:
        print("❌ Query embedding failed:", e)
        query_embed = None

    df["score"] = 0.0
    matched_filters_list = []
    failed_filters_list = []

    for i, row in df.iterrows():
        matched = []
        failed = []

        # HARD FILTERS
        if filters.get("pet_friendly") is not None:
            if row["pet_friendly"] == filters["pet_friendly"]:
                matched.append("pet_friendly")
            else:
                failed.append("pet_friendly")

        if filters.get("quiet") is not None:
            if row["quiet"] == filters["quiet"]:
                matched.append("quiet")
            else:
                failed.append("quiet")

        if filters.get("parking") is not None:
            if row["parking"] == filters["parking"]:
                matched.append("parking")
            else:
                failed.append("parking")

        # SOFT FILTER SCORING
        score = 0.0

        if filters.get("near_landmark"):
            print(f"🔎 Checking if '{filters['near_landmark'].lower()}' is in '{row['near_landmark'].lower()}'")
            if pd.notna(row["near_landmark"]) and filters["near_landmark"].lower() in row["near_landmark"].lower():
                matched.append("near_landmark")
            else:
                failed.append("near_landmark")

        # New improved scoring based on matched filters
        if "pet_friendly" in matched:
            score += 3.0
        if "quiet" in matched:
            score += 3.0
        if "near_landmark" in matched:
            score += 2.5

        if filters.get("breakfast_quality") == "high":
            score += (row["breakfast_rating"] or 0) * 0.5

        if filters.get("parking") is False:
            score -= row["parking"] * 0.5

        score -= (row["distance_to_center_km"] or 10) * 0.3

        matched_filters_list.append(matched)
        failed_filters_list.append(failed)
        df.at[i, "score"] = score

    if query_embed is not None:
        hotel_vecs = np.vstack(df["embedding"])
        query_vec = np.array(query_embed).reshape(1, -1)
        similarities = cosine_similarity(query_vec, hotel_vecs)[0]
        df["score"] += similarities * 2.0

    if np.max(similarities) < 0.20:
        print("🚫 Query too unrelated to any hotels.")
        raise ValueError("❌ That doesn't seem to be a hotel-related request.")

    df["matched_filters"] = matched_filters_list
    df["failed_filters"] = failed_filters_list

    df = df.sort_values("score", ascending=False)

    print(f"✅ Top {min(10, len(df))} results returned\n")
    print("🔍 Top Scoring Hotels Breakdown:")
    for _, row in df.head(10).iterrows():
        print(f"🏨 {row['name']} | Score: {row['score']:.2f} | Matched: {row['matched_filters']} | Failed: {row['failed_filters']}")

    return df.head(10)[[
        "name", "location", "near_landmark", "breakfast_rating",
        "pet_friendly", "parking", "quiet", "distance_to_center_km",
        "score", "matched_filters", "failed_filters"
    ]].to_dict(orient="records")
