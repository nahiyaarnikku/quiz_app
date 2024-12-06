# student.py
import streamlit as st
from utils import get_mongo_client, generate_student_result_pdf
from bson.objectid import ObjectId

def student_panel():
    st.title("Student Panel")
    mongo_client = get_mongo_client()
    db = mongo_client.quiz_app

    # Access quiz
    quiz_id = st.text_input("Enter Quiz ID (provided by admin)")
    if st.button("Start Quiz"):
        quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        if quiz:
            st.session_state.quiz = quiz
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answers = []
        else:
            st.error("Invalid Quiz ID")

    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        current_question = st.session_state.current_question

        if current_question < len(quiz["mcqs"]):
            mcq = quiz["mcqs"][current_question]
            st.write(f"Question {current_question + 1}: {mcq['question']}")
            answer = st.radio("Options:", mcq["options"], key=f"q_{current_question}")

            if st.button("Next"):
                st.session_state.answers.append(answer)
                if answer == mcq["correct_answer"]:
                    st.session_state.score += 1
                st.session_state.current_question += 1
        else:
            st.success(f"Quiz Completed! Your Score: {st.session_state.score}/{len(quiz['mcqs'])}")
            
            # Collect student details
            student_name = st.text_input("Enter your name", key="student_name")
            student_email = st.text_input("Enter your email", key="student_email")
            student_age = st.number_input("Enter your age", min_value=1, max_value=120, key="student_age")
            
            if st.button("Submit Results"):
                if not student_name or not student_email or not student_age:
                    st.error("Please fill in all the details before submitting.")
                else:
                    db.results.insert_one({
                        "student_name": student_name,
                        "student_email": student_email,
                        "student_age": student_age,
                        "admin_id": quiz["admin_id"],
                        "quiz_id": quiz["_id"],
                        "score": st.session_state.score,
                        "mcqs": quiz["mcqs"],
                        "answers": st.session_state.answers
                    })
                    st.success("Results submitted successfully!")

                    # Generate and offer download of result PDF
                    result_pdf = generate_student_result_pdf(student_name, st.session_state.score, len(quiz["mcqs"]))
                    st.download_button(
                        label="Download Result as PDF",
                        data=result_pdf,
                        file_name=f"{student_name}_quiz_result.pdf",
                        mime="application/pdf"
                    )

                    # Clear session state to prevent resubmission
                    for key in ['quiz', 'current_question', 'score', 'answers']:
                        if key in st.session_state:
                            del st.session_state[key]

    # Prevent leaving the page without submitting
    if 'quiz' in st.session_state and st.session_state.current_question == len(st.session_state.quiz["mcqs"]):
        st.warning("Please submit your results before leaving the page.")
