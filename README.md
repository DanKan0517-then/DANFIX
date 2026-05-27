# DanFix - Text Formatting and Grammar Compiler

DanFix is a text formatting and grammar checker project built using Python and Flask.

Instead of checking text in a normal way, this project follows a compiler design approach where English text is processed like source code in a programming language compiler.

The system breaks text into tokens, builds sentence structures, checks spelling and grammar, and then generates a report showing errors and suggestions.

This project was made for understanding compiler concepts in a practical way.

---

## What the project does

- Checks spelling mistakes
- Detects grammar issues
- Gives suggestions for corrections
- Shows highlighted errors in UI
- Gives statistics of errors found
- Can auto-correct text
- Supports text input and `.txt` file upload

---

## How it works

This project works in 4 stages like a compiler.

### 1. Lexical Analysis (`lexer.py`)

The lexer reads the text and converts it into tokens.

Example:

```text
Hello world!
```

becomes:

```text
WORD -> Hello
WORD -> world
PUNCTUATION -> !
```

This helps the system understand what is text, punctuation, spaces, etc.

---

### 2. Syntax Parsing (`parser.py`)

The parser takes tokens from lexer and creates sentence structures.

It groups tokens into sentences and paragraphs so grammar checking becomes easier.

Basically, it organizes the text before analysis.

---

### 3. Semantic Analysis (`semantic.py`)

This is where most checking happens.

The system checks:

- Spelling mistakes
- Grammar mistakes
- Wrong word usage

Libraries used:

- `pyspellchecker`
- `language_tool_python`

Suggestions are also generated here.

---

### 4. Error Reporting (`error_reporter.py`)

After errors are found, a report is generated.

The system:

- Creates structured JSON output
- Generates error statistics
- Sends correction suggestions
- Produces corrected text

---

## Project Structure

```bash
compiler/

├── app.py
├── requirements.txt

├── compiler/
│   ├── __init__.py
│   ├── lexer.py
│   ├── parser.py
│   ├── semantic.py
│   └── error_reporter.py

├── templates/
│   └── index.html

└── static/
    ├── css/style.css
    ├── js/main.js
    └── img/bear.png
```

### File Explanation

- `app.py` → Main Flask app  
- `lexer.py` → Converts text into tokens  
- `parser.py` → Creates sentence structure  
- `semantic.py` → Checks spelling and grammar  
- `error_reporter.py` → Generates report and corrected text  
- `main.js` → Frontend logic  
- `style.css` → UI styling

---

## Technologies Used

Backend:
- Python
- Flask

Libraries:
- pyspellchecker
- language_tool_python

Frontend:
- HTML
- CSS
- JavaScript

---

## How to Run

### 1. Clone project

```bash
git clone <repo-link>
cd compiler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the project

```bash
python3 app.py
```

Open browser:

```text
http://localhost:5050
```

---

## Features in UI

- Text input area
- Example story button
- Drag and drop text file upload
- Error statistics
- Highlighted spelling errors
- Highlighted grammar errors
- Suggestions for fixing mistakes

---

## Why this project?

This project was mainly built to understand compiler design concepts in a practical way instead of only learning theory.

The idea was to treat English text like source code and process it through compiler stages such as lexical analysis, parsing, semantic analysis, and reporting.

---
##This is how it looks
<img width="456" height="547" alt="Screenshot 2026-05-27 at 12 36 25 PM" src="https://github.com/user-attachments/assets/e9a70321-b897-4304-87f8-f66144ef5790" />

