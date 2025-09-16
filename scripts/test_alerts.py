import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_alert():
    """Test sending an email alert"""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')  # User's email for testing

    if not all([smtp_server, smtp_port, sender_email, sender_password, receiver_email]):
        print("❌ Email environment variables not set. Check your .env file.")
        return False

    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = "🚨 Toxicity Alert from NLP Pipeline"
        body = "This is a test alert for high toxicity detected in a live chat."
        message.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Email alert sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")
        return False

def test_telegram_alert():
    """Test sending a message via Telegram Bot"""
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not all([token, chat_id]):
        print("❌ Telegram environment variables not set. Check your .env file.")
        return False

    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text="🚨 Test alert! A toxic comment was detected in the live stream.")
        print("✅ Telegram alert sent successfully!")
        return True
    except TelegramError as e:
        print(f"❌ Failed to send Telegram alert: {e}")
        return False

if __name__ == "__main__":
    print("Testing alert systems...")
    print("\n--- Testing Email ---")
    email_success = test_email_alert()

    print("\n--- Testing Telegram ---")
    telegram_success = test_telegram_alert()

    if email_success and telegram_success:
        print("\n🎉 All alert tests passed!")
    else:
        print("\n💥 Some tests failed. Check your API keys and setup.")