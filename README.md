# AI Notes to Quiz and Flashcard Generator

## Project Title
**AI Notes to Quiz and Flashcard Generator**  
**Application:** StudyAI | Notes to Quiz & Flashcards

## Overview
StudyAI is an AI-powered educational application that converts study notes into multiple-choice quizzes and revision flashcards. Users can paste notes or upload PDF, TXT, or Markdown files. Google Gemini analyzes the notes and generates study material automatically.

## Objectives
- Convert study notes into interactive quizzes.
- Generate useful flashcards automatically.
- Help students revise important concepts quickly.
- Provide Easy, Medium, and Hard quiz levels.
- Calculate quiz scores and show explanations.
- Allow generated quizzes and flashcards to be downloaded.

## Features
### Notes
- Paste study material directly.
- Upload PDF, TXT, or Markdown files.
- Preview imported notes.

### Quiz Generator
- Generate 5, 10, 15, or 20 questions.
- Select Easy, Medium, or Hard difficulty.
- Four options per question with one correct answer.
- Explanations after submission.
- Automatic score and percentage.
- Download quiz as a TXT file.

### Flashcards
- Generate 5, 10, 15, or 20 cards.
- Focus on definitions, concepts, facts, processes, formulas, and exam-relevant information.
- Reveal answers when needed.
- Previous, Next, and Random Card navigation.
- Download flashcards as a TXT file.

### Dashboard
Shows notes character count, quiz question count, flashcard count, quiz score, and Gemini connection status.

## Technologies Used
- Python 3.11.9
- Streamlit
- Google Gemini AI
- Pandas
- NumPy
- Scikit-learn
- Requests
- python-dotenv
- PyPDF
- python-docx
- OpenPyXL
- Pytesseract
- NLTK
- spaCy
- Transformers
- PyTorch
- LangChain
- LangChain Community

## Requirements
```text
Python 3.11.9
streamlit>=1.40,<2
pandas>=2.2,<3
numpy>=1.26,<3
scikit-learn>=1.5,<2
requests>=2.32,<3
python-dotenv>=1.0,<2
pypdf>=5,<7
python-docx>=1.1,<2
openpyxl>=3.1,<4
pytesseract>=0.3,<1
nltk>=3.9,<4
spacy>=3.7,<4
transformers>=4.45,<6
torch>=2.4,<3
google-genai>=1.0,<2
langchain>=0.3,<2
langchain-community>=0.3,<1
```

**Additional requirement:** Install the Tesseract OCR engine separately for `pytesseract`.

## Installation and Setup

### 1. Check Python
Open Terminal and run:
```bash
python3 --version
```
The project requires Python 3.11.9.

### 2. Open the Project in VS Code
Create/open a folder such as `StudyAI`, then open **Terminal → New Terminal**.

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 5. Install Packages
Create `requirements.txt` with the requirements listed above, then run:
```bash
pip install -r requirements.txt
```
You do not need to reinstall packages every time you close Terminal. When reopening Terminal, activate the environment again with:
```bash
source venv/bin/activate
```

### 6. Install Tesseract OCR on macOS
If Homebrew is installed:
```bash
brew install tesseract
```
Check it with:
```bash
tesseract --version
```

## Gemini API Key
Create a `.env` file in the project folder:
```env
GEMINI_API_KEY=your_api_key_here
```
Replace the value with your actual Gemini API key.

Never upload `.env` or your API key to GitHub.

Recommended `.gitignore`:
```text
.env
venv/
__pycache__/
```

## Project Structure
```text
StudyAI/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── assets/
│   └── style.css
└── venv/
```

## Running the Application
Activate the environment:
```bash
source venv/bin/activate
```
Then run:
```bash
streamlit run app.py
```
The application normally opens at `http://localhost:8501`.

## How to Use
1. Open the Dashboard.
2. Go to **Notes**.
3. Paste notes or upload a PDF, TXT, or Markdown file.
4. Save/import the notes.
5. Open **Quiz Generator**.
6. Select the question count and difficulty.
7. Click **Generate Quiz**.
8. Answer the questions and submit the quiz.
9. Open **Flashcards** to generate revision cards.
10. Reveal answers and navigate between cards.
11. Download the generated material if required.

## Sample Input
```text
Database Management System

A Database Management System (DBMS) is software used to create,
store, manage and retrieve data from a database.

Advantages of DBMS include data security, data consistency,
reduced data redundancy and data sharing.

ACID properties are important for reliable transactions.
ACID stands for Atomicity, Consistency, Isolation and Durability.
```

## Sample Quiz Output
```text
1. What does DBMS stand for?

A. Data Backup Management System
B. Database Management System
C. Database Monitoring Service
D. Data Model Storage

Answer: Database Management System

Explanation: DBMS stands for Database Management System. It is
software used to create, store, manage and retrieve data from a database.
```

## Sample Flashcard Output
```text
Card 1
Question: What is a DBMS?
Answer: A Database Management System is software used to create,
store, manage and retrieve data from a database.

Card 2
Question: What are the four ACID properties?
Answer: Atomicity, Consistency, Isolation and Durability.
```

## System Workflow
```text
Student Notes
     ↓
Paste / Upload Notes
     ↓
StudyAI
     ↓
Google Gemini AI
     ↓
 ┌─────────────────────┐
 │                     │
Quiz Generator   Flashcard Generator
 │                     │
 ↓                     ↓
MCQ Questions      Revision Cards
 │                     │
 ↓                     ↓
Quiz Score         Review Concepts
```

## Quiz Scoring
```text
Score = Number of Correct Answers

Percentage = (Correct Answers / Total Questions) × 100
```
The application displays feedback based on the percentage.

## Troubleshooting

### Gemini Not Connected
Check that `.env` exists and contains:
```env
GEMINI_API_KEY=your_api_key_here
```
Then restart Streamlit.

### ModuleNotFoundError
Activate the environment:
```bash
source venv/bin/activate
```
Then:
```bash
pip install -r requirements.txt
```

### Check Installed Packages
```bash
pip list
```
For one package:
```bash
pip show streamlit
```

### Streamlit Not Found
```bash
python -m streamlit run app.py
```

### PDF Text Extraction Problems
Text-based PDFs work best with `pypdf`. Scanned image-only PDFs may require OCR with Tesseract.

## Future Enhancements
- DOCX upload support
- OCR for scanned notes
- Timed quizzes
- Progress tracking
- User accounts and database storage
- Adaptive quizzes
- PDF/Excel export
- Voice-based learning
- Multi-language support
- Spaced-repetition flashcards
- Performance analytics

## Academic Project
This project demonstrates the use of Artificial Intelligence, Generative AI, Natural Language Processing, Python programming, Streamlit web development, API integration, file processing, and interactive educational application development.

## Project Name
**StudyAI – AI Notes to Quiz & Flashcard Generator**

**Built with:** Python + Streamlit + Google Gemini AI
