import logging
from datetime import date, timedelta, datetime

# In a real application, this would be a proper database module (e.g., `src.crud.subscription`)
# that handles database queries. For this MVP, we import the fake DB directly.
from src.api.v1.subscriptions import fake_subscriptions_db

def check_for_reminders():
    """
    Checks for subscriptions that are nearing their renewal date and sends reminders.
    """
    logging.info(f"--- Running reminder check at {datetime.now()} ---")
    today = date.today()
    reminder_window_end = today + timedelta(days=7)

    subscriptions_to_remind = []

    for sub in fake_subscriptions_db:
        # Condition 1: Is the renewal date within our 7-day window?
        is_due_for_renewal = today <= sub["next_renewal_date"] <= reminder_window_end
        if not is_due_for_renewal:
            continue

        # Condition 2: Has a reminder been sent recently?
        reminder_sent_recently = False
        last_sent = sub.get("last_reminder_sent_at")
        if last_sent:
            if datetime.now() - last_sent < timedelta(days=7):
                reminder_sent_recently = True

        if not reminder_sent_recently:
            subscriptions_to_remind.append(sub)

    if not subscriptions_to_remind:
        logging.info("No subscriptions require a reminder.")
    else:
        for sub in subscriptions_to_remind:
            # Simulate sending an email
            logging.info(f"[EMAIL] REMINDER: Your subscription for '{sub['service_name']}' is renewing on {sub['next_renewal_date']}.")

            # Update the timestamp in our fake DB to prevent re-sending.
            sub["last_reminder_sent_at"] = datetime.now()
            logging.info(f"Updated last_reminder_sent_at for subscription ID: {sub['id']}")

    logging.info("--- Reminder check complete ---")
