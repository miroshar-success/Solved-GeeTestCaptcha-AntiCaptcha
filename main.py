from seleniumwire import webdriver  # Import from seleniumwire to capture requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import requests
from anticaptchaofficial.geetestproxyless import geetestProxyless

# Function to get cookies in the correct format
def get_cookies_as_dict(driver):
    cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode
chrome_options.add_argument('--disable-gpu')

# Initialize the Chrome WebDriver with selenium-wire to capture requests
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.request_storage = False

# Open the webpage that contains the CAPTCHA iframe
driver.get('https://mygift.giftcardmall.com')  # Replace with the actual URL

# Wait for the page to load (you can customize the waiting time or use WebDriverWait)
time.sleep(5)

# Capture user-agent and cookies from Selenium session
user_agent = driver.execute_script("return navigator.userAgent;")
cookies = driver.get_cookies()

# Get cookies as a dictionary
cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
print("Cookies:", cookie_string)

# Loop through network requests to find the one that matches "captcha-delivery.com"
captcha_gt = None
captcha_challenge = None
for request in driver.requests:
    if 'captcha-delivery.com' in request.url:
        print('Geetest CAPTCHA request found:', request.url)
        captcha_gt = request.params.get('initialCid')
        captcha_challenge = request.params.get('hash')
        if captcha_gt and captcha_challenge:
            print('Captcha GT:', captcha_gt)
            break  # Exit loop once captcha parameters are found

# Close the browser

if captcha_gt is None or captcha_challenge is None :
    print("Error: CAPTCHA ID not found.")
else:
    # Replace with your actual Anti-Captcha API key
    api_key = "80cc74375fbf96607b121590316eb5cb"

    # Use the Geetest solver from Anti-Captcha
    solver = geetestProxyless()
    solver.set_verbose(1)
    solver.set_key(api_key)
    solver.set_website_url("https://mygift.giftcardmall.com")  # Replace with the actual website URL
    solver.set_gt_key(captcha_gt)  # Set the GT parameter
    solver.set_version(4)
    solver.set_soft_id(0)
    solver.set_challenge_key(captcha_challenge)  # Set the challenge parameter
    solver.set_user_agent(user_agent)  # Set the user-agent
    solver.set_cookies(cookie_string)  # Pass cookies as a string

    # Solve the CAPTCHA
    g_response = solver.solve_and_return_solution()

    if g_response != 0:
        print(f"CAPTCHA Solved: {g_response}")

        # Inject the CAPTCHA solution (g_response) into the hidden input field inside the iframe
        driver.execute_script(f"document.getElementById('g-recaptcha-response').value = '{g_response}';")
        
        # Submit the form inside the iframe (if there is a form to submit)
        submit_button = driver.find_element_by_xpath("//button[@type='submit']")  # Adjust the XPath according to the actual button
        submit_button.click()
        
        # Switch back to the default content after submitting the form
        driver.switch_to.default_content()
        
        # Allow time for the form submission and redirection
        time.sleep(5)
    else:
        print(f"Error solving CAPTCHA: {solver.error_code}")
        
driver.quit()
