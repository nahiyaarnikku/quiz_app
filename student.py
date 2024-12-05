import streamlit as st
from utils import get_mongo_client
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
        else:
            st.error("Invalid Quiz ID")

    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        current_question = st.session_state.current_question

        if current_question < len(quiz["mcqs"]):
            mcq = quiz["mcqs"][current_question]
            st.markdown(f"**Question {current_question + 1}:** {mcq['question']}")
            answer = st.radio("Options:", mcq["options"])

            if st.button("Next"):
                if answer == mcq["correct_answer"]:
                    st.session_state.score += 1
                st.session_state.current_question += 1
        else:
            st.success(f"Quiz Completed! Your Score: {st.session_state.score}/{len(quiz['mcqs'])}")
            student_name = st.text_input("Enter your name")
            if st.button("Submit Results"):
                db.results.insert_one({
                    "student_name": student_name,
                    "quiz_id": quiz["_id"],
                    "score": st.session_state.score,
                    "mcqs": quiz["mcqs"],
                })
                st.success("Results submitted successfully!")
