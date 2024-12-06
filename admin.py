import streamlit as st
from utils import get_mongo_client, extract_text_from_file, generate_mcqs, create_shareable_link
from bson.objectid import ObjectId
import json

def admin_panel():
    st.title("Admin Panel")
    mongo_client = get_mongo_client()
    db = mongo_client.quiz_app
    quizzes_collection = db.quizzes

    # Login/Register
    auth_option = st.radio("Login or Register as Admin:", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if auth_option == "Register":
            db.admins.insert_one({"username": username, "password": password})
            st.success("Registered successfully!")
        elif auth_option == "Login":
            admin = db.admins.find_one({"username": username, "password": password})
            if admin:
                st.success("Logged in successfully!")
                st.session_state.admin_logged_in = True
                st.session_state.admin_id = admin["_id"]
            else:
                st.error("Invalid credentials")

    if st.session_state.get("admin_logged_in"):
        st.header(f"Welcome, {username}!")

        # Upload File
        uploaded_file = st.file_uploader("Upload Document (PDF/TXT/DOCX)")
        num_questions = st.number_input("Number of Questions", min_value=1, step=1)
        num_options = st.number_input("Number of Options per Question", min_value=2, max_value=6)

        if uploaded_file and st.button("Generate Quiz"):
            text = extract_text_from_file(uploaded_file)
            mcqs = generate_mcqs(text, num_questions, num_options)
            st.session_state.mcqs = mcqs
            quiz_id = quizzes_collection.insert_one({"admin_id": st.session_state.admin_id, "mcqs": mcqs}).inserted_id
            link = create_shareable_link(quiz_id)
            st.success(f"Quiz created successfully! Share this link: {link}")

        # View Quiz Results
        st.subheader("Quiz Results")
        results = db.results.find({"admin_id": st.session_state.admin_id})
        for result in results:
            st.write(f"Student: {result['student_name']} | Score: {result['score']}/{len(result['mcqs'])}")

        if st.button("Logout"):
            st.session_state.admin_logged_in = False
