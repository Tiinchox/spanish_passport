# Passport Appointment Monitor

A Python script that monitors the Spanish consulate website for passport appointment availability and sends email notifications when changes are detected.

## Features

- Automatically checks the consulate website every 30 minutes
- Sends email notifications when appointment dates change
- Runs in the background as a Windows scheduled task
- Logs all activities and changes
- Uses SendGrid for email delivery

## Requirements

- Python 3.8 or higher
- Windows OS
- Internet connection
- SendGrid account (free trial available)

## Quick Start

1. Clone or download this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your SendGrid credentials:
   ```
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDER_EMAIL=your_verified_email@domain.com
   RECIPIENT_EMAIL=your_email@domain.com
   ```

## Configuration

The script uses the following settings (in `main.py`):
- Check interval: 30 minutes
- Maximum retries: 3
- Retry wait time: 60 seconds
- Log file: `passport_monitor.log`
- State file: `last_state.json`

## Usage

### Automatic Startup

1. Run `setup_autostart.bat` as administrator
2. The script will:
   - Detect Python installation
   - Check for virtual environment
   - Create a Windows scheduled task
   - Configure the task to run at login

### Manual Testing

1. Run the script directly:
   ```bash
   python main.py
   ```
2. Or use Task Scheduler to run the "PassportMonitor" task

## Files

- `main.py`: Main script
- `setup_autostart.bat`: Automatic startup configuration
- `requirements.txt`: Python dependencies
- `passport_monitor.log`: Activity log
- `last_state.json`: Last known appointment dates
- `.env`: Email configuration

## Troubleshooting

If the script doesn't work:

1. Check the log file for errors
2. Verify the scheduled task exists and is enabled
3. Ensure Python and dependencies are installed correctly
4. Check your SendGrid credentials in the `.env` file

## Notes

- Email notifications are sent using SendGrid
- The script runs with highest privileges
- All files are created in the script's directory

## License

This project is open source and available under the MIT License. 