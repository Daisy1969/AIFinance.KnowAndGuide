import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperheroSecureConnector:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False

    def start_login_session(self, username=None, password=None):
        """
        Launches a headless Chrome browser and logs in using provided credentials.
        """
        try:
            options = Options()
            options.add_argument("--headless") # Must be headless in Docker
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            # Use webdriver_manager to get the driver (or system driver)
            # In Docker, we installed chromium-driver, so we might need to point to it
            # or ChromeDriverManager might find it if configured correctly.
            # Using default for now, hoping webdriver_manager handles it.
            
            # For Docker (Alpine/Debian), we often need:
            options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")

            self.driver = webdriver.Chrome(service=service, options=options)
            
            logger.info("Opening Superhero login page...")
            self.driver.get("https://app.superhero.com.au/log-in")
            
            if username and password:
                return self.perform_login(username, password)
            
            return True, "Browser opened (Headless). Waiting for logic."
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return False, f"Failed to start browser: {str(e)}"

    def perform_login(self, username, password):
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Email
            logger.info("Entering email...")
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            email_field.send_keys(username)
            
            # Password
            logger.info("Entering password...")
            pass_field = self.driver.find_element(By.NAME, "password")
            pass_field.clear()
            pass_field.send_keys(password)
            
            # Submit
            logger.info("Clicking login...")
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()
            
            # Wait for success or MFA
            # Check for URL change or MFA field
            time.sleep(5) # Brief wait for transition
            
            if "mfa" in self.driver.current_url or "otp" in self.driver.current_url:
                return True, "MFA Required"
            
            if "dashboard" in self.driver.current_url or "portfolio" in self.driver.current_url:
                self.is_logged_in = True
                return True, "Login Successful"
                
            return True, "Login submitted. Check status."
            
        except Exception as e:
            logger.error(f"Login Automation Failed: {e}")
            return False, f"Login Automation Failed: {str(e)}"

    def check_login_status(self):
        """
        Checks if the user has successfully logged in.
        Returns (bool, str): (is_logged_in, current_url)
        """
        if not self.driver:
            return False, "Browser not started"

        try:
            current_url = self.driver.current_url
            if "dashboard" in current_url or "portfolio" in current_url:
                self.is_logged_in = True
                return True, "Login Detected"
            
            return False, f"Current URL: {current_url}"
        except Exception as e:
            return False, f"Error checking status: {str(e)}"

    def get_portfolio_holdings(self):
        """
        Scrapes the portfolio holdings from the dashboard.
        Assumes user is logged in.
        """
        if not self.driver or not self.is_logged_in:
            return {"error": "Not logged in"}

        try:
            # Wait for the portfolio table or list to load
            logger.info("Scraping portfolio...")
            # For robustness, we will take a screenshot in debug mode if needed
            # self.driver.save_screenshot("/app/debug_portfolio.png")
            
            # Simplest extraction: Get page text. Refine later with specific selectors.
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # TODO: Add specific parsing for Ticker/Units
            
            return {"raw_text": body_text, "message": "Data extracted"}

        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            return {"error": f"Scraping failed: {str(e)}"}

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False
