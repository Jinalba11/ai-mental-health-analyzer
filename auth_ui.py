import streamlit as st
import requests

API = "http://127.0.0.1:5000"

def login_ui():

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # LOGIN
    with col1:
        if st.button("Login"):
            try:
                res = requests.post(f"{API}/login", json={
                    "username": username,
                    "password": password
                })

                data = res.json()

                if "user_id" in data:
                    st.session_state.user_id = data["user_id"]
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error(data.get("error", "Login failed"))

            except:
                st.error("Backend not running")

    # REGISTER
    with col2:
        if st.button("Register"):
            try:
                res = requests.post(f"{API}/register", json={
                    "username": username,
                    "password": password
                })

                data = res.json()
                st.success(data.get("message", "Registered"))

            except:
                st.error("Backend not running")