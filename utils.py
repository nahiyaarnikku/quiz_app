import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pdfplumber
import docx
from fpdf import FPDF
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_mongo_client():
    return MongoClient(os.getenv("MONGO_URI"))

def extract_text_from_file(file):
    ext = file.name.split(".")[-1].lower()
    if ext == "pdf":
        with pdfplumber.open(file) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    elif ext == "docx":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == "txt":
        return file.read().decode("utf-8")
    return None

def generate_mcqs(text, num_questions, num_options):
    prompt = f"Generate {num_questions} MCQs with {num_options} options each based on the text:\n{text}"
    response = genai.generate_content(prompt).text.strip()
    return parse_mcqs(response)

def parse_mcqs(mcq_text):
    mcqs = []
    for block in mcq_text.split("## MCQ")[1:]:
        lines = block.strip().split("\n")
        question = lines[0].replace("Question: ", "")
        options = lines[1:-1]
        correct_answer = lines[-1].replace("Correct Answer: ", "")
        mcqs.append({"question": question, "options": options, "correct_answer": correct_answer})
    return mcqs

def create_shareable_link(quiz_id):
    return f"http://localhost:8501/?quiz_id={quiz_id}"
