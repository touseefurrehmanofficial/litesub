from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape the data using Selenium
def scrape_data():
    url = "https://www.oxaam.com/serviceaccess.php?activation_key=NVJUFE7R3VBRV6P"

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

    # Specify the relative path to ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the webpage
    driver.get(url)

    # Allow page to load and refresh if necessary
    time.sleep(5)  # Wait for content to load

    # Retry in case elements are dynamically loaded or the page is updating
    for attempt in range(3):  # Try up to 3 times
        try:
            # Extract the full page source
            page_source = driver.page_source

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract email and password
            email_tag = soup.find('code', id='emailVal')
            password_tag = soup.find('code', id='passVal')

            email = email_tag.text if email_tag else "Email not found"
            password = password_tag.text if password_tag else "Password not found"

            # Extract the latest authentication codes and their timestamps
            latest_codes = []
            mail_section = soup.find_all('div', class_='card')

            # Extract the first two available codes and their timestamps
            for mail in mail_section:
                code_tag = mail.find('div', class_='display-6')
                date_tag = mail.find('span', class_='mail-date')
                
                if code_tag and date_tag:
                    latest_codes.append({
                        "code": code_tag.text.strip(),
                        "date_time": date_tag.text.strip()
                    })
                    
                    if len(latest_codes) == 2:  # Stop after extracting two codes
                        break

            # Close the browser
            driver.quit()

            return email, password, latest_codes

        except Exception as e:
            print(f"Attempt {attempt + 1}: Error occurred: {e}")
            if attempt < 2:  # Refresh and try again
                print("Refreshing the page and trying again...")
                driver.refresh()
                time.sleep(5)  # Wait for content to reload
            else:
                driver.quit()
                return None, None, None


@app.route('/')
def index():
    # Scrape the data
    email, password, latest_codes = scrape_data()

    # Render the HTML template with the scraped data
    return render_template('index.html', email=email, password=password, latest_codes=latest_codes)

if __name__ == "__main__":
    app.run(debug=True, port=3000)
