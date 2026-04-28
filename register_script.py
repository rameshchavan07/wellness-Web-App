import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
import uuid

# Add project root to path
sys.path.append(r"d:\dayscore full")

from config.firebase_config import get_firestore_client, get_firebase_auth
from config.settings import SMTPConfig
from services.counselor_service import CounselorService

emails = [
    "agckt5052+clinicalpsychologist@gmail.com",
    "agckt5052+psychiatrist@gmail.com",
    "agckt5052+therapist@gmail.com",
    "agckt5052+schoolcounsellor@gmail.com",
    "agckt5052+careercounsellor@gmail.com",
    "agckt5052+familycounsellor@gmail.com",
    "agckt5052+addiction@gmail.com",
    "agckt5052+crisis@gmail.com",
    "agckt5052+physiotherapist@gmail.com",
    "agckt5052+nutritionist@gmail.com",
    "agckt5052+dietitian@gmail.com",
    "agckt5052+occupational@gmail.com",
    "agckt5052+rehabilitation@gmail.com",
    "agckt5052+wellness@gmail.com"
]

password = "Counselor@123"
clinic = "DayScore Virtual Clinic"

def parse_specialty(email):
    part = email.split('+')[1].split('@')[0]
    mapping = {
        "clinicalpsychologist": "Clinical Psychologist",
        "psychiatrist": "Psychiatrist",
        "therapist": "Therapist",
        "schoolcounsellor": "School Counsellor",
        "careercounsellor": "Career Counsellor",
        "familycounsellor": "Family Counsellor",
        "addiction": "Addiction Specialist",
        "crisis": "Crisis Intervenor",
        "physiotherapist": "Physiotherapist",
        "nutritionist": "Nutritionist",
        "dietitian": "Dietitian",
        "occupational": "Occupational Therapist",
        "rehabilitation": "Rehabilitation Specialist",
        "wellness": "Wellness Coach"
    }
    return mapping.get(part.lower(), part.capitalize() + " Counselor")

auth = get_firebase_auth()
db = get_firestore_client()

for email in emails:
    specialty = parse_specialty(email)
    name = "Dr. " + specialty.split()[0]
    meet_link = CounselorService.generate_meet_link()
    
    print(f"Registering {email} as {specialty}...")
    
    try:
        # Check if user already exists
        try:
            user_record = auth.get_user_by_email(email)
            print(f"User {email} already exists. Updating...")
        except Exception:
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=name,
            )
        
        user_id = user_record.uid
        
        # Save to users collection
        user_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "profile_photo": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "streak": 0,
            "total_points": 0,
            "last_active_date": "",
            "sleep_streak": 0,
            "role": "counselor",
            "counselor_id": user_id
        }
        db.collection("users").document(user_id).set(user_data)
        
        # Save to counselors collection
        counselor_profile = {
            "id": user_id,
            "name": name,
            "specialty": specialty,
            "clinic": clinic,
            "email": email,
            "profile_photo": "",
            "tags": [specialty.strip()] if specialty else [],
            "rating": 5.0,
            "reviews": 0,
            "meet_link": meet_link,
            "next_available": "Tomorrow, 10:00 AM",
            "price": "₹800 / session"
        }
        db.collection("counselors").document(user_id).set(counselor_profile)
        
        print(f"Success for {email}. Password: {password}, Meeting Link: {meet_link}")
        
        # Send Email
        if SMTPConfig.USERNAME and SMTPConfig.PASSWORD:
            msg = EmailMessage()
            msg['Subject'] = "Welcome to DayScore - Counselor Registration Details"
            msg['From'] = SMTPConfig.FROM_EMAIL
            msg['To'] = email
            
            body = f"""Hello {name},

You have been successfully registered as a {specialty} on the DayScore platform.

Login Details:
Email: {email}
Password: {password}

Your Permanent Virtual Meeting Link:
{meet_link}

Please keep this link safe as it will be used for your upcoming patient sessions.

Best Regards,
DayScore Team
"""
            msg.set_content(body)
            
            try:
                with smtplib.SMTP(SMTPConfig.SERVER, SMTPConfig.PORT) as server:
                    server.starttls()
                    server.login(SMTPConfig.USERNAME, SMTPConfig.PASSWORD)
                    server.send_message(msg)
                print(f"Email sent to {email}")
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
        else:
            print(f"SMTP credentials not set, email to {email} skipped.")
            
    except Exception as e:
        print(f"Failed to register {email}: {e}")

print("Done.")
