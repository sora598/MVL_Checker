import logging
import os
import time
import random
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# ===== SETTINGS =====
load_dotenv(override=True)  # ensure .env wins over OS vars like Windows USERNAME

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
COURSE_URL = os.getenv("COURSE_URL")
COURSE_URL_2 = os.getenv("COURSE_URL_2")

if not USERNAME or not PASSWORD or not COURSE_URL or not COURSE_URL_2:
    raise RuntimeError("USERNAME, PASSWORD, COURSE_URL, and COURSE_URL_2 must be set in the .env file")

LOGIN_URL = "https://www.slu.myvirtuallearning.org/login/index.php"
LAST_RUN_FILE = "last_run.txt"
LOG_FILE = "mvl.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
MINUTES_TO_STAY = random.randint(3, 8)
TOTAL_SECONDS = MINUTES_TO_STAY * 60
FIRST_WAIT = int((TOTAL_SECONDS // 2) * random.uniform(1.2, 1.5))
SECOND_WAIT = int((TOTAL_SECONDS // 2) * random.uniform(1.2, 1.5))

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("Loaded USERNAME=%s, PASSWORD length=%s", USERNAME, len(PASSWORD))
logging.info("COURSE_URL=%s", COURSE_URL)
logging.info("COURSE_URL_2=%s", COURSE_URL_2)
logging.info("First wait: %s seconds, Second wait: %s seconds (Total: %s minutes)", FIRST_WAIT, SECOND_WAIT, (FIRST_WAIT + SECOND_WAIT) / 60)

# ===== CLEANUP LOG FILE =====
def check_and_cleanup_log():
    if os.path.exists(LOG_FILE):
        log_size = os.path.getsize(LOG_FILE)
        if log_size > LOG_MAX_SIZE:
            try:
                os.remove(LOG_FILE)
                print(f"Log file exceeded {LOG_MAX_SIZE / (1024*1024):.1f}MB; deleted")
            except Exception as exc:
                print(f"Failed to delete log file: {exc}")

# ===== CHECK INTERNET =====
def has_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        logging.info("Internet check: OK")
        return True
    except Exception as exc:
        logging.warning("Internet check failed: %s", exc)
        return False

# ===== CHECK 10-DAY CONDITION =====
def can_run():
    if not os.path.exists(LAST_RUN_FILE):
        logging.info("No last_run file; creating and allowing run")
        save_run_time()
        return True

    with open(LAST_RUN_FILE, "r") as f:
        last = datetime.fromisoformat(f.read().strip())

    allowed = datetime.now() - last >= timedelta(days=5)
    logging.info("Last run: %s | Allowed now: %s", last.isoformat(), allowed)
    return allowed

# ===== SAVE RUN DATE =====
def save_run_time():
    with open(LAST_RUN_FILE, "w") as f:
        f.write(datetime.now().isoformat())

# ===== AUTOMATION =====
def run():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")
    logging.info("Running in headless mode (with anti-bot and explicit waits)")

    logging.info("Initializing Chrome driver with webdriver-manager")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(LOGIN_URL)
        logging.info("Opened login page")

        # Use explicit waits for visibility and enter credentials
        user_input = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        user_input.clear()
        user_input.send_keys(USERNAME)
        logging.info("Entered username")
        
        # Wait a moment and refind password field to avoid stale element
        time.sleep(0.5)
        pass_input = wait.until(EC.visibility_of_element_located((By.ID, "password")))
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        logging.info("Entered password")

        # Try JavaScript click on login button as fallback
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "loginbtn")))
            driver.execute_script("arguments[0].click();", submit_btn)
            logging.info("Clicked login button with JS")
        except Exception as e:
            try:
                login_form = driver.find_element(By.ID, "login")
                driver.execute_script("arguments[0].submit();", login_form)
                logging.info("Submitted login form using JavaScript fallback")
            except Exception as e2:
                logging.error("Failed to submit form: %s, fallback: %s", e, e2)
                raise

        # Wait for navigation to complete (URL change or dashboard loaded)
        try:
            wait.until(lambda d: d.current_url != LOGIN_URL or "dashboard" in d.current_url)
        except Exception as e:
            logging.warning("URL did not change after login: %s", e)
        logging.info("Current URL after login: %s", driver.current_url)

        # Save screenshot and HTML for debugging
        driver.save_screenshot("headless_debug.png")
        with open("headless_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)


        # Go to course with retry
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                driver.get(COURSE_URL)
                logging.info(f"Opened primary course page: {COURSE_URL} (Attempt {attempt})")
                logging.info(f"Current URL: {driver.current_url}")
                break
            except Exception as e:
                logging.error(f"Failed to open primary course (Attempt {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(3)
                else:
                    raise

        # Stay half the total duration on primary
        logging.info("Staying on primary course for %s seconds", FIRST_WAIT)
        for i in range(FIRST_WAIT):
            time.sleep(1)
            # Keep connection alive by checking status every 10 seconds
            if i % 10 == 0:
                try:
                    driver.title  # Just access a property to keep connection alive
                except:
                    pass
        logging.info("Completed primary stay (%s seconds)", FIRST_WAIT)

        # Visit secondary course page
        driver.get(COURSE_URL_2)
        logging.info("Opened secondary course page: %s", COURSE_URL_2)

        # Stay remaining half on secondary
        logging.info("Staying on secondary course for %s seconds", SECOND_WAIT)
        for i in range(SECOND_WAIT):
            time.sleep(1)
            # Keep connection alive by checking status every 10 seconds
            if i % 10 == 0:
                try:
                    driver.title  # Just access a property to keep connection alive
                except:
                    pass
        logging.info("Completed secondary stay (%s seconds)", SECOND_WAIT)

    except Exception as e:
        logging.error("Error during automation: %s", e, exc_info=True)
        raise
    finally:
        logging.info("Quitting driver and saving run time")
        driver.quit()
        save_run_time()

# ===== MAIN LOGIC =====
if __name__ == "__main__":
    try:
        check_and_cleanup_log()
        if has_internet() and can_run():
            logging.info("Conditions met; starting run()")
            run()
        else:
            logging.info("Condition not met: either no internet or 10 days not passed.")
    except Exception:
        logging.exception("Unhandled error during execution")
