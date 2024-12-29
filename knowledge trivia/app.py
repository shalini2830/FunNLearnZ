import os
import random
from flask import Flask, request, jsonify, render_template
import PyPDF2
import spacy

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract sentences and keywords
def extract_sentences_and_keywords(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    keywords = [
        token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"] and len(token.text) > 1
    ]
    return sentences, list(set(keywords))

# Function to generate MCQs
def generate_mcqs(sentences, keywords, num_questions=10):
    mcqs = []
    for sentence in random.sample(sentences, min(len(sentences), num_questions)):
        for keyword in keywords:
            if keyword in sentence:
                question, correct_answer = create_question(sentence, keyword)
                options = generate_options(correct_answer, keywords)
                mcqs.append({"question": question, "options": options, "answer": correct_answer})
                break
        if len(mcqs) >= num_questions:
            break
    return mcqs

# Helper function to create questions
def create_question(sentence, keyword):
    question = sentence.replace(keyword, "_____")
    correct_answer = keyword
    return question, correct_answer

# Helper function to generate options
def generate_options(correct_answer, keywords, num_options=4):
    options = [correct_answer]
    distractors = random.sample(
        [word for word in keywords if word != correct_answer and len(word) > 1], 
        min(len(keywords), num_options - 1)
    )
    options.extend(distractors)
    random.shuffle(options)
    return options

# Route to serve the homepage
@app.route("/")
def index():
    return render_template("index.html")

# Route to handle PDF upload and MCQ generation
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        text = extract_text_from_pdf(file)
        sentences, keywords = extract_sentences_and_keywords(text)
        mcqs = generate_mcqs(sentences, keywords)
        return jsonify({"mcqs": mcqs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
