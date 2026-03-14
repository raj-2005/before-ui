import smtplib
from email.message import EmailMessage

username = "qwertydoctor@gmail.com"
password = "tjotchkdveujmkfx"

msg = EmailMessage()
msg["From"] = username
msg["To"] = "rajapplogins@gmail.com"
msg["Subject"] = "Direct SMTP Test"
msg.set_content("If you receive this, SMTP works!")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

    print("✅ EMAIL SENT SUCCESSFULLY")

except Exception as e:
    print("❌ FULL ERROR:")
    print(repr(e))