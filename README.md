# MVL Checker

Automated login and attendance tracker for MyVirtualLearning platform. This script logs into your MVL account, navigates to a specific course, and stays active for 3-8 minutes. It enforces a 5-day cooldown between runs to prevent excessive automation.

## Features

- Automated login with credentials from `.env` file
- Headless browser operation (runs in background)
- Random 3-8 minute session duration
- 5-day cooldown between runs
- Internet connectivity check before execution
- Debug logging for troubleshooting

## Requirements

- Python 3.7 or higher
- Chrome browser installed
- Virtual environment (recommended)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/sora598/MVL_Checker.git
cd MVL_Checker
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. Install required packages:
```bash
pip install requests selenium webdriver-manager python-dotenv
```

## Configuration

1. Create a `.env` file in the project root:
```
USERNAME=your_student_id
PASSWORD=your_password
COURSE_URL=https://www.slu.myvirtuallearning.org/course/view.php?id=YOUR_COURSE_ID
```

2. Replace the values with your actual credentials:
   - `your_student_id`: Your MVL username or student ID
   - `your_password`: Your MVL password
   - `YOUR_COURSE_ID`: The ID of the course you want to track (found in the course URL)

## Usage

Run the script using the virtual environment Python interpreter:

```bash
# Windows PowerShell
& ".venv\Scripts\python.exe" main.py

# Windows Command Prompt
.venv\Scripts\python.exe main.py

# macOS/Linux
.venv/bin/python main.py
```

### First Run

On first execution, the script will:
- Create `last_run.txt` to track execution history
- Perform the login and course navigation
- Stay active for 3-8 minutes (randomly chosen)

### Subsequent Runs

The script will only execute if:
- Internet connection is available
- At least 5 days have passed since the last successful run

If conditions are not met, you will see:
```
Condition not met: either no internet or 5 days not passed.
```

## Automated Scheduling (Optional)

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at a specific time)
4. Action: Start a program
5. Program: `C:\path\to\.venv\Scripts\python.exe`
6. Arguments: `C:\path\to\main.py`
7. Start in: `C:\path\to\project`

### Linux/macOS Cron

Add to crontab:
```bash
0 9 * * * /path/to/.venv/bin/python /path/to/main.py
```

## Debug Output

The script includes debug statements that show:
- Loaded credentials (password length only, not actual value)
- Random session duration selected
- Internet connectivity status
- Last run timestamp and eligibility
- Chrome driver initialization
- Page navigation steps
- Session completion

## Troubleshooting

### ModuleNotFoundError

Make sure you're using the virtual environment Python interpreter and all packages are installed:
```bash
.venv\Scripts\python.exe -m pip install requests selenium webdriver-manager python-dotenv
```

### Login Fails

- Verify credentials in `.env` are correct
- Check that LOGIN_URL matches your institution's MVL login page
- Ensure the username and password field IDs are "username" and "password"

### Chrome Driver Issues

webdriver-manager automatically downloads the correct ChromeDriver version. If issues persist:
- Ensure Chrome browser is installed
- Check that Chrome is up to date
- Try manually clearing the webdriver cache

### Script Runs Every Time

Check that `last_run.txt` exists and contains a valid ISO timestamp. The file should be created automatically on first run.

## File Structure

```
.
├── .env                # Credentials (DO NOT COMMIT)
├── .gitignore          # Git ignore rules
├── main.py             # Main automation script
├── last_run.txt        # Last execution timestamp (auto-generated)
└── README.md           # This file
```

## Security Notes

- Never commit `.env` to version control
- Rotate credentials regularly
- Use this tool responsibly and in accordance with your institution's policies
- The `.env` file is automatically excluded via `.gitignore`

## License

This project is provided as-is for educational purposes.
