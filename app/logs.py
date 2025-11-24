from datetime import datetime
import os

#--------------------
# LOGGING FUNCTION
#--------------------

def log_action(actor, action):
    """Log a user action with timestamp to a monthly log file."""
    now = datetime.now()
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", now.strftime("%y-%m") + ".txt")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {actor} | Action: {action}\n")
