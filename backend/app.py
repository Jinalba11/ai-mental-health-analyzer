from flask import Flask, request, jsonify
import pickle, os
from backend.db import get_connection

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = pickle.load(open(os.path.join(BASE_DIR, 'models/model.pkl'), 'rb'))
vectorizer = pickle.load(open(os.path.join(BASE_DIR, 'models/vectorizer.pkl'), 'rb'))

suggestions = {
    "sadness": "Try talking to a friend 💬",
    "anger": "Take a deep breath 🧘",
    "joy": "Keep smiling 😊",
    "fear": "You are safe 💙",
    "love": "Spread kindness ❤️",
    "surprise": "Take it easy 😮"
}

@app.route('/')
def home():
    return "Backend running 🚀"


# LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username=%s AND password=%s",
                (data["username"], data["password"]))

    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"user_id": user[0]})
    return jsonify({"error": "Invalid credentials"})


# REGISTER
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s,%s)",
                    (data["username"], data["password"]))
        conn.commit()
        return jsonify({"message": "User created"})
    except:
        conn.rollback()
        return jsonify({"error": "User exists"})


# PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    text = data.get("text")
    user_id = data.get("user_id")

    if not text or not user_id:
        return jsonify({"error": "Missing data"})

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0].max()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO entries (user_id, text, emotion) VALUES (%s,%s,%s)",
        (user_id, text, pred)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "emotion": pred,
        "confidence": round(prob * 100, 2),
        "suggestion": suggestions.get(pred, "")
    })


# ANALYTICS (🔥 FIXED)
@app.route('/analytics', methods=['GET'])
def analytics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT emotion, created_at FROM entries ORDER BY created_at")

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"emotion": r[0], "time": r[1].isoformat()}
        for r in rows
    ])


if __name__ == "__main__":
    app.run(debug=True)