from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

# Secret key for session
app.secret_key = "ro_water_survey_secret_key"


# ==============================
# CREATE DATABASE
# ==============================

def create_database():

    connection = sqlite3.connect("votes.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():

    connection = sqlite3.connect("votes.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT candidate, COUNT(*)
        FROM votes
        GROUP BY candidate
    """)

    results = cursor.fetchall()

    connection.close()


    # Default vote counts

    votes = {
        "Facing the problem (A)": 0,
        "Not facing the problem (B)": 0
    }


    # Update counts from database

    for candidate, count in results:

        if candidate in votes:

            votes[candidate] = count


    # Check whether this browser has already voted

    already_voted = session.get("already_voted", False)


    return render_template(
        "index.html",
        votes=votes,
        already_voted=already_voted
    )


# ==============================
# VOTING
# ==============================

@app.route("/vote", methods=["POST"])
def vote():

    # Prevent the same browser from voting again

    if session.get("already_voted", False):

        return redirect("/")


    # Get selected option

    candidate = request.form.get("candidate")


    # Check valid option

    valid_candidates = [

        "Facing the problem (A)",

        "Not facing the problem (B)"

    ]


    if candidate not in valid_candidates:

        return redirect("/")


    # Store vote

    connection = sqlite3.connect("votes.db")

    cursor = connection.cursor()


    cursor.execute(
        "INSERT INTO votes (candidate) VALUES (?)",
        (candidate,)
    )


    connection.commit()

    connection.close()


    # Mark this browser as already voted

    session["already_voted"] = True


    return redirect("/")


# ==============================
# RUN FLASK
# ==============================

if __name__ == "__main__":

    create_database()

    app.run(

        host="0.0.0.0",

        port=int(os.environ.get("PORT", 5000)),

        debug=False

    )