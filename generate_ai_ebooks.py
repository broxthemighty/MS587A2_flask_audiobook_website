# ================================================
# AI eBook Generator Script using OpenAI's GPT API
# Author: Refactored for real-world dev practices
# ================================================

import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client using the modern SDK
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Directory where eBooks will be saved
OUTPUT_DIR = "ebooks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Short story themes — you can expand this list easily
themes = [
    "Space Adventure",
    "Jungle Mystery",
    "Ancient Egypt",
    "Robot Rebellion",
    "Underwater City"
]

# Prompt template to use for generation
def build_prompt(theme: str) -> str:
    """
    Constructs the prompt for GPT based on the desired theme.
    """
    return f"Write a creative short story (~500 words) titled '{theme}'. Make it engaging and suitable for a general audience."

# Generate and save the stories
for idx, theme in enumerate(themes, start=1):
    try:
        print(f"[{idx}] Generating story: '{theme}'...")

        # Send chat-style message to GPT-3.5
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative fiction writer."},
                {"role": "user", "content": build_prompt(theme)}
            ]
        )

        # Extract the story text from the first response choice
        story = response.choices[0].message.content.strip()

        # Generate a safe filename
        filename = f"book{idx}_{theme.replace(' ', '_').lower()}.txt"
        path = os.path.join(OUTPUT_DIR, filename)

        # Save the story to a .txt file
        with open(path, "w", encoding="utf-8") as file:
            file.write(story)

        print(f"✅ Saved: {path}")

    except OpenAIError as e:
        # Handle API quota, rate limit, or key errors
        print(f"❌ Failed to generate '{theme}': {str(e)}")

    except Exception as e:
        # Catch-all for I/O or unexpected issues
        print(f"🚨 Unexpected error: {str(e)}")

print(f"\n📚 Done generating {len(themes)} stories. Files are in: {OUTPUT_DIR}/")
