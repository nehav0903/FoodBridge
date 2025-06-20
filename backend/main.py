import os
import json
from google.oauth2 import service_account
from flask import Flask, request, render_template
from google.cloud import vision
from google.cloud import firestore
from dotenv import load_dotenv
from datetime import datetime
import re
from flask import jsonify


app = Flask(__name__)
load_dotenv()


#db = firestore.Client()
#vision_client = vision.ImageAnnotatorClient()
creds_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(creds_info)

db = firestore.Client(credentials=credentials, project=creds_info["project_id"])
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

def extract_expiry_date(text):
    # Find all dates (DD/MM/YY or DD-MM-YY or DD/MM/YYYY)
    date_matches = re.findall(r'(\d{2}[/-]\d{2}[/-]\d{2,4})', text)
    
    for date_str in date_matches:
        # Grab 15 characters before the date to find context
        index = text.find(date_str)
        context = text[max(0, index - 15):index].lower()

        if "exp" in context or "expiry" in context:
            # Normalize separators
            date_str_clean = date_str.replace('-', '/').replace('.', '/')
            year_part = date_str_clean.split('/')[-1]

            try:
                if len(year_part) == 2:
                    return datetime.strptime(date_str_clean, '%d/%m/%y')
                else:
                    return datetime.strptime(date_str_clean, '%d/%m/%Y')
            except ValueError:
                continue  # Try next match

    return None  # No valid expiry date found

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        owner_email = request.form['email']

        content = image.read()
        image_vision = vision.Image(content=content)
        response = vision_client.text_detection(image=image_vision)
        text = response.text_annotations[0].description if response.text_annotations else ""
        print("🔍 Detected text from image:")
        print(text)

        expiry_date = extract_expiry_date(text)
        if not expiry_date:
            return jsonify({'success': False, 'message': '❌ Expiry date not found in the image.'})

        # Store in Firestore
        db.collection('food_items').add({
            'email': owner_email,
            'expiry_date': expiry_date,
            'uploaded_on': datetime.now(),
            'notified': False,
            'donated': False,
            'ready_to_notify': True,
            'time': expiry_date.strftime('%I:%M %p'),
            'name': "FoodBridge"
        })

        print("✅ Data stored in Firestore")

        return jsonify({
            'success': True,
            'email': owner_email,
            'expiry_date': expiry_date.strftime('%d-%m-%Y')
        })

    # GET request – render the page normally
    return render_template('upload.html',
        FIREBASE_API_KEY=os.getenv('FIREBASE_API_KEY'),
        FIREBASE_AUTH_DOMAIN=os.getenv('FIREBASE_AUTH_DOMAIN'),
        FIREBASE_PROJECT_ID=os.getenv('FIREBASE_PROJECT_ID'),
        FIREBASE_STORAGE_BUCKET=os.getenv('FIREBASE_STORAGE_BUCKET'),
        FIREBASE_MESSAGING_SENDER_ID=os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        FIREBASE_APP_ID=os.getenv('FIREBASE_APP_ID'),
        EMAILJS_USER_ID=os.getenv('EMAILJS_USER_ID'),
        EMAILJS_SERVICE_ID=os.getenv('EMAILJS_SERVICE_ID'),
        EMAILJS_TEMPLATE_ID=os.getenv('EMAILJS_TEMPLATE_ID'),
    )

@app.route('/ngo_map')
def show_ngo_map():
    return render_template('ngo_map.html',
        GOOGLE_MAPS_API_KEY=os.getenv('GOOGLE_MAPS_API_KEY'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
