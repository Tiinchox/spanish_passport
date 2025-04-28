import requests
from bs4 import BeautifulSoup
import schedule
import time
import logging
import json
from pathlib import Path
import random
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Basic config
SCRIPT_DIR = Path(__file__).parent.absolute()
load_dotenv()

# CGE and email config
CONFIG = {
    "url": "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html",
    "check_interval_minutes": 30,
    "max_retries": 3,
    "retry_wait_time": 60,
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ],
    "email": {
        "sender": os.getenv("SENDER_EMAIL"),
        "recipient": os.getenv("RECIPIENT_EMAIL")
    }
}

# Logging config
logging.basicConfig(
    filename=SCRIPT_DIR / "passport_monitor.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def send_email(subject, message):
    """Send email using SendGrid"""
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        mail = Mail(
            from_email=CONFIG['email']['sender'],
            to_emails=CONFIG['email']['recipient'],
            subject=subject,
            plain_text_content=message
        )
        response = sg.send(mail)
        logging.info(f"Email sent successfully. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def get_passport_dates():
    """Obtiene las fechas de citas del sitio web"""
    headers = {
        "User-Agent": random.choice(CONFIG["user_agents"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
    }

    for attempt in range(CONFIG["max_retries"]):
        try:
            response = requests.get(CONFIG["url"], headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 3 and "Pasaportes" in cells[0].text and "renovación y primera vez" in cells[0].text:
                    return {
                        "last_opening": cells[1].text.strip(),
                        "next_opening": cells[2].text.strip()
                    }
            logging.warning("Passport row not found in the table")
            return None

        except requests.RequestException as e:
            logging.error(f"Error in attempt {attempt + 1}/{CONFIG['max_retries']}: {e}")
            if attempt < CONFIG["max_retries"] - 1:
                time.sleep(CONFIG["retry_wait_time"])
            else:
                send_email(
                    "Verification Error",
                    "Could not access the consulate website"
                )
                return None

def check_passport_status():
    """Check any changes in the appointment dates"""
    current_state = get_passport_dates()
    if not current_state:
        return

    last_state_file = SCRIPT_DIR / "last_state.json"
    try:
        last_state = json.loads(last_state_file.read_text()) if last_state_file.exists() else {}
    except Exception as e:
        logging.error(f"Error loading last state: {e}")
        last_state = {}

    if current_state != last_state:
        message = (
            f"Changes detected in passport appointment dates!\n\n"
            f"Last opening: {current_state['last_opening']}\n"
            f"Next opening: {current_state['next_opening']}\n\n"
            f"Please visit the website for more information: {CONFIG['url']}"
        )
        
        subject = "New Passport Appointment Date Available!" if current_state['next_opening'].lower() != "fecha por confirmar" else "Passport Appointment Status Changes"
        send_email(subject, message)
        
        try:
            last_state_file.write_text(json.dumps(current_state, indent=2))
        except Exception as e:
            logging.error(f"Error saving state: {e}")

def main():
    logging.info("Starting passport monitoring script")
    print(f"Script started. Checking every {CONFIG['check_interval_minutes']} minutes.")
    
    # First immediate check
    check_passport_status()
    
    # Schedule subsequent checks
    schedule.every(CONFIG["check_interval_minutes"]).minutes.do(check_passport_status)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()