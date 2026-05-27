"""
app.py — Flask entry point for DanFix
"""

import os
import io
import json

from flask import Flask, request, jsonify, render_template, send_from_directory

from compiler.lexer         import Lexer
from compiler.parser        import Parser
from compiler.semantic      import SemanticAnalyser
from compiler.error_reporter import ErrorReporter

# Optional file-parsing libraries
try:
    import PyPDF2
    _PDF_OK = True
except ImportError:
    _PDF_OK = False

try:
    from docx import Document as DocxDocument
    _DOCX_OK = True
except ImportError:
    _DOCX_OK = False

# ── Flask setup ──────────────────────────────────────────────────────
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024   # 5 MB upload limit

lexer    = Lexer()
parser   = Parser()
semantic = SemanticAnalyser()
reporter = ErrorReporter()

# ── helpers ──────────────────────────────────────────────────────────
def _extract_text(file) -> str:
    """Extract plain text from an uploaded file object."""
    filename = file.filename.lower()

    if filename.endswith('.txt'):
        return file.read().decode('utf-8', errors='replace')

    if filename.endswith('.pdf') and _PDF_OK:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return '\n'.join(
            page.extract_text() or '' for page in reader.pages
        )

    if filename.endswith('.docx') and _DOCX_OK:
        doc = DocxDocument(io.BytesIO(file.read()))
        return '\n'.join(p.text for p in doc.paragraphs)

    return file.read().decode('utf-8', errors='replace')


# ── routes ───────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/analyse', methods=['POST'])
def analyse():
    # ── 1. get input text ────────────────────────────────────────────
    if 'file' in request.files and request.files['file'].filename:
        text = _extract_text(request.files['file'])
    else:
        data = request.get_json(silent=True) or {}
        text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'No text provided.'}), 400

    # ── 2. run the pipeline ──────────────────────────────────────────
    tokens   = lexer.tokenise(text)
    ast      = parser.parse(tokens)
    errors   = semantic.analyse(ast)
    ast_dict = parser.to_dict(ast)
    report   = reporter.generate_report(text, errors, tokens, ast_dict)

    return jsonify(report)


# ── demo endpoint ─────────────────────────────────────────────────────
@app.route('/demo')
def demo():
    sample = (
        "i is very good at speling and grammer. "
        "she dont know how to wright properly. "
        "their going to the park tommorow."
    )
    return jsonify({'text': sample})


if __name__ == '__main__':
    app.run(debug=True, port=5050)
