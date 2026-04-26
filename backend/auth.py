from flask import request, jsonify
from backend.db import get_connection

def register():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (data["username"], data["password"])
        )
        conn.commit()
        return jsonify({"message": "User created"})
    except:
        conn.rollback()
        return jsonify({"error": "User exists"})