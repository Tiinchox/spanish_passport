import requests
from bs4 import BeautifulSoup
import schedule
import time
from plyer import notification
import logging
from datetime import datetime
import json
from pathlib import Path
import random

# Configuration
CONFIG = {
    "url": "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html",
    "check_interval_minutes": 30,
    "max_retries": 3,
    "retry_wait_time": 60,  # seconds
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
}

# Logging configuration
logging.basicConfig(
    filename='passport_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File to store the last known state
LAST_STATE_FILE = Path("last_state.json")

def save_last_state(state):
    try:
        with open(LAST_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving last state: {e}")

def load_last_state():
    try:
        if LAST_STATE_FILE.exists():
            with open(LAST_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading last state: {e}")
    return {"last_opening": "", "next_opening": ""}

def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon="favicon.ico",
            timeout=20
        )
        logging.info(f"Notification sent: {title} - {message}")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

def check_passport_status():
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
            rows = soup.find_all("tr")
            
            last_state = load_last_state()
            
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3 and "Pasaportes" in cells[0].text and "renovación y primera vez" in cells[0].text:
                    last_opening = cells[1].text.strip()
                    next_opening = cells[2].text.strip()
                    
                    current_state = {
                        "last_opening": last_opening,
                        "next_opening": next_opening
                    }
                    
                    # Check for changes
                    if current_state != last_state:
                        message = (
                            f"Changes detected!\n"
                            f"Last opening: {last_opening}\n"
                            f"Next opening: {next_opening}"
                        )
                        
                        if next_opening.lower() != "fecha por confirmar":
                            send_notification(
                                "New Passport Appointment Date Available!",
                                message
                            )
                        else:
                            send_notification(
                                "Passport Status Changes",
                                message
                            )
                        
                        save_last_state(current_state)
                        logging.info(f"Changes detected: {message}")
                    
                    return True
            
            logging.warning("Passport row not found in the table")
            return False

        except requests.RequestException as e:
            logging.error(f"Error in attempt {attempt + 1}/{CONFIG['max_retries']}: {e}")
            if attempt < CONFIG["max_retries"] - 1:
                time.sleep(CONFIG["retry_wait_time"])
            else:
                send_notification(
                    "Verification Error",
                    "Could not access the consulate website"
                )
                return False

def scheduled_check():
    logging.info("Starting scheduled check")
    check_passport_status()

def main():
    logging.info("Starting passport monitoring script")
    print(f"Script started. Checking every {CONFIG['check_interval_minutes']} minutes.")
    print(f"Logs are saved in: {Path('passport_monitor.log').absolute()}")
    
    # First immediate check
    scheduled_check()
    
    # Schedule subsequent checks
    schedule.every(CONFIG["check_interval_minutes"]).minutes.do(scheduled_check)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()