# ========================
# Flask Web App: AI eBook & Audiobook Library
# Author: Refactored for clarity, maintainability, and UX
# ========================

from flask import Flask, render_template, send_from_directory, request, abort
import os
import pyttsx3

# Flask app initialization
app = Flask(__name__)

# Define directories for books and generated audio
EBOOK_DIR = "ebooks"
AUDIO_DIR = "static/audio"

# Ensure the audio directory exists
os.makedirs(AUDIO_DIR, exist_ok=True)


@app.route("/")
def index():
    """
    Homepage route:
    Lists all available eBook files in the ebooks/ directory.
    """
    # Filter only .txt files (ignores temp or system files)
    ebooks = [f for f in os.listdir(EBOOK_DIR) if f.endswith(".txt")]
    return render_template("index.html", ebooks=ebooks)


@app.route("/read/<filename>")
def read(filename):
    """
    Route to render a full page for reading the selected eBook.
    Styled to match the rest of the app.
    """
    try:
        with open(os.path.join(EBOOK_DIR, filename), "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("read_book.html", filename=filename, content=content)
    except FileNotFoundError:
        abort(404)


@app.route("/audio/<filename>")
def audio(filename):
    """
    Route to generate audio for a book and stream it in-browser.
    If audio already exists, skip regeneration.
    """
    # Derive audio filename from text filename
    audio_file = filename.replace(".txt", ".mp3")
    audio_path = os.path.join(AUDIO_DIR, audio_file)

    # Only generate if it doesn't already exist
    if not os.path.exists(audio_path):
        book_path = os.path.join(EBOOK_DIR, filename)
        try:
            # Load text content
            with open(book_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Initialize TTS engine and export as MP3
            engine = pyttsx3.init()
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

        except Exception as e:
            return f"Error during audio generation: {str(e)}", 500

    # Stream audio via <audio> tag from static folder
    return render_template("audio_player.html", audio_file=audio_file)


@app.route("/download/<filename>")
def download(filename):
    """
    Route to allow downloading of eBook .txt files directly.
    """
    return send_from_directory(EBOOK_DIR, filename, as_attachment=True)


# Entry point to run the server in debug mode
if __name__ == "__main__":
    app.run(debug=True)
