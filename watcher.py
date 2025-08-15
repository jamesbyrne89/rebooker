import subprocess
import time
import datetime
from playwright.sync_api import sync_playwright
from run import run_with_booking_page, run, send_notification

RUN_DURATION_SECONDS = 7 * 24 * 60 * 60
# How often to run when it crashes (in seconds):
INTERVAL_SECONDS = 1 * 30

send_notification("Watcher started: birth registration slot checker is running.")

start_time = datetime.datetime.now()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()  # Create a single page to reuse
    
    while (datetime.datetime.now() - start_time).total_seconds() < RUN_DURATION_SECONDS:
        print(f"Running run.py at {datetime.datetime.now().isoformat()}")
        try:
            # Run the booking page function
            run_with_booking_page(playwright, browser, context, page)
            # Run the main function
            # run(playwright, browser, context, page)
        except Exception as e:
            print(f"run.py failed with error: {e}")
            send_notification(f"Error in birth registration checker: {e}")
        print(f"Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)

    page.close()
    context.close()
    browser.close()

send_notification("Watcher finished after 7 days.")
print("Watcher finished after 7 days.") 
