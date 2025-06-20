from google.cloud import firestore
from datetime import datetime, timedelta

db = firestore.Client()

def check_expiring_food():
    items = db.collection('food_items').where('notified', '==', False).stream()
    for item in items:
        data = item.to_dict()
        expiry_date = data['expiry_date'].replace(tzinfo=None)
        days_left = (expiry_date - datetime.now()).days

        print(f"Checking {data['email']} — Days left: {days_left}")

        if days_left <= 14:
            print("📌 Marking for frontend notification")
            item.reference.update({
                'ready_to_notify': True  # <-- frontend will look for this
            })

if __name__ == "__main__":
    check_expiring_food()
