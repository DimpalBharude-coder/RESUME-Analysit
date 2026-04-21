from flask import Flask, render_template, request, jsonify
import PyPDF2
from docx import Document
import re
import io
import os
import spacy

# Load spacy safely
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

class ResumeAnalyzer:

    def extract_text(self, file_content, filename):
        if filename.endswith('.pdf'):
            pdf = PyPDF2.PdfReader(io.BytesIO(file_content))
            return " ".join([p.extract_text() or "" for p in pdf.pages])

        elif filename.endswith('.docx'):
            doc = Document(io.BytesIO(file_content))
            return " ".join([p.text for p in doc.paragraphs])

        return ""

    def calculate_score(self, text):
        score = 0
        text = text.lower()

        keywords = ["python", "java", "sql", "html", "css", "react", "aws"]

        score += sum(10 for k in keywords if k in text)

        if len(text.split()) > 300:
            score += 20

        return min(score, 100)

    def analyze(self, file_content, filename):
        text = self.extract_text(file_content, filename)

        if not text.strip():
            return {'success': False, 'error': 'Cannot read file'}

        doc = nlp(text)

        skills = list(set([
            token.text.lower()
            for token in doc
            if token.pos_ in ["NOUN", "PROPN"]
        ]))[:10]

        role = "Software Developer"
        if "python" in text.lower():
            role = "Python Developer"
        elif "java" in text.lower():
            role = "Java Developer"
        elif "html" in text.lower():
            role = "Frontend Developer"

        result_text = f"""
Skills: {', '.join(skills)}

Suggested Role: {role}

Improvements:
- Add more technical keywords
- Add projects
- Improve formatting
- Add achievements
"""

        return {
            'success': True,
            'score': self.calculate_score(text),
            'ai_analysis': result_text
        }


analyzer = ResumeAnalyzer()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})

    file = request.files['resume']
    content = file.read()

    result = analyzer.analyze(content, file.filename)
    return jsonify(result)


# REQUIRED FOR RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)