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
        # Wait for 3 seconds
        time.sleep(3)
        page.get_by_role("button", name="Next").click()

        locator = page.locator("text=The next available appointment is")
        locator.wait_for(timeout=240000*2)  # 4 minutes in ms

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


def run(playwright: Playwright, browser, context, page) -> None:
    page.goto("https://www.lambeth.gov.uk/births-deaths-ceremonies-and-citizenship/births/register-birth/make-appointment")
    page.get_by_role("link", name="Book an appointment online").click()
    page.get_by_role("checkbox", name="I confirm and accept the above").check()
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="Baby's date of birth").click()
    page.get_by_role("link", name="12").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("Baby was born in Lambeth").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("St Thomas' Hospital").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("Parents were married or in a").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("I confirm I understand this").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("baby").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("Yes").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="Your first name (required)").click()
    page.get_by_role("textbox", name="Your first name (required)").fill("Mar")
    page.get_by_role("textbox", name="Your surname (required)").click()
    page.get_by_role("textbox", name="Your surname (required)").fill("Bar")
    page.get_by_role("textbox", name="Email (required)").click()
    page.get_by_role("textbox", name="Email (required)").fill("marbar@gmail.com")
    page.locator(".govuk-grid-column-one-half.text-right").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="NHS Number: (required)").click()
    page.get_by_role("textbox", name="NHS Number: (required)").fill("7363578991")
    page.get_by_role("textbox", name="All first and middle names in").click()
    page.get_by_role("textbox", name="All first and middle names in").fill("Leo")
    page.get_by_role("textbox", name="Surname in which the child").click()
    page.get_by_role("textbox", name="Surname in which the child").fill("Mar Bar")
    page.get_by_label("Child's gender: (required)").select_option("Male")
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="First name of baby's father/").click()
    page.get_by_role("textbox", name="First name of baby's father/").fill("Bar")
    page.get_by_role("textbox", name="Surname name of baby's father").click()
    page.get_by_role("textbox", name="Surname name of baby's father").fill("Mar")
    page.get_by_role("textbox", name="Baby's father/second parent - Are you or have you ever been known by any other").click()
    page.get_by_role("textbox", name="Baby's father/second parent - Are you or have you ever been known by any other").fill("No")
    page.get_by_role("textbox", name="Father/second parent's date").click()
    page.get_by_role("textbox", name="Father/second parent's date").fill("01/01/1990")
    page.get_by_role("textbox", name="Father/second parent's place").click()
    page.get_by_role("textbox", name="Father/second parent's place").fill("London")
    page.get_by_role("textbox", name="Father/second parent's place").press("Tab")
    page.get_by_role("textbox", name="Father/second parent's place").click()
    page.get_by_role("textbox", name="Father/second parent's place").fill("London, London")
    page.get_by_role("textbox", name="Father/second parent's occupation at the time of birth: (required)").click()
    page.get_by_role("textbox", name="Father/second parent's occupation at the time of birth: (required)").fill("Software Engineer")
    page.get_by_role("textbox", name="Baby's mother - Are you or").click()
    page.get_by_role("textbox", name="Baby's mother - Are you or").fill("No")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").click()
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").fill("01/01/1989")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's date of birth (dd/mm").fill("01/03/1989")
    page.get_by_role("textbox", name="Mother's place of birth (").click()
    page.get_by_role("textbox", name="Mother's place of birth (").fill("London, London")
    page.get_by_role("textbox", name="Mother's occupation at the").click()
    page.get_by_role("textbox", name="Mother's occupation at the").fill("Software Engineer")
    page.get_by_role("textbox", name="Mother's address at the time").click()
    page.get_by_role("textbox", name="Mother's address at the time").fill("SW49DT")
    page.get_by_role("textbox", name="Mother's address at the time").press("ArrowLeft")
    page.get_by_role("textbox", name="Mother's address at the time").press("ControlOrMeta+ArrowLeft")
    page.get_by_role("textbox", name="Mother's address at the time").fill("\nSW49DT")
    page.get_by_role("textbox", name="Mother's address at the time").press("ArrowUp")
    page.get_by_role("textbox", name="Mother's address at the time").fill("Flat 5,\n09 Maud Chadburn Place\nSW49DT")
    page.get_by_role("textbox", name="Mother's address at the time").press("ArrowDown")
    page.get_by_role("textbox", name="Mother's address at the time").press("Shift+ArrowUp")
    page.get_by_role("textbox", name="Mother's address at the time").press("Shift+ArrowUp")
    page.get_by_role("textbox", name="Mother's address at the time").press("Shift+ArrowUp")
    page.get_by_role("textbox", name="Mother's address at the time").press("ControlOrMeta+c")
    page.get_by_role("textbox", name="Father/second parent's address at the time of birth: (required)").click()
    page.get_by_role("textbox", name="Father/second parent's address at the time of birth: (required)").fill("Flat 5,\n09 Maud Chadburn Place\nSW49DT")
    page.get_by_role("textbox", name="Month and year in which").click()
    page.get_by_role("textbox", name="Month and year in which").fill("01/2018")
    page.get_by_role("textbox", name="What industry does the father").click()
    page.get_by_role("textbox", name="What industry does the father").fill("Information Technology")
    page.get_by_label("Are they: (required)").first.select_option("Employee")
    page.get_by_role("textbox", name="What industry does the mother").click()
    page.get_by_role("textbox", name="What industry does the mother").fill("Information Technology")
    page.get_by_label("Are they: (required)").nth(1).select_option("Employee")
    page.get_by_text("Yes").click()
    page.get_by_role("button", name="Next").click()
    page.get_by_role("textbox", name="Informant's telephone number").click()
    page.get_by_role("textbox", name="Informant's telephone number").fill("7692845957")
    page.get_by_role("textbox", name="Informant's telephone number").click()
    page.get_by_role("textbox", name="Informant's telephone number").press("ControlOrMeta+ArrowLeft")
    page.get_by_role("textbox", name="Informant's telephone number").fill("07692845957")
    page.get_by_role("button", name="Next").click()
    page.locator(".govuk-radios > div:nth-child(2)").click()
    page.get_by_text("No", exact=True).click()
    page.get_by_role("button", name="Next").click()
    
    locator = page.locator("text=The next available appointment is")
    locator.wait_for(timeout=240000)  # 2 minutes in ms

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
        if appointment_date < COMPARE_DATE:
            print(f"Appointment is before {COMPARE_DATE.strftime('%d %B %Y')}: {appointment_date.strftime('%d %B %Y')}")
            date_found = appointment_date.strftime('%d %B %Y')
            send_notification(f"🚨 A birth registration slot is available {date_found}")
        else:
            print(f"Appointment is on or after 27th August: {appointment_date.strftime('%d %B %Y')}")
            date_found = appointment_date.strftime('%d %B %Y')
            # send_notification(f"No slot before 27th August. Next available: {date_found}")
    else:
        print("Could not extract appointment date.")
        send_notification("No slot found in the appointment text.")
