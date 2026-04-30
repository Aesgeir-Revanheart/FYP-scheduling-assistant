import re

def parse_query(text: str):
    text_l = text.lower()

    out = {}

    #Detects whether the user is referring to "today" or "tomorrow"
    if "today" in text_l:
        out["date"] = "today"

    elif "tomorrow" in text_l:
        out["date"] = "tomorrow"

    #Helper function to convert time into 24-hour format
    def normalize_time(hour, minute, ampm):
        hour = int(hour)
        minute = int(minute or 0)

        if ampm:
            if ampm == "pm" and hour != 12:
                hour += 12
            if ampm == "am" and hour == 12:
                hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute
        return None, None

    #match "after X time"
    m_after = re.search(r"\bafter\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m_after:
        hour, minute = normalize_time(m_after.group(1), m_after.group(2), m_after.group(3))
        if hour is not None:
            out["after_hour"] = hour
            out["after_min"] = minute

    #atches "before X time"
    m_before = re.search(r"\bbefore\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m_before:
        hour, minute = normalize_time(m_before.group(1), m_before.group(2), m_before.group(3))
        if hour is not None:
            out["before_hour"] = hour
            out["before_min"] = minute

    #match specifcally "at X time"
    m_at = re.search(r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m_at:
        hour, minute = normalize_time(m_at.group(1), m_at.group(2), m_at.group(3))
        if hour is not None:
            out["at_hour"] = hour
            out["at_min"] = minute

    #Detects general scheduling intent
    if any(word in text_l for word in ["free", "available", "meet", "schedule"]):
        out["intent"] = "free_time"

    return out if out else None