import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:5000"

st.set_page_config(page_title="Emotion AI", layout="wide")

# 🌗 THEME
dark = st.toggle("🌙 Dark Mode")

# SESSION
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# LOGIN
if not st.session_state.user_id:
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API}/login", json={"username": user, "password": pwd})
        data = res.json()

        if "user_id" in data:
            st.session_state.user_id = data["user_id"]
            st.success("Logged in")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Register"):
        requests.post(f"{API}/register", json={"username": user, "password": pwd})
        st.success("Registered")

    st.stop()


# 💬 CHAT UI
st.title("🧠 Emotion Intelligence System")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("How are you feeling?")

if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

    res = requests.post(f"{API}/predict", json={
        "text": prompt,
        "user_id": st.session_state.user_id
    })

    data = res.json()

    if "error" in data:
        reply = data["error"]
    else:
        reply = f"""
**Emotion:** {data['emotion']}  
**Confidence:** {data['confidence']}%  
💡 {data['suggestion']}
"""

    st.session_state.chat.append({"role": "assistant", "content": reply})
    st.rerun()


# 📊 ANALYTICS
st.divider()
st.subheader("📊 Analytics")

res = requests.get(f"{API}/analytics")
data = res.json()

if data:
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])

    # LINE CHART
    st.line_chart(
        df.groupby([pd.Grouper(key="time", freq="D"), "emotion"])
        .size().unstack().fillna(0)
    )

    # WEEKLY
    st.subheader("📅 Weekly Trends")
    st.area_chart(
        df.groupby([pd.Grouper(key="time", freq="W"), "emotion"])
        .size().unstack().fillna(0)
    )

    # CSV
    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        "history.csv"
    )
else:
    st.info("No data yet")