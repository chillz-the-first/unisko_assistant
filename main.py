from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

from data_manager import get_unpaid_balances
from whatsapp import app, send_whatsapp_msg

load_dotenv()

def send_payment_reminders(day):
    """Gets all unpaid balances and sends each parent a WhatsApp reminder."""
    unpaid = get_unpaid_balances()

    for row in unpaid:
        message = (
            f"Hello {row['Parent Name']}! 👋 "
            f"This is a friendly reminder that payment of "
            f"{row['Amount Due']} for {row['Student Name']} is due. "
            f"Please make payment before the {day + 6}th of this month "
            f"to avoid any disruptions to your child's sessions. "
            f"Thank you! 😊"
        )

        send_whatsapp_msg(row["Parent WhatsApp"], message)

def start_scheduler():
    """Sets up the monthly payment reminder schedule."""
    scheduler = BackgroundScheduler()

    reminder_days = [1, 10, 20]
    for day in reminder_days:
        scheduler.add_job(
            send_payment_reminders,
            trigger="cron",
            day=day,
            hour=4,
            minute=0,
            args=[day],
        )

    scheduler.start()