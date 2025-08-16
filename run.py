import re
import time
from playwright.sync_api import Playwright, expect
from datetime import datetime
import subprocess

# Add it here, has that shape: https://lambeth.sishost.co.uk/Agenda/OnlineBookings/appointment.html?pg=...
BIRTH_REBOOK_PAGE = "https://lambeth.sishost.co.uk/Agenda/OnlineBookings/appointment.html?pg=14c073f6-37da-4092-b118-f6beca3bd5a8&pltoken=c7d639c7-9217-404f-a20b-33e1d410645b"
NTFY_TOPIC = "james_lambeth_alert"
# Compare to 27th August of the same year - change for your case
COMPARE_DATE_AFTER = datetime(2025, 9, 1)
COMPARE_DATE_BEFORE = datetime(2025, 8, 18)

def send_notification(message):
    subprocess.run([
        "ntfy", "publish", NTFY_TOPIC, message
    ])

def run_with_booking_page(playwright: Playwright, browser, context, page) -> None:
    """
    Run with a rebook page.
    """

    page.goto(BIRTH_REBOOK_PAGE)
    page.get_by_role("button", name="Next").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("Reschedule my appointment").click()
    page.get_by_role("textbox", name="Reason:").click()
    page.get_by_role("textbox", name="Reason:").fill("Need to book earlier appointment due to travel")

    def go_to_next_and_try_to_reserve():
        # Wait for 1 second
        time.sleep(1)
        page.get_by_role("button", name="Next").click()

        locator = page.locator("text=The next available appointment is")
        locator.wait_for(timeout=60000 * 4)

        full_text = locator.inner_text()
        print(full_text)

        def extract_appointment_date(text):
            # Regex to match e.g. '2nd September 2025'
            match = re.search(r'on (\d{1,2})(?:st|nd|rd|th)? ([A-Za-z]+) (\d{4})', text)
            if not match:
                return None
            day, month_str, year = match.groups()
            # Parse month name to month number
            try:
                date_obj = datetime.strptime(f"{day} {month_str} {year}", "%d %B %Y")
                return date_obj
            except ValueError:
                return None

        appointment_date = extract_appointment_date(full_text)

        if appointment_date:
            # Compare to 27th August of the same year
            if appointment_date < COMPARE_DATE_AFTER and appointment_date > COMPARE_DATE_BEFORE:
                print(f"Appointment is between {COMPARE_DATE_BEFORE.strftime('%d %B %Y')} and {COMPARE_DATE_AFTER.strftime('%d %B %Y')}: {appointment_date.strftime('%d %B %Y')}")
                date_found = appointment_date.strftime('%d %B %Y')
                send_notification(f"🚨 A birth registration slot is available {date_found}")

                # Find the button with the text "Reserve this time"
                reserve_button = page.get_by_text("Reserve this time")
                reserve_button.click()

                # Pause here so that I can manually fill in the form
                input("Press Enter to continue...")

            else:
                print(f"Appointment is not between {COMPARE_DATE_BEFORE.strftime('%d %B %Y')} and {COMPARE_DATE_AFTER.strftime('%d %B %Y')}: {appointment_date.strftime('%d %B %Y')}")
                date_found = appointment_date.strftime('%d %B %Y')
                # send_notification(f"No slot before 27th August. Next available: {date_found}")

                # Click on 'Back' button
                # Wait for 3 seconds
                time.sleep(3)
                page.get_by_role("button", name="Back").click()
                go_to_next_and_try_to_reserve()
        else:
            print("Could not extract appointment date.")
            send_notification("No slot found in the appointment text.")
    
            # Click on 'Back' button
            # Wait for 3 seconds
            time.sleep(3)
            page.get_by_role("button", name="Back").click()
            go_to_next_and_try_to_reserve()
        
    go_to_next_and_try_to_reserve()

