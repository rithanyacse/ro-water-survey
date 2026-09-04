import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "votes.db"
)


# =========================
# CREATE DATABASE
# =========================

def create_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Create database when Flask starts
create_database()


# =========================
# GET VOTE DATA
# =========================

def get_votes():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidate, COUNT(*)
        FROM votes
        GROUP BY candidate
    """)

    rows = cursor.fetchall()

    conn.close()

    votes = {
        "Facing the problem (A)": 0,
        "Not facing the problem (B)": 0
    }

    for candidate, count in rows:

        if candidate in votes:
            votes[candidate] = count

    return votes


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    votes = get_votes()

    total_votes = (
        votes["Facing the problem (A)"] +
        votes["Not facing the problem (B)"]
    )

    if total_votes > 0:

        percentages = {
            "Facing the problem (A)": round(
                votes["Facing the problem (A)"] / total_votes * 100,
                1
            ),

            "Not facing the problem (B)": round(
                votes["Not facing the problem (B)"] / total_votes * 100,
                1
            )
        }

    else:

        percentages = {
            "Facing the problem (A)": 0,
            "Not facing the problem (B)": 0
        }

    already_voted = request.cookies.get("has_voted") == "yes"

    return render_template(
        "index.html",
        percentages=percentages,
        already_voted=already_voted
    )


# =========================
# VOTE
# =========================

@app.route("/vote", methods=["POST"])
def vote():

    # Prevent another vote from same browser
    if request.cookies.get("has_voted") == "yes":
        return redirect(url_for("home"))

    candidate = request.form.get("candidate")

    valid_candidates = [
        "Facing the problem (A)",
        "Not facing the problem (B)"
    ]

    if candidate not in valid_candidates:
        return redirect(url_for("home"))

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes (candidate) VALUES (?)",
        (candidate,)
    )

    conn.commit()
    conn.close()

    # Remember that this browser has voted
    response = make_response(
        redirect(url_for("home"))
    )

    response.set_cookie(
        "has_voted",
        "yes",
        max_age=31536000,
        httponly=True,
        samesite="Lax"
    )

    return response


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False
    )
