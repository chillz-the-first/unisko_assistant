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
            Please make the payment before the the {day + 7}th of this month to avoid disruptions to your child's sessions.\n
            Thank you! 😊
        """

        send_whatsapp_msg(row["Parent WhatsApp"], message)

def start_scheduler():
    """Temporary test version — fires 2 minutes from now."""
    from datetime import datetime, timedelta

    scheduler = BackgroundScheduler()
    test_time = datetime.now() + timedelta(minutes=2)

    scheduler.add_job(
        send_payment_reminders,
        trigger="date",
        run_date=test_time,
        args=[1]
    )

    scheduler.start()
    print(f"Test reminder scheduled for {test_time}")