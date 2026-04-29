import re

def parse_query(text: str):
    text_l = text.lower()

    out = {}

    # --- DATE ---
    if "tomorrow" in text_l:
        out["date"] = "tomorrow"

    # --- TIME NORMALIZATION FUNCTION ---
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

    # --- AFTER ---
    m = re.search(r"\bafter\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m:
        hour, minute = normalize_time(m.group(1), m.group(2), m.group(3))
        if hour is not None:
            out["after_hour"] = hour
            out["after_min"] = minute

    # --- BEFORE ---
    m2 = re.search(r"\bbefore\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_l)
    if m2:
        hour, minute = normalize_time(m2.group(1), m2.group(2), m2.group(3))
        if hour is not None:
            out["before_hour"] = hour
            out["before_min"] = minute

    # --- AT TIME (IMPROVED) ---
    # Supports:
    # "at 3pm", "at 3", "3pm", "14:00"
    m3 = re.search(r"\b(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text_l)
    if not m3:
        # fallback: "at 14" (no am/pm)
        m3 = re.search(r"\bat\s+(\d{1,2})(?::(\d{2}))?\b", text_l)

    if m3:
        hour, minute = normalize_time(m3.group(1), m3.group(2), m3.group(3) if len(m3.groups()) >= 3 else None)
        if hour is not None:
            out["at_hour"] = hour
            out["at_min"] = minute

    # --- INTENT DETECTION ---
    if any(word in text_l for word in ["free", "available", "meet", "schedule"]):
        out["intent"] = "free_time"

    return out if out else None