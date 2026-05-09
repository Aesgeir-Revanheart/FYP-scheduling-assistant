````md
# AI Scheduling Assistant (FYP)

## Overview

This project is a semi-automated scheduling assistant that processes email queries and checks calendar availability using Gmail and Google Calendar integration.

The system is capable of:
- Reading scheduling-related email requests
- Interpreting time constraints such as:
  - “Are you free after 3pm?”
  - “Are you free before 6pm?”
  - “Are you free at 10pm?”
- Checking busy and available time slots from the user’s calendar
- Displaying free slot suggestions based on computed availability

The current implementation focuses on rule-based scheduling automation and availability checking.

---

# Features

- Gmail integration
- Google Calendar integration
- Rule-based query parsing
- Time constraint interpretation
- Free slot computation
- Busy interval detection
- Interval-based scheduling logic

---

# Requirements

## Step 1

Python is required to run this project.

If Python is not already installed on your system, you can download the latest version here:

https://www.python.org/downloads/
---

## Step 2

Clone the repository using Git or download the ZIP file from GitHub.

---

## Step 3

Install the required Google API libraries if they are not already installed:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

---

# Google API Setup

This project requires Google OAuth credentials in order to access Gmail and Google Calendar APIs.

The following files are intentionally excluded from the repository for security reasons:
- client_secret.json
- client_secret_gmail.json
- token.json
- token_gmail.json

These files contain authentication credentials and generated access tokens tied to the developer’s Google account.

---

## Step 1 — Create a Google Cloud Project

1. Go to:

https://console.cloud.google.com/

2. Sign in with your Google account.

3. At the top of the page, click the project selection dropdown.

4. Click:
   New Project

5. Enter a project name.

6. Click:
   Create

---

## Step 2 — Enable Gmail API and Google Calendar API

1. Inside the Google Cloud project, use the left sidebar and go to:

    APIs & Services -> Library

2. Search for:
    Gmail API

3. Open it and click:
    Enable

4. Return to the API Library.

5. Search for:
    Google Calendar API

6. Open it and click:
    Enable

---

## Step 3 — Configure OAuth Consent Screen

1. In the left sidebar, go to:

    APIs & Services → OAuth consent screen

2. Choose:
    External

3. Click:
    Create

4. Fill in the required fields such as:
   - App name
   - User support email
   - Developer contact email

5. Continue through the setup pages.

6. Save the configuration.

---

## Step 4 — Create OAuth Desktop Credentials

1. In the left sidebar, go to:

    APIs & Services → Credentials

2. Click:
    Create Credentials

3. Select:
    OAuth client ID

4. For Application Type, select:
    Desktop App

5. Enter a name for the OAuth client.

6. Click:
    Create

7. Download the generated OAuth JSON file.

8. Rename the downloaded file to:
    client_secret.json

9. Place the file inside the project root directory.

---

## Step 5 — Install Required Libraries

Install the required Python libraries using:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

---

## Step 6 — Run the Project

You may first try running the project using:

```bash
python main.py
```

If this does not work due to the project structure, run:

```bash
python src/main.py
```

---

## Step 7 — First-Time Authentication

When running the application for the first time:

- A browser window will open
- Google authentication will be requested
- Sign in with the Google account you wish to use
- Grant Gmail and Calendar access permissions

After successful login:
- token.json
- token_gmail.json

will be generated automatically.

---

## Missing Credential Files

If the OAuth credential files are missing, the application will display an authentication setup error message during startup.

---

# Current Limitations

The current implementation uses deterministic rule-based parsing rather than a fully trained AI model.

The system currently:
- Requires manual execution through Python
- Requires manual responses to emails/messages
- Has limited natural language understanding
- Supports Gmail integration only

The project currently focuses more on scheduling assistance and availability computation rather than fully autonomous AI behavior.

---

# Future Improvements

Future development may include:
- WhatsApp integration
- More advanced AI and machine learning capabilities
- Improved natural language processing
- Fully automated response generation
- Smarter conversational scheduling assistance
- Better scalability and scheduling optimization

---

# Current State of the Project

This project serves as a functional prototype for AI-assisted scheduling automation.

While the original scope aimed for a more advanced AI-driven assistant, the final implementation prioritizes:
- Reliability
- Simplicity
- Maintainability
- Functional scheduling logic


