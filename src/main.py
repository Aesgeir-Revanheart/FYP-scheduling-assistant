from config import *
from parser import parse_query
from scheduler import show_free_slots_tomorrow
import os
from datetime import datetime, timezone, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email_processor import process_email

import re


def path_next_to_script(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    return os.path.join(project_root, filename)



# CALENDAR AUTH 

def get_creds():
    oauth_json_path = path_next_to_script(OAUTH_JSON_FILENAME)
    token_path = path_next_to_script(TOKEN_FILENAME)

    if not os.path.exists(oauth_json_path):
        raise FileNotFoundError(
            f"OAuth JSON file not found:\n  {oauth_json_path}\n\n"
            "Place it in the same folder as this script and update OAUTH_JSON_FILENAME."
        )

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(oauth_json_path, SCOPES)
        creds = flow.run_local_server(port=0)

    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    return creds



# GMAIL AUTH 

def get_gmail_service():
    oauth_path = path_next_to_script(GMAIL_OAUTH_FILENAME)
    token_path = path_next_to_script(GMAIL_TOKEN_FILENAME)

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(oauth_path, GMAIL_SCOPES)
        creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service



# GMAIL READER 

def read_latest_emails(service, events, max_results=15):
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        labelIds=["INBOX"],
        q="category:primary"
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
        return

    print("\n=== LATEST EMAILS ===\n")

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"]
        ).execute()

        headers = msg_data.get("payload", {}).get("headers", [])

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown)")

        body = msg_data.get("snippet", "")

        print(f"From: {sender}")
        print(f"Subject: {subject}")

        full_text = subject + " " + body
        process_email(full_text, events)

        print("-" * 40)



# CALENDAR FUNCTIONS 

def list_calendars(service):
    cal_list = service.calendarList().list().execute()
    items = cal_list.get("items", [])

    print("\n=== calendarList (includes shared calendars) ===\n")
    for c in items:
        print(
            f"- {c.get('summary')} | id={c.get('id')} | role={c.get('accessRole')} | primary={c.get('primary', False)}"
        )
    return items


def normalize_name(s: str) -> str:
    return " ".join((s or "").split()).casefold()


def find_calendar_by_name(calendars, name: str):
    target = normalize_name(name)
    for cal in calendars:
        if normalize_name(cal.get("summary", "")) == target:
            return cal
    return None


def fetch_events(service, calendar_id: str):
    time_min = datetime.now(timezone.utc).isoformat()
    time_max = (datetime.now(timezone.utc) + timedelta(days=EVENTS_DAYS_FORWARD)).isoformat()

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=EVENTS_MAX_RESULTS,
        singleEvents=True,
        orderBy="startTime",
        showDeleted=False,
    ).execute()

    events = events_result.get("items", [])

    print(f"\n=== EVENTS (calendarId: {calendar_id}) ===")
    print(f"[DEBUG] Window: {time_min}  →  {time_max}")
    print(f"[DEBUG] events returned: {len(events)}\n")

    for e in events[:PRINT_EVENTS_LIMIT]:
        start = e["start"].get("dateTime", e["start"].get("date"))
        end = e["end"].get("dateTime", e["end"].get("date"))
        title = e.get("summary", "(no title)")
        status = e.get("status", "")
        visibility = e.get("visibility", "")
        print(f"{start} → {end} — {title}  [status={status} visibility={visibility}]")

    if len(events) > PRINT_EVENTS_LIMIT:
        print(f"\n... (showing first {PRINT_EVENTS_LIMIT} of {len(events)})")

    return events


