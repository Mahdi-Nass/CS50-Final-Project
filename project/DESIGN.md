This Flask application is designed as a personal dashboard integrating several features like a Google Calendar view, to-do list, goal tracking, and motivational quotes. 

The application is built using Flask, python, html files, javascript, and css. Different features such as calendar, quotes, goals are organized into separate routes and functions to ensure code readability. Common operations, such as fetching quotes (fetch_quote), are saved as helper functions in functions.py. 
The libraries and functions to include are sorted in alphabetical order on the top of the app.py and functions.py

User information like username, password, and goals are stored in an SQLite database, (with the cs50 library).

Registration: User data is hashed using bcrypt for security and stored in the database.
Login: Verifies credentials against hashed passwords and initializes a session.
Session Management: A unique session is created for each user using Flask's session object and secured with a randomly generated key.

To do list tasks are dynamically added by the user and stored in the session rather than the table since these are likely to change session by session (a user wont be working on the same things every day).

API Choices
The dashboard displays personalized goals and quotes for motivation.
Google Calendar Integration:

Uses Google Calendar API to fetch and display events for the day.
OAuth 2.0 credentials are securely stored and refreshed when expired.
Timezone adjustments ensure accurate display across time zones.

Used an API for quotes so that the same quote isnt being used every time. Displays them on the dashboard and a separate /quote route.

Error Handling
Have different errors for things that could go wrong because of the user like incorrect password, passwords not matching, etc.
Handles database errors (e.g., duplicate usernames).
Catches and processes API-related exceptions (e.g., network issues, invalid credentials)
Ensures invalid inputs (e.g., empty goals) return appropriate feedback messages.
The modular design allows easy addition of features, such as more API integrations or expanding the to-do list.

Since this website is not public and approved by Google, I made it so the token.json file is only saved once and includes the information necessary to sync to one email at a time. Basically, any new username and password will use that json and will be synced to mahdinassereddine@college.harvard.edu.

HTMLs
All html files use layout.html and jinja that way the website can have a consistent uniform look.