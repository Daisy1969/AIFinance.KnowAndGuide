import time
import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class SuperheroConnector:
    def __init__(self):
        print("Initializing Browser Agent...")
        # Use webdriver_manager to get matching driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.base_url = "https://app.superhero.com.au"

    def login_check(self):
        """
        Navigates to Superhero and waits for user to log in manually.
        """
        print(f"Navigating to {self.base_url}")
        self.driver.get(self.base_url)
        print(">>> ACTION REQUIRED: Please Log In to Superhero in the opened browser window.")
        print("Waiting for login (looking for 'Portfolio' or 'Wallet' element)...")
        
        try:
            # Wait up to 5 minutes for user to login
            WebDriverWait(self.driver, 300).until(
                lambda d: "login" not in d.current_url and ("dashboard" in d.current_url or "portfolio" in d.current_url)
            )
            print("Login confirmed!")
        except Exception as e:
             print("Login timeout or detection failed. Please ensure you are logged in.")
             # Continue anyway to allow testing if detection flaked
             
    def draft_trade(self, ticker, action, units):
        print(f"Drafting Order: {action.upper()} {units} x {ticker}")
        
        try:
            # 1. Search for Ticker
            # Note: Selectors (.css-...) are unstable in React apps. 
            # We use generic attributes or text where possible.
            
            # Click Search input
            # Placeholder might be 'Search by company or code'
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Search']"))
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(ticker)
            time.sleep(2) # Wait for dropdown
            
            # Select first result
            search_box.send_keys(Keys.ENTER)
            time.sleep(3) # Wait for page load
            
            # 2. Click Buy/Sell
            # Look for button with text "Buy" or "Sell"
            action_btn = self.driver.find_element(By.XPATH, f"//button[contains(., '{action.title()}')]")
            action_btn.click()
            time.sleep(1)
            
            # 3. Enter Units (or Value)
            # Switch to 'Units' mode if necessary. Assume default or find toggle.
            
            # Find input for quantity. Often type='number' or has label 'Quantity'
            qty_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='number']")
            qty_input.click()
            qty_input.send_keys(str(units))
            
            # 4. Review Order
            review_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Review')]")
            review_btn.click()
            
            print(">>> SUCCESS: Trade drafted and Review screen open.")
            print(">>> SAFETY STOP: Automated execution halted. Please review and submit manually.")
            
        except Exception as e:
            print(f"Failed to draft trade: {e}")
            print("Ensure you are on the correct page and the ticker exists.")

    def close(self):
        input("Press Enter to close the browser agent...")
        self.driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Superhero Client Agent")
    parser.add_argument("--ticker", required=True, help="ASX Ticker (e.g. BHP)")
    parser.add_argument("--action", default="buy", choices=["buy", "sell"])
    parser.add_argument("--units", type=int, default=1)
    
    args = parser.parse_args()

    agent = SuperheroConnector()
    try:
        agent.login_check()
        agent.draft_trade(args.ticker, args.action, args.units)
    finally:
        agent.close()
