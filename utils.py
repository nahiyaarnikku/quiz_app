import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pdfplumber
import docx
from fpdf import FPDF
import google.generativeai as genai
from bson.objectid import ObjectId
import json

# Load environment variables
load_dotenv()

# API Key for Generative AI
API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not API_KEY or not MONGO_URI:
    raise ValueError("Environment variables GOOGLE_API_KEY or MONGO_URI are not set.")

# Configure Generative AI API
genai.configure(api_key=API_KEY)

def get_mongo_client():
    """
    Returns a MongoDB client connected to the URI defined in the environment variables.
    """
    if not MONGO_URI:
        raise ValueError("MongoDB URI is not set in the environment variables.")
    return MongoClient(MONGO_URI)

def extract_text_from_file(file):
    """
    Extracts text from the provided file based on its extension (PDF, DOCX, or TXT).
    """
    ext = file.name.split(".")[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(file) as pdf:
                return "".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif ext == "docx":
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif ext == "txt":
            return file.read().decode("utf-8")
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Supported formats: pdf, docx, txt.")
    except Exception as e:
        raise ValueError(f"Error extracting text from {file.name}: {e}")

def generate_mcqs(text, num_questions, num_options):
    """
    Generates multiple-choice questions based on the provided text using Google Generative AI.
    """
    prompt = f"Generate {num_questions} MCQs with {num_options} options each based on the following text:\n{text}"
    try:
        response = genai.generate_text(prompt)  # Ensure using Google Generative AI's 'generate_text'
        if not response or not response.text:
            raise ValueError("Received empty response from AI model.")
        return parse_mcqs(response.text.strip())
    except Exception as e:
        raise ValueError(f"Error generating MCQs: {e}")

def parse_mcqs(mcq_text):
    """
    Parses the generated MCQs into a structured format.
    """
    mcqs = []
    try:
        for block in mcq_text.split("## MCQ")[1:]:
            lines = block.strip().split("\n")
            question = lines[0].replace("Question: ", "")
            options = [line.strip() for line in lines[1:-1]]
            correct_answer = lines[-1].replace("Correct Answer: ", "").strip()
            mcqs.append({"question": question, "options": options, "correct_answer": correct_answer})
    except Exception as e:
        raise ValueError(f"Error parsing MCQs: {e}")
    return mcqs

def save_quiz_to_db(quiz_data):
    """
    Saves the quiz data to the MongoDB database.
    """
    try:
        mongo_client = get_mongo_client()
        db = mongo_client.quiz_app
        result = db.quizzes.insert_one(quiz_data)
        return result.inserted_id
    except Exception as e:
        raise ValueError(f"Error saving quiz to database: {e}")

def download_quiz(quiz_id):
    """
    Generates a PDF of the quiz to be downloaded by the admin.
    """
    mongo_client = get_mongo_client()
    db = mongo_client.quiz_app
    quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        raise ValueError("Quiz not found")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Generated Quiz", ln=True, align='C')

    # Questions and Options
    for i, mcq in enumerate(quiz["mcqs"], 1):
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Q{i}: {mcq['question']}")
        for j, option in enumerate(mcq["options"], 1):
            pdf.multi_cell(0, 10, f"  {chr(64 + j)}) {option}")

    # Save the PDF to a file
    pdf_output_path = f"quiz_{quiz_id}.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path
