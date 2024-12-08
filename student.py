import streamlit as st
from utils import get_mongo_client, generate_student_result_pdf, parse_mcqs
from bson.objectid import ObjectId

def student_panel():
    st.title("Student Panel")
    mongo_client = get_mongo_client()
    db = mongo_client.quiz_app

    quiz_id = st.text_input("Enter Quiz ID (provided by admin)")
    if st.button("Start Quiz"):
        quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id)})
        if quiz:
            st.session_state.quiz = quiz
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.quiz_generated = True
            st.session_state.mcqs = parse_mcqs(quiz["mcqs"])
        else:
            st.error("Invalid Quiz ID")

    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        current_question = st.session_state.current_question

        if current_question < len(st.session_state.mcqs):
            mcq = st.session_state.mcqs[current_question]
            st.write(f"Question {current_question + 1}: " ,mcq['question'].lstrip('0123456789. '));
            #st.write(mcq['question'])
            
            options = mcq["options"]
            answer = st.radio("Select your answer:", options, key=f"q_{current_question}")

            if st.button("Next"):
                st.session_state.answers.append(answer)
                st.session_state.current_question += 1
                st.rerun()
        else:
            st.session_state.score = sum(
                1 for user_ans, mcq in zip(st.session_state.answers, st.session_state.mcqs)
                if user_ans.split(")")[0].strip() == mcq["correct_answer"].split(")")[0].strip()
            )
            
            st.success(f"Quiz Completed!")
            
            student_name = st.text_input("Enter your name", key="student_name")
            student_roll = st.number_input("Enter your Roll no.", min_value=1, key="student_roll")
            
            if st.button("Submit Results"):
                if not student_name or not student_roll:
                    st.error("Please fill in all the details before submitting.")
                else:
                    db.results.insert_one({
                        "student_name": student_name,
                        "student_roll": student_roll,
                        "admin_id": quiz["admin_id"],
                        "quiz_id": quiz["_id"],
                        "score": st.session_state.score,
                        "mcqs": st.session_state.mcqs,
                        "answers": st.session_state.answers
                    })
                    st.success("Results submitted successfully!")
                    st.success(f"Your Score: {st.session_state.score}/{len(st.session_state.mcqs)}")
                    result_pdf = generate_student_result_pdf(student_name, st.session_state.score, len(st.session_state.mcqs))
                    st.download_button(
                        label="Download Result as PDF",
                        data=result_pdf,
                        file_name=f"{student_name}_quiz_result.pdf",
                        mime="application/pdf"
                    )

                    for key in ['quiz', 'current_question', 'score', 'answers', 'mcqs', 'quiz_generated']:
                        if key in st.session_state:
                            del st.session_state[key]

    if 'quiz' in st.session_state and st.session_state.current_question == len(st.session_state.mcqs):
        st.warning("Please submit your results before leaving the page.")

