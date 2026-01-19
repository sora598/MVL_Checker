import os
import time
import random
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# ===== SETTINGS =====
load_dotenv(override=True)  # ensure .env wins over OS vars like Windows USERNAME

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
COURSE_URL = os.getenv("COURSE_URL")

if not USERNAME or not PASSWORD or not COURSE_URL:
    raise RuntimeError("USERNAME, PASSWORD, and COURSE_URL must be set in the .env file")

print(f"[DEBUG] Loaded USERNAME={USERNAME}, PASSWORD length={len(PASSWORD)}")
print(f"[DEBUG] COURSE_URL={COURSE_URL}")
LOGIN_URL = "https://www.slu.myvirtuallearning.org/login/index.php"
LAST_RUN_FILE = "last_run.txt"
MINUTES_TO_STAY = random.randint(3, 8)
print(f"[DEBUG] Stay duration selected: {MINUTES_TO_STAY} minutes")

# ===== CHECK INTERNET =====
def has_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        print("[DEBUG] Internet check: OK")
        return True
    except:
        print("[DEBUG] Internet check: FAILED")
        return False

# ===== CHECK 10-DAY CONDITION =====
def can_run():
    if not os.path.exists(LAST_RUN_FILE):
        print("[DEBUG] No last_run file; creating and allowing run")
        save_run_time()
        return True

    with open(LAST_RUN_FILE, "r") as f:
        last = datetime.fromisoformat(f.read().strip())

    allowed = datetime.now() - last >= timedelta(days=5)
    print(f"[DEBUG] Last run: {last.isoformat()} | Allowed now: {allowed}")
    return allowed

# ===== SAVE RUN DATE =====
def save_run_time():
    with open(LAST_RUN_FILE, "w") as f:
        f.write(datetime.now().isoformat())

# ===== AUTOMATION =====
def run():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    print("[DEBUG] Running in headless mode")

    print("[DEBUG] Initializing Chrome driver")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(LOGIN_URL)
        print("[DEBUG] Opened login page")
        time.sleep(3)

        # Find fields
        user_input = driver.find_element(By.ID, "username")
        pass_input = driver.find_element(By.ID, "password")

        user_input.send_keys(USERNAME)
        pass_input.send_keys(PASSWORD)
        pass_input.send_keys(Keys.RETURN)
        print("[DEBUG] Submitted login form")

        time.sleep(5)

        # Go to course
        driver.get(COURSE_URL)
        print("[DEBUG] Opened course page")

        # Stay 3-8 minutes
        time.sleep(MINUTES_TO_STAY * 60)
        print("[DEBUG] Completed stay")

    finally:
        print("[DEBUG] Quitting driver and saving run time")
        driver.quit()
        save_run_time()

# ===== MAIN LOGIC =====
if __name__ == "__main__":
    if has_internet() and can_run():
        print("[DEBUG] Conditions met; starting run()")
        run()
    else:
        print("Condition not met: either no internet or 10 days not passed.")
