from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def get_user():
    uid = request.args.get("id")
    conn = sqlite3.connect("app.db")
    row = conn.execute("SELECT * FROM users WHERE id = " + uid).fetchone()
    return {"user": row}
