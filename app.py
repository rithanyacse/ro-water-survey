import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database file
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "votes.db")

# Candidate options
CANDIDATES = [
    "Facing the problem (A)",
    "Not facing the problem (B)"
]


def create_database():
    """Create the votes table if it does not already exist."""
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


def get_votes():
    """Get vote counts for all candidates."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidate, COUNT(*)
        FROM votes
        GROUP BY candidate
    """)

    rows = cursor.fetchall()
    conn.close()

    # Start every candidate at 0
    votes = {
        candidate: 0
        for candidate in CANDIDATES
    }

    # Update with actual database values
    for candidate, count in rows:
        votes[candidate] = count

    return votes


@app.route("/")
def home():
    """Display voting page and current results."""
    create_database()

    votes = get_votes()

    return render_template(
        "index.html",
        votes=votes
    )


@app.route("/vote", methods=["POST"])
def vote():
    """Store a submitted vote."""
    candidate = request.form.get("candidate")

    # Only accept valid candidates
    if candidate not in CANDIDATES:
        return redirect(url_for("home"))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes (candidate) VALUES (?)",
        (candidate,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/results")
def results():
    """Display current voting results."""
    create_database()

    votes = get_votes()

    return render_template(
        "index.html",
        votes=votes
    )


@app.route("/health")
def health():
    """Simple health check for Render."""
    return "OK", 200


if __name__ == "__main__":
    create_database()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
