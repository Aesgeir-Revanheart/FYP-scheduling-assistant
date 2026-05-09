#AI Scheduling Assistant (FYP)

#Overview
This project is a semi-automated scheduling assistant that processes email queries and checks calendar availability using Google Calendar.

The system interprets queries such as:
- "Are you free after 3pm?"
- "Are you free before 6pm?"
- "Are you free at 10pm?"

It then outputs available time slots based on the user’s calendar.



# How to Run

1. Open the project in an IDE (VSC)
2. Navigate to:
   src/main.py

3. Run `main.py`


When running for the first time:

- A browser window will open
- You will be asked to:
  1. Select your Google account
  2. Grant calendar access permissions

This allows the program to read your calendar events.



After authentication:

1. The script runs and processes email queries
2. Outputs are shown in the terminal
3. You can return to the IDE to modify inputs or test queries



Notes on Calendar Data

- The system reads your Google Calendar events
- If your calendar is empty:
  - No conflicts will be detected
  - All time slots may appear free



Testing with Empty Calendar

If your calendar has no events:

You can modify the test input manually:

- Open `main.py`
- Go to  **line 230**
- Edit the sample query or logic
- Run the script again


#Output Example

- Busy slots displayed
- Free slots listed
- Specific time checks:
  "FREE at 13:00"
  "BUSY at 16:00"

