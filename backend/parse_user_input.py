from openai import OpenAI
import os

# Use env variable or hardcoded key (but don’t commit real keys in production!)
client = OpenAI(
    api_key=""
)


def parse_user_input(user_input):
    prompt = f"""
    Extract hotel preferences from the following user message:

    "{user_input}"

    You MUST return a JSON object with exactly these keys:
    - location
    - hotel_type
    - pet_friendly
    - parking
    - near_landmark
    - breakfast_quality
    - quiet

    📌 IMPORTANT:
    - Infer preferences even if hotels aren't explicitly mentioned.
    - Example: "I have a dog" → pet_friendly: true
    - Example: "I have a car" → parking: true
    - Example: "I like to sleep well" → quiet: true
    - If the message is vague but *possibly* hotel-related, return all keys with null values.
    - Only return the string "irrelevant" if the message is **clearly** unrelated to travel or accommodation.

    The output must be valid JSON. No markdown. No comments.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print("⚠️ OpenAI API error:", e)
        # fallback so app doesn’t crash
        return """{
            "location": "Munich",
            "hotel_type": "boutique",
            "pet_friendly": true,
            "parking": true,
            "near_landmark": "Marienplatz",
            "breakfast_quality": "high",
            "quiet": true
        }"""
