import sys
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["From"] = ""
msg["To"] = ""
msg["Subject"] = sys.argv[3]
msg.set_content(f"{sys.argv[2]}")

server = smtplib.SMTP_SSL(host="", port="465")
server.login("", sys.argv[1])
server.send_message(msg)
server.quit()
print("Сообщение отправлено")