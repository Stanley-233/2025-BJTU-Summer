import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_address: str, subject: str, body: str):
  """发送邮件"""
  sender_email = "your_email@example.com"
  sender_password = "your_password"

  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = to_address
  msg['Subject'] = subject

  msg.attach(MIMEText(body, 'plain'))

  try:
    with smtplib.SMTP('smtp.example.com', 587) as server:
      server.starttls()
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, to_address, msg.as_string())
  except Exception as e:
    raise RuntimeError(f"Failed to send email: {e}")
