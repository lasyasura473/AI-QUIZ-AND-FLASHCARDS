import os
import json
import random
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StudyAI - Notes to Quiz & Flashcards",
    page_icon="🧠",
    layout="wide"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:
    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY
        )
    except Exception as e:
        st.error(
            f"Gemini initialization failed: {e}"
        )


MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# SESSION STATE
# ============================================================

default_values = {
    "active_page": "Dashboard",
    "notes": "",
    "quiz": [],
    "flashcards": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "score": 0,
    "flashcard_index": 0
}

for key, value in default_values.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 45px;
        font-weight: bold;
        margin-top: 20px;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        margin-bottom: 30px;
    }

    .card {
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #444;
        margin-bottom: 20px;
    }

    .question {
        font-size: 20px;
        font-weight: bold;
    }

    .flashcard {
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #555;
        text-align: center;
        margin: 20px 0;
    }

    .flashcard-question {
        font-size: 28px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# PDF READER
# ============================================================

def extract_pdf_text(uploaded_file):

    try:

        pdf_bytes = uploaded_file.read()

        reader = PdfReader(
            BytesIO(pdf_bytes)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return clean_text(
            "\n".join(pages)
        )

    except Exception as e:

        st.error(
            f"Could not read PDF: {e}"
        )

        return ""


# ============================================================
# FILE READER
# ============================================================

def read_uploaded_file(uploaded_file):

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):

        return extract_pdf_text(
            uploaded_file
        )

    try:

        data = uploaded_file.read()

        return clean_text(
            data.decode("utf-8")
        )

    except Exception as e:

        st.error(
            f"Could not read file: {e}"
        )

        return ""


# ============================================================
# GEMINI FUNCTION
# ============================================================

def call_gemini(prompt):

    if client is None:

        st.error(
            "Gemini API is not connected."
        )

        return None

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt

        )

        return response.text

    except Exception as e:

        st.error(
            f"Gemini request failed: {e}"
        )

        return None


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    if not text:
        return None

    text = text.strip()

    # Remove Markdown code fences
    if text.startswith("```"):

        text = text.replace(
            "```json",
            "",
            1
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    # Try complete JSON
    try:

        return json.loads(text)

    except json.JSONDecodeError:

        pass

    # Try JSON array
    start = text.find("[")

    end = text.rfind("]")

    if start != -1 and end != -1:

        try:

            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError:

            pass

    # Try JSON object
    start = text.find("{")

    end = text.rfind("}")

    if start != -1 and end != -1:

        try:

            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError:

            pass

    return None


# ============================================================
# QUIZ GENERATOR
# ============================================================

def generate_quiz(
    notes,
    question_count,
    difficulty
):

    prompt = f"""
You are an expert educational quiz generator.

Create exactly {question_count}
multiple-choice questions based ONLY
on the study notes below.

Difficulty: {difficulty}

Rules:

1. Use only information from the notes.
2. Create exactly 4 options.
3. Only one option must be correct.
4. Do not repeat questions.
5. Wrong options should be plausible.
6. Give a short explanation.
7. The answer must exactly match one option.
8. Return ONLY valid JSON.
9. Do not use Markdown.

Return this exact structure:

[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Correct option",
    "explanation": "Short explanation"
  }}
]

STUDY NOTES:

{notes}
"""

    response = call_gemini(prompt)

    data = extract_json(response)

    if not isinstance(data, list):

        st.error(
            "Gemini did not return a valid quiz."
        )

        return []

    quiz = []

    for item in data:

        if not isinstance(item, dict):
            continue

        question = item.get(
            "question"
        )

        options = item.get(
            "options"
        )

        answer = item.get(
            "answer"
        )

        explanation = item.get(
            "explanation",
            ""
        )

        if (
            question
            and isinstance(options, list)
            and len(options) == 4
            and answer in options
        ):

            quiz.append(
                {
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                }
            )

    return quiz


# ============================================================
# FLASHCARD GENERATOR
# ============================================================

def generate_flashcards(
    notes,
    card_count
):

    prompt = f"""
You are an expert study assistant.

Create exactly {card_count}
useful flashcards from the study notes.

Focus on:

- Definitions
- Important concepts
- Key facts
- Processes
- Relationships
- Exam-relevant information

Rules:

1. Use ONLY the provided notes.
2. Do not invent information.
3. Avoid duplicate flashcards.
4. Keep questions short.
5. Keep answers clear.
6. Return ONLY valid JSON.
7. Do not use Markdown.

Return this exact structure:

[
  {{
    "question": "What is ...?",
    "answer": "Clear answer..."
  }}
]

STUDY NOTES:

{notes}
"""

    response = call_gemini(prompt)

    data = extract_json(response)

    if not isinstance(data, list):

        st.error(
            "Gemini did not return valid flashcards."
        )

        return []

    cards = []

    for item in data:

        if not isinstance(item, dict):
            continue

        question = item.get(
            "question"
        )

        answer = item.get(
            "answer"
        )

        if question and answer:

            cards.append(
                {
                    "question": question,
                    "answer": answer
                }
            )

    return cards


# ============================================================
# QUIZ DOWNLOAD
# ============================================================

def quiz_to_text(quiz):

    output = ""

    output += "STUDYAI - AI GENERATED QUIZ\n"

    output += "=" * 60

    output += "\n\n"

    for index, item in enumerate(
        quiz,
        start=1
    ):

        output += (
            f"{index}. "
            f"{item['question']}\n\n"
        )

        for option_index, option in enumerate(
            item["options"],
            start=1
        ):

            output += (
                f"   {option_index}. "
                f"{option}\n"
            )

        output += (
            f"\nAnswer: "
            f"{item['answer']}\n"
        )

        output += (
            f"Explanation: "
            f"{item['explanation']}\n"
        )

        output += "\n"

        output += "-" * 60

        output += "\n\n"

    return output


# ============================================================
# FLASHCARD DOWNLOAD
# ============================================================

def flashcards_to_text(cards):

    output = ""

    output += "STUDYAI - AI FLASHCARDS\n"

    output += "=" * 60

    output += "\n\n"

    for index, card in enumerate(
        cards,
        start=1
    ):

        output += (
            f"Card {index}\n"
        )

        output += (
            f"Question: "
            f"{card['question']}\n"
        )

        output += (
            f"Answer: "
            f"{card['answer']}\n"
        )

        output += "\n"

        output += "-" * 60

        output += "\n\n"

    return output


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧠 StudyAI")

    st.caption(
        "Smart Study Assistant"
    )

    st.divider()

    st.subheader(
        "Navigation"
    )

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.session_state.active_page = (
            "Dashboard"
        )

        st.rerun()

    if st.button(
        "📝 Notes",
        use_container_width=True
    ):

        st.session_state.active_page = (
            "Notes"
        )

        st.rerun()

    if st.button(
        "🎯 Quiz Generator",
        use_container_width=True
    ):

        st.session_state.active_page = (
            "Quiz Generator"
        )

        st.rerun()

    if st.button(
        "🎴 Flashcards",
        use_container_width=True
    ):

        st.session_state.active_page = (
            "Flashcards"
        )

        st.rerun()

    st.divider()

    if client:

        st.success(
            "Gemini Connected"
        )

    else:

        st.warning(
            "Gemini Not Connected"
        )

    st.caption(
        "Study smarter. Learn faster. 🚀"
    )


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.active_page == "Dashboard":

    st.markdown(
        """
        <div class="main-title">
            🧠 StudyAI
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="subtitle">
            AI Notes to Quiz & Flashcard Generator
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Turn your study notes into quizzes "
        "and flashcards using Gemini AI."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Notes Characters",
            f"{len(st.session_state.notes):,}"
        )

    with col2:

        st.metric(
            "Quiz Questions",
            len(st.session_state.quiz)
        )

    with col3:

        st.metric(
            "Flashcards",
            len(st.session_state.flashcards)
        )

    with col4:

        if st.session_state.quiz:

            st.metric(
                "Quiz Score",
                f"{st.session_state.score}/"
                f"{len(st.session_state.quiz)}"
            )

        else:

            st.metric(
                "Quiz Score",
                "—"
            )

    st.divider()

    st.subheader(
        "How it works"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "### 📝 1. Add Your Notes"
        )

        st.write(
            "Paste your notes or upload "
            "a PDF, TXT or Markdown file."
        )

    with col2:

        st.markdown(
            "### 🤖 2. Let Gemini Generate"
        )

        st.write(
            "Gemini analyzes your notes "
            "and creates study material."
        )

    with col3:

        st.markdown(
            "### 🚀 3. Start Learning"
        )

        st.write(
            "Take quizzes and revise "
            "using flashcards."
        )


# ============================================================
# NOTES PAGE
# ============================================================

elif st.session_state.active_page == "Notes":

    st.title(
        "📝 Your Notes"
    )

    st.write(
        "Add the material that you "
        "want Gemini to analyze."
    )

    tab1, tab2 = st.tabs(
        [
            "Paste Notes",
            "Upload File"
        ]
    )

    # --------------------------------------------------------
    # PASTE NOTES
    # --------------------------------------------------------

    with tab1:

        notes_input = st.text_area(
            "Study Notes",

            value=st.session_state.notes,

            height=400,

            placeholder=(
                "Paste your lecture notes, "
                "textbook content or study material here..."
            )
        )

        if st.button(
            "💾 Save Notes",
            type="primary"
        ):

            if notes_input.strip():

                st.session_state.notes = (
                    clean_text(notes_input)
                )

                st.success(
                    "Notes saved successfully!"
                )

            else:

                st.warning(
                    "Please enter some notes."
                )

    # --------------------------------------------------------
    # FILE UPLOAD
    # --------------------------------------------------------

    with tab2:

        uploaded_file = st.file_uploader(
            "Upload PDF, TXT or Markdown",
            type=[
                "pdf",
                "txt",
                "md"
            ]
        )

        if uploaded_file:

            if st.button(
                "📥 Import File",
                type="primary"
            ):

                text = read_uploaded_file(
                    uploaded_file
                )

                if text:

                    st.session_state.notes = text

                    st.success(
                        f"Imported "
                        f"{uploaded_file.name} successfully!"
                    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    if st.session_state.notes:

        st.divider()

        st.subheader(
            "Notes Preview"
        )

        preview = (
            st.session_state.notes
        )

        if len(preview) > 5000:

            preview = (
                preview[:5000]
                + "\n\n...more"
            )

        st.text_area(
            "Preview",
            value=preview,
            height=300,
            disabled=True
        )

        st.caption(
            f"{len(st.session_state.notes):,} "
            "characters"
        )


# ============================================================
# QUIZ GENERATOR PAGE
# ============================================================

elif st.session_state.active_page == "Quiz Generator":

    st.title(
        "🎯 Quiz Generator"
    )

    if not st.session_state.notes:

        st.info(
            "Please add notes first."
        )

        if st.button(
            "📝 Go to Notes"
        ):

            st.session_state.active_page = (
                "Notes"
            )

            st.rerun()

    elif not client:

        st.error(
            "Gemini API is not connected. "
            "Please check your .env file."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            question_count = st.selectbox(
                "Number of Questions",
                [
                    5,
                    10,
                    15,
                    20
                ]
            )

        with col2:

            difficulty = st.selectbox(
                "Difficulty",
                [
                    "Easy",
                    "Medium",
                    "Hard"
                ],
                index=1
            )

        if st.button(
            "✨ Generate Quiz",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Gemini is creating your quiz..."
            ):

                quiz = generate_quiz(
                    st.session_state.notes,
                    question_count,
                    difficulty
                )

            if quiz:

                st.session_state.quiz = quiz

                st.session_state.quiz_answers = {}

                st.session_state.quiz_submitted = False

                st.session_state.score = 0

                st.success(
                    f"Generated "
                    f"{len(quiz)} questions!"
                )

        # ----------------------------------------------------
        # DISPLAY QUIZ
        # ----------------------------------------------------

        if st.session_state.quiz:

            st.divider()

            st.subheader(
                "🧠 Your Quiz"
            )

            for index, question in enumerate(
                st.session_state.quiz
            ):

                st.markdown(
                    f"### Question {index + 1}"
                )

                st.write(
                    question["question"]
                )

                selected = st.radio(
                    "Choose an answer:",
                    question["options"],
                    key=f"quiz_{index}"
                )

                st.session_state.quiz_answers[
                    index
                ] = selected

                # Show result after submit
                if st.session_state.quiz_submitted:

                    if (
                        selected
                        == question["answer"]
                    ):

                        st.success(
                            "✅ Correct! "
                            + question["explanation"]
                        )

                    else:

                        st.error(
                            "❌ Incorrect."
                        )

                        st.info(
                            "Correct answer: "
                            + question["answer"]
                        )

                        st.caption(
                            question["explanation"]
                        )

                st.divider()

            # ------------------------------------------------
            # SUBMIT
            # ------------------------------------------------

            if not st.session_state.quiz_submitted:

                if st.button(
                    "✅ Submit Quiz",
                    type="primary",
                    use_container_width=True
                ):

                    score = 0

                    for index, question in enumerate(
                        st.session_state.quiz
                    ):

                        selected = (
                            st.session_state
                            .quiz_answers
                            .get(index)
                        )

                        if (
                            selected
                            == question["answer"]
                        ):

                            score += 1

                    st.session_state.score = (
                        score
                    )

                    st.session_state.quiz_submitted = (
                        True
                    )

                    st.rerun()

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            else:

                total = len(
                    st.session_state.quiz
                )

                score = (
                    st.session_state.score
                )

                percentage = (
                    score / total * 100
                    if total
                    else 0
                )

                st.divider()

                st.subheader(
                    "🏆 Quiz Result"
                )

                st.metric(
                    "Score",
                    f"{score}/{total}",
                    f"{percentage:.0f}%"
                )

                if percentage >= 80:

                    st.success(
                        "Excellent work! 🎉"
                    )

                elif percentage >= 60:

                    st.info(
                        "Good job! Keep practicing. 💪"
                    )

                else:

                    st.warning(
                        "Keep studying and try again! 📚"
                    )

                col1, col2 = st.columns(2)

                with col1:

                    st.download_button(
                        "⬇️ Download Quiz",

                        data=quiz_to_text(
                            st.session_state.quiz
                        ),

                        file_name=(
                            "studyai_quiz.txt"
                        ),

                        mime="text/plain",

                        use_container_width=True
                    )

                with col2:

                    if st.button(
                        "🔄 Try Again",
                        use_container_width=True
                    ):

                        st.session_state.quiz_answers = {}

                        st.session_state.quiz_submitted = False

                        st.session_state.score = 0

                        st.rerun()


# ============================================================
# FLASHCARDS PAGE
# ============================================================

elif st.session_state.active_page == "Flashcards":

    st.title(
        "🎴 Flashcards"
    )

    if not st.session_state.notes:

        st.info(
            "Please add notes first."
        )

        if st.button(
            "📝 Go to Notes"
        ):

            st.session_state.active_page = (
                "Notes"
            )

            st.rerun()

    elif not client:

        st.error(
            "Gemini API is not connected."
        )

    else:

        card_count = st.selectbox(
            "Number of Flashcards",
            [
                5,
                10,
                15,
                20
            ],
            index=1
        )

        if st.button(
            "✨ Generate Flashcards",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Gemini is creating flashcards..."
            ):

                cards = generate_flashcards(
                    st.session_state.notes,
                    card_count
                )

            if cards:

                st.session_state.flashcards = (
                    cards
                )

                st.session_state.flashcard_index = 0

                st.success(
                    f"Generated "
                    f"{len(cards)} flashcards!"
                )

        # ----------------------------------------------------
        # DISPLAY FLASHCARD
        # ----------------------------------------------------

        if st.session_state.flashcards:

            cards = (
                st.session_state.flashcards
            )

            total = len(cards)

            index = (
                st.session_state.flashcard_index
            )

            if index >= total:

                index = 0

                st.session_state.flashcard_index = 0

            card = cards[index]

            st.divider()

            st.caption(
                f"Card {index + 1} of {total}"
            )

            st.markdown(
                """
                <div class="flashcard">
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "### ❓ Question"
            )

            st.markdown(
                f"""
                <div class="flashcard-question">
                {card["question"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            with st.expander(
                "👁️ Reveal Answer"
            ):

                st.success(
                    card["answer"]
                )

            st.divider()

            col1, col2, col3 = st.columns(3)

            # Previous
            with col1:

                if st.button(
                    "← Previous",
                    disabled=(
                        index == 0
                    ),
                    use_container_width=True
                ):

                    st.session_state.flashcard_index -= 1

                    st.rerun()

            # Random
            with col2:

                if st.button(
                    "🔀 Random",
                    use_container_width=True
                ):

                    choices = [
                        i
                        for i in range(total)
                        if i != index
                    ]

                    if choices:

                        st.session_state.flashcard_index = (
                            random.choice(choices)
                        )

                    st.rerun()

            # Next
            with col3:

                if st.button(
                    "Next →",
                    disabled=(
                        index == total - 1
                    ),
                    use_container_width=True
                ):

                    st.session_state.flashcard_index += 1

                    st.rerun()

            st.download_button(
                "⬇️ Download Flashcards",

                data=flashcards_to_text(
                    cards
                ),

                file_name=(
                    "studyai_flashcards.txt"
                ),

                mime="text/plain",

                use_container_width=True
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧠 StudyAI | AI Notes to Quiz & "
    "Flashcard Generator | Built with "
    "Streamlit & Gemini"
)