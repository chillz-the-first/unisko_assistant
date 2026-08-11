from apscheduler.schedulers.background import BackgroundScheduler
from data_manager import get_unpaid_balances
from dotenv import load_dotenv
import os

load_dotenv()

# The name of your approved WhatsApp template (set in .env / Render).
# If this is blank, the bot falls back to plain text messages, which only
# work in Meta test mode. For real customers you MUST use a template,
# because reminders are business-initiated messages outside the 24-hour
# customer service window.
PAYMENT_TEMPLATE_NAME = os.getenv("PAYMENT_TEMPLATE_NAME", "").strip()

def send_payment_reminders(day):
    """Gets all unpaid balances and sends each parent a WhatsApp reminder."""
    print(f"Payment reminder job started for day {day}")
    from whatsapp import send_whatsapp_msg, send_whatsapp_template

    try:
        unpaid = get_unpaid_balances()
    except Exception as e:
        print(f"Could not read balances sheet, no reminders sent: {e}")
        return

    print(f"Found {len(unpaid)} unpaid balances")
    deadline = f"{day + 6}th of this month"

    for row in unpaid:
        # One bad row (missing column, bad number) must not stop the rest
        try:
            number = str(row["Parent WhatsApp"]).strip()
            print(f"Sending reminder to {number}")

            if PAYMENT_TEMPLATE_NAME:
                sent = send_whatsapp_template(
                    number,
                    PAYMENT_TEMPLATE_NAME,
                    [
                        row["Parent Name"],     # {{1}}
                        row["Amount Due"],      # {{2}}
                        row["Student Name"],    # {{3}}
                        deadline,               # {{4}}
                    ]
                )
            else:
                message = (
                    f"Hello {row['Parent Name']}! 👋 "
                    f"This is a friendly reminder that payment of "
                    f"{row['Amount Due']} for {row['Student Name']} is due. "
                    f"Please make payment before the {deadline} "
                    f"to avoid any disruptions to your child's sessions. "
                    f"Thank you! 😊"
                )
                sent = send_whatsapp_msg(number, message)

            if sent:
                print(f"Reminder sent to {number}")
        except Exception as e:
            print(f"Failed to send reminder for row {row}: {e}")

def start_scheduler():
    """Sends payment reminders on the 1st, 10th and 20th of every month
    at 04:00 UTC, which is 06:00 South African time (SAST = UTC+2)."""
    scheduler = BackgroundScheduler()

    reminder_days = [1, 10, 20]
    for day in reminder_days:
        scheduler.add_job(
            send_payment_reminders,
            trigger="cron",
            day=day,
            hour=4,
            minute=0,
            args=[day]
        )

    scheduler.start()
    print('Payment reminder scheduler started')
