import os
import traceback
from datetime import datetime


def log_exception(exception):
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Get today's date for log file name
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/{today}.txt"

    # Write exception to log file
    with open(log_file, "a") as f:
        f.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Exception occurred:\n"
        )
        f.write(traceback.format_exc())
        f.write("\n" + "=" * 50 + "\n")
