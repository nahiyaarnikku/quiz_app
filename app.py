import streamlit as st
from admin import admin_panel
from student import student_panel

# Streamlit configuration
st.set_page_config(page_title="MCQ Quiz Platform", layout="centered")

# Main page navigation
st.sidebar.title("MCQ Quiz Platform")
option = st.sidebar.radio("Go to:", ["Admin Panel", "Student Panel"])

if option == "Admin Panel":
    admin_panel()
elif option == "Student Panel":
    student_panel()
