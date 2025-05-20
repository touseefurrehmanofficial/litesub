from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)

# Function to scrape the data using Selenium
def scrape_data():
    url = "https://www.oxaam.com/serviceaccess.php?activation_key=NVJUFE7R3VBRV6P"

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    # Set up ChromeDriver service
    service = Service("/usr/bin/chromedriver")

    # Start the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)

        for attempt in range(3):
            try:
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                email_tag = soup.find('code', id='emailVal')
                password_tag = soup.find('code', id='passVal')

                email = email_tag.text if email_tag else "Email not found"
                password = password_tag.text if password_tag else "Password not found"

                latest_codes = []
                mail_section = soup.find_all('div', class_='card')

                for mail in mail_section:
                    code_tag = mail.find('div', class_='display-6')
                    date_tag = mail.find('span', class_='mail-date')

                    if code_tag and date_tag:
                        latest_codes.append({
                            "code": code_tag.text.strip(),
                            "date_time": date_tag.text.strip()
                        })

                        if len(latest_codes) == 2:
                            break

                return email, password, latest_codes

            except Exception as e:
                print(f"Attempt {attempt + 1}: Error occurred: {e}")
                if attempt < 2:
                    driver.refresh()
                    time.sleep(5)
                else:
                    return None, None, None
    finally:
        driver.quit()

@app.route('/')
def index():
    email, password, latest_codes = scrape_data()
    return render_template('index.html', email=email, password=password, latest_codes=latest_codes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=False, host="0.0.0.0", port=port)
