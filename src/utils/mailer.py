import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from pathlib import Path

def send_html_report(subject: str, html_body: str):
    recipients = [e.strip() for e in open(Path("config/recipients.txt")) if e.strip()]
    if not recipients: return
    u, p = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")
    if not u or not p: logger.error("🔐 缺失邮箱Secrets"); return
    
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, u, ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as s:
            s.login(u, p); s.sendmail(u, recipients, msg.as_string())
        logger.info(f"📧 HTML报告推送成功 ({len(recipients)}个)")
    except Exception as e: logger.error(f"📧 发送失败: {e}")