def freebusy_probe(service, calendar_id: str):
    time_min = datetime.now(timezone.utc).isoformat()
    time_max = (datetime.now(timezone.utc) + timedelta(days=FREEBUSY_DAYS_FORWARD)).isoformat()

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": calendar_id}],
    }

    fb = service.freebusy().query(body=body).execute()
    busy = fb.get("calendars", {}).get(calendar_id, {}).get("busy", [])

    print(f"\n=== FREEBUSY PROBE (calendarId: {calendar_id}) ===")
    print(f"[DEBUG] Window: {time_min}  →  {time_max}")
    print(f"[DEBUG] busy blocks returned: {len(busy)}\n")

    for b in busy[:PRINT_BUSY_LIMIT]:
        print(f"BUSY: {b.get('start')} → {b.get('end')}")

    if len(busy) > PRINT_BUSY_LIMIT:
        print(f"\n... (showing first {PRINT_BUSY_LIMIT} of {len(busy)})")

    return busy



# MAIN

def main():
    print("RUNNING:", os.path.abspath(__file__))

    # --- Calendar ---
    creds = get_creds()
    service = build("calendar", "v3", credentials=creds)

    calendars = list_calendars(service)

    target_cal = find_calendar_by_name(calendars, TARGET_CALENDAR_NAME)
    print(f"\n[DEBUG] TARGET_CALENDAR_NAME = {TARGET_CALENDAR_NAME!r}")

    if not target_cal:
        raise RuntimeError(
            f"Could not find a calendar named '{TARGET_CALENDAR_NAME}'. "
            "It must appear in calendarList output."
        )

    target_id = target_cal.get("id")
    print(f"[DEBUG] Using calendar summary = {target_cal.get('summary')!r}")
    print(f"[DEBUG] Using calendarId       = {target_id!r}")
    print(f"[DEBUG] accessRole            = {target_cal.get('accessRole')!r}\n")

    events = fetch_events(service, target_id)

    USER_QUERY = "Are you free at 1pm tomorrow?"

    parsed = parse_query(USER_QUERY)
    print(f"[DEBUG] USER_QUERY = {USER_QUERY!r}")
    print(f"[DEBUG] parsed     = {parsed!r}")

    if parsed and parsed.get("date") == "tomorrow":
        after_hour = parsed.get("after_hour")
        after_min = parsed.get("after_min", 0)

        before_hour = parsed.get("before_hour")
        before_min = parsed.get("before_min", 0)

        now_local = datetime.now(MY_TZ)
        tomorrow = (now_local + timedelta(days=1)).date()

        earliest_start = None
        if after_hour is not None:
            earliest_start = datetime.combine(
                tomorrow, datetime.min.time(), tzinfo=MY_TZ
            ).replace(hour=after_hour, minute=after_min)

        latest_end = None
        if before_hour is not None:
            latest_end = datetime.combine(
                tomorrow, datetime.min.time(), tzinfo=MY_TZ
            ).replace(hour=before_hour, minute=before_min)

        show_free_slots_tomorrow(
            events,
            earliest_start=earliest_start,
            latest_end=latest_end,
        )

        # SPECIFIC TIME CHECK 
        at_hour = parsed.get("at_hour")
        at_min = parsed.get("at_min", 0)

        if at_hour is not None:
            specific_time = datetime.combine(
                tomorrow, datetime.min.time(), tzinfo=MY_TZ
            ).replace(hour=at_hour, minute=at_min)

            print("\n=== SPECIFIC TIME CHECK ===\n")

            is_free = True

            for e in events:
                start_dt_str = e["start"].get("dateTime")
                end_dt_str = e["end"].get("dateTime")

                if not start_dt_str or not end_dt_str:
                    continue

                start_dt = datetime.fromisoformat(start_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)
                end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00")).astimezone(MY_TZ)

                if start_dt <= specific_time < end_dt:
                    is_free = False
                    break

            if is_free:
                print(f"You are FREE at {specific_time.strftime('%H:%M')}")
            else:
                print(f"You are BUSY at {specific_time.strftime('%H:%M')}")

    else:
        print("Query not understood yet.")

    freebusy_probe(service, target_id)

    # --- Gmail ---
    gmail_service = get_gmail_service()
    read_latest_emails(gmail_service, events)


if __name__ == "__main__":
    main()