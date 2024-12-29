from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import random
import time

app = Flask(__name__)
CORS(app)

# Global variables for game state
words_to_find = []
start_time = None
fail_attempts = 0

def extract_keywords_from_pdf(pdf_file):
    """Extract unique words from a PDF and select 5 random words."""
    reader = PdfReader(pdf_file)
    words = []
    for page in reader.pages:
        text = page.extract_text()
        words.extend([word.upper() for word in text.split() if word.isalpha()])
    unique_words = list(set(words))
    if len(unique_words) < 5:
        raise ValueError("PDF does not contain enough unique words.")
    return random.sample(unique_words, 5)

@app.route("/", methods=["POST"])
def upload_pdf():
    global words_to_find, start_time
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400
    pdf_file = request.files["pdf"]
    try:
        words_to_find = extract_keywords_from_pdf(pdf_file)
        start_time = time.time()  # Start the timer
        return jsonify({"message": "Select the following", "words": words_to_find}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

@app.route("/validate_word", methods=["POST"])
def validate_word():
    global words_to_find, fail_attempts
    word = request.json.get("word", "").upper()
    if word in words_to_find:
        words_to_find.remove(word)
        return jsonify({"valid": True, "remaining_words": len(words_to_find)}), 200
    fail_attempts += 1
    return jsonify({"valid": False, "remaining_words": len(words_to_find)}), 200

@app.route("/score", methods=["POST"])
def calculate_score():
    global start_time, fail_attempts
    if not start_time:
        return jsonify({"error": "Game not started yet"}), 400

    end_time = time.time()
    time_taken = round(end_time - start_time)
    score = max(100 - (fail_attempts * 10) - (time_taken // 10), 0)
    return jsonify({"score": score, "time_taken": time_taken, "fail_attempts": fail_attempts})

if __name__ == "__main__":
    app.run(debug=True)
