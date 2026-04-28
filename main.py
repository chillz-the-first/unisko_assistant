from flask import Flask
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
        message = f"""
            Hello {row["Parent Name"]}! 👋\n
            This is a friendly reminder that payment of {row["Amount Due"]} for {row["Student Name"]} is due.\n
            Please make the payment before the the 7th of this month to avoid disruptions to your child's sessions.\n
            Thank you! 😊
        """

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
            hour=6,
            minute=0,
        )

if __name__ == "__main__":
    start_scheduler()
    app.run(port=5000)
