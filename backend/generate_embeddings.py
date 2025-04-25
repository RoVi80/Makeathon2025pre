from openai import OpenAI
import pandas as pd
import time
import pickle

client = OpenAI(api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # or use env variable

# 1. Load the CSV file
df = pd.read_csv("mock_hotel_data_munich.csv")

# 2. Ensure 'description' column exists
if "description" not in df.columns:
    raise ValueError("❌ 'description' column not found in your CSV.")

# 3. Define embedding function
def embed(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"⚠️ Error embedding: {e}")
        return None

# 4. Generate embeddings for each hotel
print("🚀 Generating embeddings...")
df["embedding"] = df["description"].apply(embed)
print("✅ All embeddings generated!")

# 5. Save the new CSV with embeddings
df.to_csv("hotel_data_with_embeddings.csv", index=False)
print("📦 Saved CSV with embeddings -> hotel_data_with_embeddings.csv")

# 6. Also save the embeddings separately as .pkl
with open("hotel_embeddings.pkl", "wb") as f:
    pickle.dump(df["embedding"].tolist(), f)
print("💾 Saved raw embeddings -> hotel_embeddings.pkl")