# ==================================================
# Flask Web App: AI eBook & Audiobook Library
# Author: Clean architecture + Gemini integration
# Refactored: Senior-level structure & practices
# ==================================================

import os
import logging
from flask import Flask, render_template, send_from_directory, request, abort, redirect, url_for
from dotenv import load_dotenv
import pyttsx3
import google.generativeai as genai

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Directory configuration
EBOOK_DIR = "ebooks"
AUDIO_DIR = "static/audio"
os.makedirs(EBOOK_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def generate_unique_filename(base: str, extension: str, directory: str) -> str:
    """
    Prevents file overwrites by appending a numeric suffix.
    Example: story.txt → story_1.txt
    """
    counter = 0
    candidate = f"{base}.{extension}"
    while os.path.exists(os.path.join(directory, candidate)):
        counter += 1
        candidate = f"{base}_{counter}.{extension}"
    return candidate


@app.route("/")
def index():
    """
    Homepage: displays a list of all .txt eBooks in the library.
    """
    ebooks = sorted(f for f in os.listdir(EBOOK_DIR) if f.endswith(".txt"))
    return render_template("index.html", ebooks=ebooks)


@app.route("/read/<filename>")
def read(filename):
    """
    Displays a single eBook's content in a styled HTML template.
    """
    filepath = os.path.join(EBOOK_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404)
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
    return render_template("read_book.html", filename=filename, content=content)


@app.route("/audio/<filename>")
def audio(filename):
    """
    Converts an eBook to audio using pyttsx3 and streams it in-browser.
    """
    audio_filename = filename.replace(".txt", ".mp3")
    audio_path = os.path.join(AUDIO_DIR, audio_filename)

    if not os.path.exists(audio_path):
        try:
            with open(os.path.join(EBOOK_DIR, filename), "r", encoding="utf-8") as file:
                text = file.read()
            engine = pyttsx3.init()
            engine.save_to_file(text, audio_path)
            engine.runAndWait()
        except Exception as e:
            logging.error(f"Audio generation failed for {filename}: {e}")
            return f"Error during audio generation: {str(e)}", 500

    return render_template("audio_player.html", audio_file=audio_filename)


@app.route("/download/<filename>")
def download(filename):
    """
    Allows users to download the raw .txt version of a book.
    """
    return send_from_directory(EBOOK_DIR, filename, as_attachment=True)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Handles AI story generation using Gemini when the user submits a theme.
    Saves a new eBook and refreshes the index page.
    """
    theme = request.form.get("theme", "").strip()
    if not theme:
        return redirect(url_for("index"))

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Write a creative short story (~500 words) titled '{theme}'. It should be imaginative and suitable for general audiences."

        response = model.generate_content(prompt)
        story = response.text.strip()

        filename_base = theme.replace(" ", "_").lower()
        filename = generate_unique_filename(filename_base, "txt", EBOOK_DIR)

        with open(os.path.join(EBOOK_DIR, filename), "w", encoding="utf-8") as file:
            file.write(story)

        logging.info(f"New story generated and saved: {filename}")

    except Exception as e:
        logging.exception("Error during AI story generation")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
