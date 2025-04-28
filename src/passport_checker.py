import requests
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path
import random
import time

class PassportChecker:
    def __init__(self, config, email_sender):
        self.config = config
        self.email_sender = email_sender
        self.script_dir = Path(__file__).parent.parent.absolute()
        self.last_state_file = self.script_dir / "data" / "last_state.json"

    def get_passport_dates(self):
        """Get passport appointment dates from the website"""
        headers = {
            "User-Agent": random.choice(self.config["user_agents"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
        }

        for attempt in range(self.config["max_retries"]):
            try:
                response = requests.get(self.config["url"], headers=headers, timeout=30)
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
                logging.error(f"Error in attempt {attempt + 1}/{self.config['max_retries']}: {e}")
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(self.config["retry_wait_time"])
                else:
                    self.email_sender.send(
                        "Verification Error",
                        "Could not access the consulate website"
                    )
                    return None

    def check_status(self):
        """Check for changes in appointment dates"""
        current_state = self.get_passport_dates()
        if not current_state:
            return

        try:
            last_state = json.loads(self.last_state_file.read_text()) if self.last_state_file.exists() else {}
        except Exception as e:
            logging.error(f"Error loading last state: {e}")
            last_state = {}

        if current_state != last_state:
            message = (
                f"Changes detected in passport appointment dates!\n\n"
                f"Last opening: {current_state['last_opening']}\n"
                f"Next opening: {current_state['next_opening']}\n\n"
                f"Please visit the website for more information: {self.config['url']}"
            )
            
            subject = "New Passport Appointment Date Available!" if current_state['next_opening'].lower() != "fecha por confirmar" else "Passport Appointment Status Changes"
            self.email_sender.send(subject, message)
            
            try:
                self.last_state_file.write_text(json.dumps(current_state, indent=2))
            except Exception as e:
                logging.error(f"Error saving state: {e}") 