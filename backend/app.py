from flask import Flask, request, jsonify
import pickle
import re
import nltk
import os
import psycopg2
import atexit

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required nltk data
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)

# Dynamic path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(base_dir, 'models', 'model.pkl')
vectorizer_path = os.path.join(base_dir, 'models', 'vectorizer.pkl')

model = pickle.load(open(model_path, 'rb'))
vectorizer = pickle.load(open(vectorizer_path, 'rb'))

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="mental_health_db",
    user="postgres",
    password="Jinalba@2811"
)
cursor = conn.cursor()

# NLP preprocessing
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return " ".join(words)

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']

    cleaned = clean_text(text)
    vectorized = vectorizer.transform([cleaned])
    prediction = model.predict(vectorized)[0]

    cursor.execute(
        "INSERT INTO entries (text, emotion) VALUES (%s, %s)",
        (text, prediction)
    )
    conn.commit()

    return jsonify({'emotion': prediction})

# ---------------- HISTORY ----------------
@app.route('/history', methods=['GET'])
def history():
    cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "text": row[1],
            "emotion": row[2],
            "created_at": row[3]
        })

    return jsonify(data)

# ---------------- CLEAR HISTORY ----------------
@app.route('/clear', methods=['DELETE'])
def clear():
    cursor.execute("DELETE FROM entries")
    conn.commit()
    return jsonify({"message": "History cleared successfully"})

# Home
@app.route('/')
def home():
    return "API is running 🚀"

# Close DB
def close_connection():
    cursor.close()
    conn.close()

atexit.register(close_connection)

# Run
if __name__ == '__main__':
    app.run(debug=True)