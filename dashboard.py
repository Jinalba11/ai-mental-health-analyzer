import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API = "http://127.0.0.1:5000"

st.title("🧠 Mental Health Emotion Analyzer")

# Input
text = st.text_area("Enter your thoughts")

if st.button("Analyze"):
    if text.strip():
        res = requests.post(f"{API}/predict", json={"text": text})
        if res.ok:
            st.success(f"Predicted Emotion: {res.json()['emotion']}")
        else:
            st.error("Prediction failed")
    else:
        st.warning("Please enter some text")

st.divider()

# Clear Button
if st.button("🗑️ Clear History"):
    res = requests.delete(f"{API}/clear")
    if res.ok:
        st.success("History cleared")
    else:
        st.error("Failed to clear")

# History
st.subheader("📜 History")

if st.button("Load History"):
    res = requests.get(f"{API}/history")

    if res.ok:
        data = res.json()

        if data:
            df = pd.DataFrame(data)

            st.dataframe(df)

            st.subheader("📊 Emotion Distribution")

            counts = df['emotion'].value_counts()

            st.bar_chart(counts)

            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
            ax.set_title("Emotion Share")
            st.pyplot(fig)

        else:
            st.info("No data yet")

    else:
        st.error("Error loading history")