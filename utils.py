# utils.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pdfplumber
import docx
from fpdf import FPDF
import google.generativeai as genai
from docx import Document
from docx.shared import Inches

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

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
    prompt = f"""
        Generate {num_questions} multiple-choice questions (MCQs) based on the following text. Each MCQ should have {num_options} options.

        Text: {text}

        Please follow this format for each MCQ:

        ## MCQ
        Question: [Write the question here]
        A. [First option]
        B. [Second option]
        C. [Third option]
        ...etc
        Correct Answer: [Write the letter of the correct option]

        Ensure that:
        1. Questions are clear and directly related to the text.
        2. All options are plausible, but only one is correct.
        3. The correct answer is clearly indicated.
        4. The order of options (A, B, ....) is used consistently.

        Begin generating the MCQs now:
        """
    response = model.generate_content(prompt).text.strip()
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

def generate_pdf(mcqs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for i, mcq in enumerate(mcqs, 1):
        pdf.cell(200, 10, txt=f"Question {i}: {mcq['question']}", ln=1)
        for option in mcq['options']:
            pdf.cell(200, 10, txt=f"- {option}", ln=1)
        pdf.cell(200, 10, txt=f"Correct Answer: {mcq['correct_answer']}", ln=1)
        pdf.cell(200, 10, txt="", ln=1)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_docx(mcqs):
    doc = Document()
    
    for i, mcq in enumerate(mcqs, 1):
        doc.add_paragraph(f"Question {i}: {mcq['question']}")
        for option in mcq['options']:
            doc.add_paragraph(f"- {option}")
        doc.add_paragraph(f"Correct Answer: {mcq['correct_answer']}")
        doc.add_paragraph()
    
    return doc

def generate_student_result_pdf(student_name, score, total_questions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Student Name: {student_name}", ln=1)
    pdf.cell(200, 10, txt=f"Score: {score}/{total_questions}", ln=1)
    
    return pdf.output(dest='S').encode('latin-1')