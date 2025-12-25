import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

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
            
            # Robust Driver Finding Logic
            import shutil
            import os
            
            # Common paths for chromium-driver in Docker/Linux
            possible_driver_paths = [
                "/usr/bin/chromedriver",
                "/usr/local/bin/chromedriver",
                "/usr/lib/chromium-browser/chromedriver",
                "/usr/bin/chromium-driver",
                shutil.which("chromedriver"),
                shutil.which("chromium-driver")
            ]
            
            driver_path = None
            for p in possible_driver_paths:
                if p and os.path.exists(p):
                    driver_path = p
                    break
            
            # Common paths for Chromium binary
            possible_bin_paths = [
                 "/usr/bin/chromium",
                 "/usr/bin/chromium-browser",
                 "/usr/lib/chromium/chrome",
                 shutil.which("chromium"),
                 shutil.which("chromium-browser")
            ]
            
            bin_path = None
            for p in possible_bin_paths:
                 if p and os.path.exists(p):
                     bin_path = p
                     break
            
            logger.info(f"Selected Driver: {driver_path}, Binary: {bin_path}")
            
            if bin_path:
                options.binary_location = bin_path
            
            service = Service(driver_path) if driver_path else None
            # If service is None, Selenium will try to find it on PATH
            
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
            
            # Smart Error Detection
            if "log-in" in current_url:
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                    if "incorrect" in body_text or "invalid" in body_text or "check your email" in body_text:
                        return False, "Login Failed: Invalid Credentials"
                except:
                    pass
            
            return False, f"Current URL: {current_url} (Waiting...)"
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
            
            # Get full page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            holdings = []
            
            # Generic table scraping (robust to layout changes)
            # looking for rows with ticker-like text
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                     text_row = [c.get_text(strip=True) for c in cols]
                     # Heuristic: Check if first col looks like a ticker (3-4 chars, uppercase)
                     ticker = text_row[0]
                     if ticker.isupper() and 3 <= len(ticker) <= 5:
                         holdings.append({
                             "ticker": ticker,
                             "details": text_row
                         })
            
            # Fallback: finding divs if not a table
            if not holdings:
                 # Look for common stock codes in text
                 import re
                 text = soup.get_text()
                 candidates = re.findall(r'\b[A-Z]{3,5}\b', text)
                 # Filter common words
                 ignore = {'ASX', 'ETF', 'BUY', 'SELL', 'AUD', 'USD', 'NAV'}
                 holdings = [{"ticker": c} for c in set(candidates) if c not in ignore]

            return {
                "raw_text": "Parsed", 
                "holdings": holdings,
                "message": f"Found {len(holdings)} positions"
            }

        except Exception as e:
            logger.error(f"Scraping error: {str(e)}")
            return {"error": f"Scraping failed: {str(e)}"}

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False
