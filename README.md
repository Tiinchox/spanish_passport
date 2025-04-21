# Passport Appointment Monitor

A Python script that monitors the Spanish consulate website for passport appointment availability and sends desktop notifications when changes are detected.

## Features

- Automatically checks the consulate website every 30 minutes
- Sends desktop notifications when appointment dates change
- Runs in the background as a Windows scheduled task
- Logs all activities and changes
- Supports virtual environment for dependency isolation

## Requirements

- Python 3.8 or higher
- Windows operating system
- Internet connection

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The script uses the following configuration (in `main.py`):
- Check interval: 30 minutes
- Maximum retries: 3
- Retry wait time: 60 seconds
- Log file: `passport_monitor.log`
- State file: `last_state.json`

## Usage

### Automatic Startup Setup

1. Run `setup_autostart.bat` as administrator
2. The script will:
   - Detect Python installation
   - Check for virtual environment
   - Create a Windows scheduled task named "PassportMonitor"
   - Configure the task to run at login

### Manual Testing

1. Run the script directly:
   ```bash
   python main.py
   ```
2. Or use the Task Scheduler to run the "PassportMonitor" task

### Monitoring

- Check the log file (`passport_monitor.log`) for script activity
- Desktop notifications will appear when changes are detected
- The task runs automatically when you log in to Windows

## Files

- `main.py`: Main script file
- `setup_autostart.bat`: Script to configure automatic startup
- `requirements.txt`: Python package dependencies
- `passport_monitor.log`: Activity log file
- `last_state.json`: Last known state of appointment dates

## Troubleshooting

If the script doesn't work as expected:

1. Check the log file for errors
2. Verify the scheduled task exists and is enabled
3. Ensure Python and all dependencies are installed correctly
4. Check that the virtual environment is properly set up

## Notes

- Notifications appear in the Windows notification area
- The script runs with highest privileges to ensure proper operation
- All files are created in the script's directory

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License. 