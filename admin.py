import streamlit as st
from utils import get_mongo_client, save_quiz_to_db, download_quiz, extract_text_from_file
import json

def admin_panel():
    st.title("Admin Panel")

    # Upload File
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])
    if uploaded_file:
        try:
            text = extract_text_from_file(uploaded_file)  # This line will now work properly
            st.text_area("Extracted Text", value=text, height=200)

            num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
            num_options = st.number_input("Number of Options per Question", min_value=2, max_value=5, value=4)

            if st.button("Generate Quiz"):
                try:
                    mcqs = generate_mcqs(text, num_questions, num_options)
                    quiz_data = {
                        "mcqs": mcqs,
                        "admin_id": "admin123",  # Replace with the actual admin ID
                    }
                    quiz_id = save_quiz_to_db(quiz_data)
                    st.success(f"Quiz generated and saved. Shareable link: http://localhost:8501/?quiz_id={quiz_id}")
                    st.session_state.quiz_id = quiz_id

                    # Provide download option for the admin
                    if st.button("Download Quiz PDF"):
                        file_path = download_quiz(quiz_id)
                        with open(file_path, "rb") as file:
                            st.download_button("Download PDF", file, file_name=f"quiz_{quiz_id}.pdf")
                except Exception as e:
                    st.error(f"Error generating quiz: {e}")
        except ValueError as e:
            st.error(f"Error extracting text: {e}")
