from cs50 import SQL
from dateutil import parser
from flask import Flask, flash, redirect, render_template, request, session, url_for
from functions import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import bcrypt
import datetime
import os
import os.path
import pytz
import requests

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

app = Flask(__name__)
app.secret_key = os.urandom(24)
db = SQL("sqlite:///dashboard.db")

@app.route("/", methods=["GET", "POST"])
def home():
    """Displays the main dashboard with calendar events, quote of the day, user's goal, and to-do list."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch the quote of the day
    quote = fetch_quote()

    # Fetch user's goal and username from the database
    rows = db.execute("SELECT goal, username FROM user WHERE id = ?", session["user_id"])
    current_goal = rows[0]["goal"] if rows else "No goal set yet."
    username = rows[0]["username"] if rows else "Guest"

    # Handle to-do list form submission
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            # Store the task (for simplicity, storing it in the session)
            if 'tasks' not in session:
                session['tasks'] = []
            session['tasks'].append(task)
            session.modified = True

    # Fetch the user's calendar events
    event_details = fetch_calendar_events(session["user_id"])

    # Render the dashboard with to-do list data
    return render_template(
        "index.html",
        quote=quote,
        current_goal=current_goal,
        events=event_details,
        username=username,
        tasks=session.get('tasks', [])  # Pass tasks to the template
    )

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return error("missing username")
        elif not request.form.get("password"):
            return error("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return error("passwords don't match")
        password = request.form.get("password")  # Define the password variable here

        # Add user to database
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            id = db.execute("INSERT INTO user (username, hash) VALUES(?, ?)",
                            request.form.get("username"),
                            hashed_password)
        except ValueError:
            return error("username taken")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM user WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not bcrypt.checkpw(request.form.get("password").encode('utf-8'), rows[0]["hash"]):
            return error("invalid username and or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        if not rows[0]["google_token"]:
            # If no Google token, start OAuth flow to get refresh token
            refresh_token = get_refresh_token()
            
            # Store the refresh token in the database
            db.execute("UPDATE user SET google_refresh_token = ? WHERE id = ?",
                       refresh_token, session["user_id"])

            print("Refresh Token:", refresh_token)  # Debugging print statement

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/calendar")
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    event_details = fetch_calendar_events(session["user_id"])

    return render_template("calendar.html", events=event_details)

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote")
def index():
    # Fetch a quote
    quote = fetch_quote()
    
    # Render the quote on an HTML page
    return render_template("quote.html", quote=quote)

@app.route("/goals", methods=["GET", "POST"])
def goals():
    if request.method == "POST":
        # Get the submitted goal
        goal = request.form.get("goal")

        if not goal:
            return error("Goal cannot be empty", 400)

        # Update the database with the user's goal
        db.execute(
            "UPDATE user SET goal = ? WHERE id = ?",
            goal,
            session["user_id"]
        )

        # Flash a success message
        flash("Goal added successfully!")
        return redirect("/goals")

    # Retrieve the current goal for the user
    rows = db.execute("SELECT goal FROM user WHERE id = ?", session["user_id"])
    current_goal = rows[0]["goal"] if rows else None

    return render_template("goals.html", current_goal=current_goal)

if __name__ == "__main__":
    app.run(debug=True)
