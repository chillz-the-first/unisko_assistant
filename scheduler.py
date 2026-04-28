from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from data_manager import get_unpaid_balances

def send_payment_reminders(day):
    """Gets all unpaid balances and sends each parent a WhatsApp reminder."""
    print(f"Payment reminder job started for day {day}")
    from whatsapp import send_whatsapp_msg
    unpaid = get_unpaid_balances()
    print(f"Found {len(unpaid)} unpaid balances")

    for row in unpaid:
        print(f"Sending reminder to {row['Parent WhatsApp']}")
        message = (
            f"Hello {row['Parent Name']}! 👋 "
            f"This is a friendly reminder that payment of "
            f"{row['Amount Due']} for {row['Student Name']} is due. "
            f"Please make payment before the {day + 6}th of this month "
            f"to avoid any disruptions to your child's sessions. "
            f"Thank you! 😊"
        )
        send_whatsapp_msg(row["Parent WhatsApp"], message)
        print(f"Reminder sent to {row['Parent WhatsApp']}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    test_time = datetime.now() + timedelta(minutes=2)

    scheduler.add_job(
        send_payment_reminders,
        trigger="date",
        run_date=test_time,
        args=[1],
    )
    scheduler.start()
    print(f"Test reminder scheduled for {test_time}")