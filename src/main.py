import schedule
import time
import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from email_sender import EmailSender
from passport_checker import PassportChecker

# Basic config
SCRIPT_DIR = Path(__file__).parent.parent.absolute()
load_dotenv()

# Configuration
CONFIG = {
    "url": "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html",
    "check_interval_minutes": 30,
    "max_retries": 3,
    "retry_wait_time": 60,
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
}

# Logging configuration
logging.basicConfig(
    filename=SCRIPT_DIR / "logs" / "passport_monitor.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    """Main function"""
    logging.info("Starting passport monitoring script")
    print(f"Script started. Checking every {CONFIG['check_interval_minutes']} minutes.")
    
    # Initialize components
    email_sender = EmailSender(
        api_key=os.getenv('SENDGRID_API_KEY'),
        sender_email=os.getenv('SENDER_EMAIL'),
        recipient_email=os.getenv('RECIPIENT_EMAIL')
    )
    
    checker = PassportChecker(CONFIG, email_sender)
    
    # First immediate check
    checker.check_status()
    
    # Schedule subsequent checks
    schedule.every(CONFIG["check_interval_minutes"]).minutes.do(checker.check_status)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main() 