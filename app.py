from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

# Secret key for session
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "ro-water-survey-secret-key"
)

DATABASE = "votes.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==========================================
# CREATE DATABASE AND TABLE
# ==========================================

def create_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# GET VOTE COUNTS
# ==========================================

def get_vote_counts():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT candidate, COUNT(*) AS total
        FROM votes
        GROUP BY candidate
    """)

    results = cursor.fetchall()

    connection.close()

    votes = {
        "Facing the problem (A)": 0,
        "Not facing the problem (B)": 0
    }

    for row in results:

        candidate = row["candidate"]
        total = row["total"]

        if candidate in votes:
            votes[candidate] = total

    return votes


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    votes = get_vote_counts()

    already_voted = session.get("already_voted", False)

    return render_template(
        "index.html",
        votes=votes,
        already_voted=already_voted
    )


# ==========================================
# SUBMIT VOTE
# ==========================================

@app.route("/vote", methods=["POST"])
def vote():

    # Prevent the same browser session
    # from voting more than once

    if session.get("already_voted", False):

        return redirect("/")


    # Get selected radio button

    candidate = request.form.get("candidate")


    # Allowed voting options

    valid_candidates = [
        "Facing the problem (A)",
        "Not facing the problem (B)"
    ]


    # Check whether a valid option was selected

    if candidate not in valid_candidates:

        return redirect("/")


    # Store vote in database

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO votes (candidate)
        VALUES (?)
        """,
        (candidate,)
    )

    connection.commit()

    connection.close()


    # Mark this browser as already voted

    session["already_voted"] = True


    # Show updated results

    return redirect("/")


# ==========================================
# DATABASE INITIALIZATION
# ==========================================
#
# IMPORTANT:
# This must be OUTSIDE the
# if __name__ == "__main__"
#
# because Render uses Gunicorn:
#
# gunicorn app:app
#
# Gunicorn does not execute the
# __main__ section.
# ==========================================

create_database()


# ==========================================
# RUN APPLICATION LOCALLY
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
