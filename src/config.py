import os
from datetime import timezone, timedelta

# --- CONFIG ---
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

 
OAUTH_JSON_FILENAME = "client_secret.json"
GMAIL_OAUTH_FILENAME = "client_secret_gmail.json"
GMAIL_TOKEN_FILENAME = "token_gmail.json"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TOKEN_FILENAME = "token.json"
TARGET_CALENDAR_NAME = os.getenv("TARGET_CALENDAR_NAME", "SmartB Team")

EVENTS_DAYS_FORWARD = 60
EVENTS_MAX_RESULTS = 250
PRINT_EVENTS_LIMIT = 50

FREEBUSY_DAYS_FORWARD = 14
PRINT_BUSY_LIMIT = 50

MY_TZ = timezone(timedelta(hours=8))

WORK_START_HOUR = 9
WORK_START_MIN = 0
WORK_END_HOUR = 21
WORK_END_MIN = 30

LEAVE_KEYWORDS = [" AL", "ANNUAL LEAVE", "LEAVE", "OOO", "OUT OF OFFICE", "HOLIDAY"]