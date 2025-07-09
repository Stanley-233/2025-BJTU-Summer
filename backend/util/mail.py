import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

def send_email(to_address: str, subject: str, body: str):
  """发送邮件"""
  sender_email = "bjtu-25s-no-reply@bearingwall.top"
  sender_password = "Bjtu@2025"

  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = to_address
  msg['Subject'] = subject

  msg.attach(MIMEText(body, 'plain'))

  try:
    with smtplib.SMTP('smtp.bearingwall.top', 25) as server:
      server.starttls()
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, to_address, msg.as_string())
  except Exception as e:
    raise RuntimeError(f"Failed to send email: {e}")

def send_email_markdown(to_address: str, subject: str, markdown_body: str):
  """发送含 Markdown 内容的邮件"""
  sender_email = "bjtu-25s-no-reply@bearingwall.top"
  sender_password = "Bjtu@2025"

  # 将 Markdown 转为 HTML
  html_body = markdown.markdown(markdown_body)

  msg = MIMEMultipart('alternative')
  msg['From'] = sender_email
  msg['To'] = to_address
  msg['Subject'] = subject

  # 添加纯文本版本和 HTML 版本
  part1 = MIMEText(markdown_body, 'plain')
  msg.attach(part1)
  part2 = MIMEText(html_body, 'html')
  msg.attach(part2)

  try:
    with smtplib.SMTP('smtp.bearingwall.top', 25) as server:
      server.starttls()
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, to_address, msg.as_string())
  except Exception as e:
    raise RuntimeError(f"Failed to send email: {e}")

if __name__ == '__main__':
  sample_markdown = "# 算法设计与分析课程成绩\n\n## 基本信息\n - 测试 \n\n## 成绩\n - 期末考试：9分\n\n## 总结\n刘铎老师对你很生气。"
  try:
    send_email_markdown("23301174@bjtu.edu.cn", "测试邮件", sample_markdown)
    print("Email sent.")
  except RuntimeError as e:
    print(f"发送邮件失败: {e}")
