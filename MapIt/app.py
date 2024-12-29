from flask import Flask, render_template, request, redirect, url_for
import os
from utils.extract_pdf_text import extract_text_from_pdf
from utils.process_text import extract_keywords_and_subheadings
from create_mind_map import create_mind_map

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def upload_pdf():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return "No file part", 400
        file = request.files["pdf_file"]
        if file.filename == "":
            return "No selected file", 400
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Step 1: Extract text
            extracted_text = extract_text_from_pdf(filepath)
            with open("extracted_text.txt", "w") as f:
                f.write(extracted_text)

            # Step 2: Process text and extract headings and subheadings
            headings, subheadings = extract_keywords_and_subheadings(extracted_text)
            with open("headings.txt", "w") as f:
                f.write("\n".join(headings))

            # Step 3: Create hierarchical mind map
            create_mind_map(headings, subheadings)

            return redirect(url_for("result"))
    return render_template("upload.html")

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(debug=True)
