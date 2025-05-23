# ========================================
# AI eBook Generator using Gemini Pro API
# Google SDK v0.8.5+
# ========================================

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API client
genai.configure(api_key=GEMINI_API_KEY)

# Use the Gemini Pro model (v0.8.5+ supports it)
model = genai.GenerativeModel("gemini-1.5-flash")

# Story themes
themes = [
    "Space Adventure",
    "Jungle Mystery",
    "Ancient Egypt",
    "Robot Rebellion",
    "Underwater City"
]

# Output directory
OUTPUT_DIR = "ebooks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Unique filename generator
def generate_unique_filename(base: str, extension: str, directory: str) -> str:
    counter = 0
    candidate = f"{base}.{extension}"
    while os.path.exists(os.path.join(directory, candidate)):
        counter += 1
        candidate = f"{base}_{counter}.{extension}"
    return candidate

# Prompt builder
def build_prompt(theme: str) -> str:
    return f"Write a creative short story (~500 words) titled '{theme}'. It should be imaginative and suitable for general audiences."

# Story generation loop
for i, theme in enumerate(themes, start=1):
    try:
        print(f"[{i}] Generating: {theme}...")
        prompt = build_prompt(theme)

        # Gemini Pro content generation
        response = model.generate_content(prompt)

        story = response.text.strip()
        base_filename = f"book{i}_{theme.replace(' ', '_').lower()}"
        final_filename = generate_unique_filename(base_filename, "txt", OUTPUT_DIR)

        with open(os.path.join(OUTPUT_DIR, final_filename), "w", encoding="utf-8") as f:
            f.write(story)

        print(f"✅ Saved: {final_filename}")

    except Exception as e:
        print(f"❌ Error generating '{theme}': {e}")

print(f"\n📚 Done. Stories saved to '{OUTPUT_DIR}/'")
