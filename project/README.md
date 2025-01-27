This project is a personalized dashboard that displays a user's daily information, such as the current time, a motivational quote, their set goal,
upcoming events, and a to-do list that they make. The dashboard is built using Flask for the backend, HTML for the structure, and CSS/Bootstrap for styling.

To Use:

Install Required Dependencies:
Ensure Python, flask, and the google calendar API libraries on the Google Cloud website are all installed.

Delete the token.json that's currently included. This makes it only work for mahdinassereddine@college.harvard.edu. Since this program isn't public,
it can only work for my harvard email, my personal email, and your (sammi's) harvard email. When you delete the token.json, a new one will automatically
be created that will work for your email (once you register on the website and try to sync your college email). Again, this will only work for the three
emails I listed previously. I cannot make it work for all emails unless I make the website public and approved by Google.

By default, the application will run locally at http://127.0.0.1:5000.

Once the application is running, open the provided URL in your browser. The dashboard is divided into several sections which can be accessed using the
nav bar on the top of the page

Current Time:
The current time is displayed in real-time in the top-right corner of the main webpage. This time updates every second and is formatted in a 12-hour AM/PM style. No additional configuration is needed for this feature.

Welcome Section and Motivational Quote:
At the top of the page, the user's name is displayed alongside a motivational quote. The quote changes upon each visit.

Your Goal Section:
This section displays the user's current goal. This goal is stored in the user table and will be remembered upon each login. If no goal is set, the message "No goal set yet." is shown, and the "goals" button on the navbar allows the user to navigate to a page where they can set their goal (they can keep this goal for the semester, day, year, etc).

Today's Events:

This section shows the events scheduled for the current day using the gcal API. If no events are scheduled, a placeholder message will notify the user.
Events are displayed in a card format for a clean and organized look.

To-Do List:

Users can add tasks to a simple to-do list by typing them into the input field and clicking "Add Task."
Tasks are displayed as a list with checkboxes to mark them as completed. The list resets on page reload, as the tasks are not yet persisted.

File Structure:
The project files are organized as follows:

app.py: Main Flask application file.
functions.py helper functions

templates/: Contains the HTML templates:
layout.html (base layout)
index.html (dashboard page)
apology.html (for errors)
calendar.html
goals.html
login.html
register.html
quote.html

static/: Contains CSS and JavaScript files for styling and interactivity.
requirements.txt: List of all Python dependencies.
