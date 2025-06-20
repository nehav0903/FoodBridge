import requests

def send_notification(email, expiry_date):
    service_id = 'service_5muhiik'
    template_id = 'template_zm4uyuk'
    user_id = 'lu_rb52TLwgkWl-k0'

    payload = {
        'service_id': service_id,
        'template_id': template_id,
        'user_id': user_id,
        'template_params': {
            'to_email': email,
            'expiry_date': expiry_date.strftime('%d-%m-%Y'),
        }
    }

    response = requests.post('https://api.emailjs.com/api/v1.0/email/send', json=payload)

    if response.status_code == 200:
        print(f"✅ Email sent to {email}")
    else:
        print(f"❌ Failed to send email: {response.text}")
