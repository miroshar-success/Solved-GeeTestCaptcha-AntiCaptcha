from seleniumwire import webdriver  # Import from seleniumwire to capture requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
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
chrome_options.add_argument('--disable-gpu')

# Initialize the Chrome WebDriver with selenium-wire to capture requests
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.request_storage = False

# Open the webpage that contains the CAPTCHA iframe
driver.get('https://mygift.giftcardmall.com')  # Replace with the actual URL

# Wait for the page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

# Capture user-agent and cookies from Selenium session
user_agent = driver.execute_script("return navigator.userAgent;")
cookies = driver.get_cookies()

# Get cookies as a dictionary
cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
print("Cookies:", cookie_string)

# Switch to iframe that contains the CAPTCHA
iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'captcha-delivery.com')]")))
driver.switch_to.frame(iframe)

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

# Return to main content from iframe
driver.switch_to.default_content()

if captcha_gt is None or captcha_challenge is None:
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

        # Switch to the CAPTCHA iframe again
        driver.switch_to.frame(iframe)

        # Inject the CAPTCHA solution (g_response) into the hidden input field inside the iframe
        # driver.execute_script(f"document.getElementById('geetest_validate').value = '{g_response}';")

        # Execute JavaScript to trigger CAPTCHA submission
        # driver.switch_to.default_content()

        # Inject and execute the JavaScript code for captchaCallback (from your provided code)
        
        
        
        lot_number = g_response['lot_number']
        gen_time = g_response['gen_time']
        pass_token = g_response['pass_token']
        captcha_output = g_response['captcha_output']
        captcha_id = g_response['captcha_id']
        isOffline = 'true' if g_response['isOffline'] is True else 'false'
        
        
        js_code = f"""
        ddm.cid = '{captcha_gt}';
        ddm.hash = '{captcha_challenge}';
        
        console.log(ddm);

        window.captchaResponse = {{
            lot_number: '{lot_number}',
            gen_time: {gen_time},
            pass_token: '{pass_token}',
            captcha_output: '{captcha_output}',
            captcha_id: '{captcha_id}',
            isOffline: {isOffline},
        }};
        window.captchaCallback();
        """
        
        driver.execute_script(js_code)

        # Wait for the submission and the page to reload
        time.sleep(15)

        # Check if the CAPTCHA was successfully solved and the page navigated
        print("CAPTCHA bypassed and form submitted. Proceeding to next page.")
    else:
        print(f"Error solving CAPTCHA: {solver.error_code}")

# while True:
#     key = input("Press 'x' to continue: ")
#     if key.lower() == 'x':
#         break
