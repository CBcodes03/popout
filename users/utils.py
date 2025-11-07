import math
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def genotp():
    digits = "0123456789"
    return "".join(random.choice(digits) for _ in range(6))

def send_vmail(otp, emailid):
    message = MIMEMultipart()
    message['From'] = 'popout .Inc <cbblogs58@gmail.com>'
    message['To'] = emailid
    message['Subject'] = 'Verification'
    message.attach(MIMEText(f'Your OTP is: {otp}', 'plain'))

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("cbblogs58@gmail.com", "orhn nagd xhpc swsq")
    s.sendmail(from_addr="cbblogs58@gmail.com", to_addrs=emailid, msg=message.as_string())
    s.quit()

OTP_STORE = {}  # {email: {"otp": "123456", "timestamp": 1234567.0, "password": "userpass"}}
OTP_EXPIRY_SECONDS = 30

def store_otp(email, otp, password):
    OTP_STORE[email] = {"otp": otp, "timestamp": time.time(), "password": password}

def validate_otp(email, otp_input):
    if email not in OTP_STORE:
        return False, "No OTP found for this email."
    
    data = OTP_STORE[email]
    # Check expiration
    if time.time() - data["timestamp"] > OTP_EXPIRY_SECONDS:
        del OTP_STORE[email]
        return False, "OTP expired. Please try again."

    # Check correctness
    if data["otp"] != otp_input:
        return False, "Invalid OTP."

    # Return success
    password = data["password"]
    del OTP_STORE[email]
    return True, password

