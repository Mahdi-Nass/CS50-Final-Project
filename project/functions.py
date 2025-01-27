from cs50 import SQL
from dateutil import parser
from flask import Flask, flash, redirect, render_template, request, session, url_for
from functions import *

import bcrypt
import datetime
import os
import os.path
import pytz
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

db = SQL("sqlite:///dashboard.db")
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def error(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def fetch_calendar_events(user_id):
    """Fetch events from Google Calendar for the current day."""
    try:
        # Retrieve user's credentials from the database
        user = db.execute("SELECT google_token, google_refresh_token FROM user WHERE id = ?", user_id)
        if not user:
            return []

        google_token = user[0]["google_token"]
        google_refresh_token = user[0]["google_refresh_token"]

        # Initialize credentials
        creds = None
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update token in the database after refresh
            db.execute("UPDATE user SET google_token = ?, google_refresh_token = ? WHERE id = ?",
                       creds.token, creds.refresh_token, user_id)

        tz = pytz.timezone('US/Eastern')
        today_start = datetime.datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59, microsecond=0)
        today_start = today_start.astimezone(pytz.utc)
        today_end = today_end.astimezone(pytz.utc)

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)
        events_result = service.events().list(
            calendarId="primary",
            timeMin=today_start.isoformat(),
            timeMax=today_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        event_details = []

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            event_details.append({
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": end
            })

        for event in event_details:
            start_dt = parser.parse(event['start'])
            end_dt = parser.parse(event['end'])

            # Format start and end into date and time
            event['start_date'] = start_dt.strftime('%Y-%m-%d')
            event['start_time'] = start_dt.strftime('%I:%M %p')

            event['end_date'] = end_dt.strftime('%Y-%m-%d')
            event['end_time'] = end_dt.strftime('%I:%M %p')

        return event_details

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def fetch_quote():
    # API Endpoint
    url = "http://api.forismatic.com/api/1.0/"
    params = {
        "method": "getQuote",  # API method
        "format": "json",     # Response format
        "lang": "en"          # Language
    }

    try:
        # Send GET request to the API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()      # Parse JSON response

        # Extract quote data
        return {
            "text": data.get("quoteText", "No quote found."),
            "author": data.get("quoteAuthor", "Unknown")
        }
    except requests.RequestException as e:
        return {"text": "Error fetching quote.", "author": str(e)}
