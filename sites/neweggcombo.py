from selenium import webdriver
import selenium
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib import parse
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import WebDriverWait
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from utils import random_delay, send_webhook, create_msg
from utils.json_utils import find_values
from utils.selenium_utils import enable_headless
from utils.useragentlist import user_agent
import json, settings, webbrowser, urllib3, requests, time
import pickle
import random

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
except:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NEW_EGG_PDP_URL = "https://www.newegg.com/global/sa-en/Product/ComboDealDetails?ItemList={sku}"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "user-agent": user_agent,
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "origin": "https://www.newegg.com/global/sa-en/",
}

options = Options()
options.page_load_strategy = "eager"
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
options.add_argument("user-data-dir=.profile-nwcm")


class NewEggcombo:
    def __init__(self, task_id, status_signal, image_signal, product, profile, account, proxy, monitor_delay, error_delay, end_less, cookie_name):
        self.task_id, self.status_signal, self.image_signal, self.product, self.profile, self.account, self.monitor_delay, self.error_delay, self.end_less, self.cookie_name = task_id, status_signal, image_signal, product, profile, account, float(
            monitor_delay), float(error_delay), end_less, cookie_name

        self.sku_id = parse.parse_qs(parse.urlparse(self.product).query)['ItemList'][0]
        self.session = requests.Session()
        normal_browser = "Starting Normal browser Not Headless"
        endless_msg = "Endless Buy is on"
        starting_msg = "Starting Newegg Combo"
        self.browser = self.init_driver()

        self.SHORT_TIMEOUT = 5
        self.LONG_TIMEOUT = 20

        if settings.headless_browser:
            normal_browser = "Starting in headless."

        if settings.dont_buy:
            starting_msg = "Starting Newegg Combo in dev mode; will not actually checkout."
        
        self.status_signal.emit(create_msg(normal_browser, "normal"))
        self.status_signal.emit(create_msg(starting_msg, "normal"))
        if self.end_less != False:
            self.status_signal.emit(create_msg(endless_msg, "normal"))

        if proxy:
            self.session.proxies.update(proxy)

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            )
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        response = self.session.get(
            NEW_EGG_PDP_URL.format(sku=self.sku_id), headers=DEFAULT_HEADERS
        )

        self.status_signal.emit(create_msg(f"PDP Request: {response.status_code}", "normal"))
        if response.status_code == 400:
            self.status_signal.emit(create_msg(f"Error page: {response.status_code}", "error"))
        self.product = response.url
        self.status_signal.emit(create_msg(f"Product URL: {self.product}", "normal"))
        self.session.get(self.product)
        self.status_signal.emit(create_msg(f"Product URL Request: {response.status_code}", "normal"))
        self.status_signal.emit(create_msg("Loading headless driver.", "normal"))

        headless = True
        if headless:
            enable_headless()

        self.status_signal.emit(create_msg("Loading https://www.newegg.com/global/sa-en/", "normal"))
        self.login()

        self.browser.get(self.product)
        cookies = self.browser.get_cookies()

        [
            self.session.cookies.set_cookie(
                requests.cookies.create_cookie(
                    domain=cookie["domain"],
                    name=cookie["name"],
                    value=cookie["value"]
                )
            )
            for cookie in cookies
        ]

        self.check_stock()

    def init_driver(self):
        driver_manager = ChromeDriverManager()
        driver_manager.install()
        chrome_options = Options()
        if settings.headless_browser:
            chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--window-size=1920,1080")
        # change_driver(self.status_signal, driver_path)
        browser = webdriver.Chrome(binary_path ,options=chrome_options)

        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                  Object.defineProperty(navigator, 'webdriver', {
                   get: () => undefined
                  })
                """
        })


        return browser
    

    def login(self):
        
        self.status_signal.emit(create_msg("Logging In..", "normal"))

        self.browser.maximize_window()
        
        self.browser.get("https://www.newegg.com/global/sa-en/")
        
        time.sleep(5)

        cookies = pickle.load(open(f'{self.cookie_name}', "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)

        self.status_signal.emit(create_msg("Cookies Loaded", "normal"))
        
        

        if self.browser.title == "Are you a human?":
            self.browser.close()
            self.status_signal.emit(create_msg("Captacha Detected Stopping", "error"))
            time.sleep(2)
        
        time.sleep(.1)

        self.browser.get("https://www.newegg.com/global/sa-en/")

        #wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.LINK_TEXT, "MY ACCOUNT")))
        time.sleep(1)
        # self.browser.find_element_by_link_text('MY ACCOUNT').click()

        # wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "signIn"))).click()
        # wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div/div[1]/form/div/div[1]/div'))).click()

        # email = self.browser.find_element_by_id("labeled-input-signEmail")
        # email.send_keys(self.account["account_email"])

        # wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signInSubmit"]')))
        # sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signInSubmit"]')
        # sign_in_btn.click()

        # try:
        #     time.sleep(3)

        #     password = self.browser.find_element_by_id("labeled-input-password")
        #     password.send_keys(self.account["account_pass"])
        #     wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signInSubmit"]')))
        #     sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signInSubmit"]')
        #     sign_in_btn.click()
        # except (ElementNotVisibleException, NoSuchElementException):
        #     self.status_signal.emit(create_msg("Didn't find password field", "normal"))
        
        # time.sleep(.5) # slight delay for in-between filling out login info and clicking Sign In
        # if self.browser.title == "Newegg.com - Protect Your Account":
        #     self.status_signal.emit(create_msg("Verify the activtiy in your email", "normal"))
        # else:
        #     pass


    
    def check_stock(self):
        while not self.in_stock():
            time.sleep(
                random_delay(self.monitor_delay, settings.random_delay_start, settings.random_delay_stop))
        self.status_signal.emit(create_msg(f"Item {self.sku_id} is in stock!", "normal"))
        self.monitor()

    def in_stock(self):

        self.status_signal.emit(create_msg("Checking stock", "normal"))
        url = "https://www.newegg.com/global/sa-en/Product/ComboDealDetails?ItemList={}".format(
            self.sku_id
        )
        # TODO: Add random delay configuration
        response = self.session.get(url, headers=DEFAULT_HEADERS)
        self.status_signal.emit(create_msg(f"Stock check response code: {response.status_code} {url}", "normal"))
        if response.status_code == 400:
            self.status_signal.emit(create_msg(f"Error page: {response.status_code} {url}", "error"))
        if response.status_code == 403:
            self.status_signal.emit(create_msg(f"Error page: {response.status_code} {url}", "error"))
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            in_stock_divs = soup.find("a", {"class": "atnPrimary"})  # <--- change "text" to div
            self.status_signal.emit(create_msg(f"Button Status: {in_stock_divs}", "normal"))
            if "<h2>Are you a human?</h2>" in response.text:
                self.status_signal.emit(create_msg(f"Error page: Captcha detected {url}", "error"))
            if "atnPrimary" in response.text: #TODO: Make this case insensitive
                self.status_signal.emit(create_msg("Item is in stock!", "normal"))
                return True
            else:
                self.status_signal.emit(create_msg("Item is out of stock", "normal"))
                return False
        except Exception as e:
            self.status_signal.emit(create_msg("Error parsing json. Using string search to determine state.", "error"))
            self.status_signal.emit(create_msg(f"{e}", "error"))


    def monitor(self):

        self.status_signal.emit(create_msg("Going to the product", "normal"))

        image_found = False
        self.product_image = ""
        
        self.browser.maximize_window()

        self.browser.get(self.product)
        wait(self.browser, self.LONG_TIMEOUT).until(lambda _: self.browser.current_url == self.product)

        in_stock = False

        while not in_stock:
            try: 
                wait(self.browser, random_delay(self.monitor_delay, settings.random_delay_start, settings.random_delay_stop)).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="synopsis"]/div[2]/div[2]/div/div[1]/div/div[3]/a')))
                add_to_cart_btn = self.browser.find_element_by_xpath('//*[@id="synopsis"]/div[2]/div[2]/div/div[1]/div/div[3]/a')
                if not image_found:
                    self.product_image = self.browser.find_element_by_xpath("//meta[@property='og:image']").get_attribute("content")
                    self.image_signal.emit(self.product_image)
                    image_found = True
                add_to_cart_btn.click()
                time.sleep(.5)
                if not self.browser.current_url == "https://secure.newegg.com/global/sa-en/Shop/Cart?submit=view":
                    self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
                    self.browser.execute_script("location.reload(true);")
                    continue
                if self.browser.title == "Are you a human?":
                    self.browser.close()
                    self.status_signal.emit(create_msg("Captacha Detected Stopping", "error"))
                    time.sleep(2)
                    
                in_stock = True
                self.status_signal.emit(create_msg("Adding to cart", "normal"))
                self.add_to_cart()
            except:
                if not self.browser.current_url == "https://secure.newegg.com/global/sa-en/Shop/Cart?submit=view":
                    self.status_signal.emit(create_msg("Waiting For Restock", "normal"))
                    self.browser.execute_script("location.reload(true);")
                    continue
                if self.browser.title == "Are you a human?":
                    self.browser.close()
                    self.status_signal.emit(create_msg("Captacha Detected Stopping", "error"))
                    time.sleep(2)

    def add_to_cart(self):
        WebDriverWait(self.browser, 10).until(
            lambda x: "Newegg.com Shopping Cart" in self.browser.title
        )
        checkout_btn = self.browser.find_element_by_xpath('//*[@id="app"]/div[2]/section/div/div/form/div[2]/div[3]/div/div/div[3]/div/button')
        time.sleep(.1)
        self.browser.get("https://www.newegg.com/global/sa-en/")
        time.sleep(.3)
        cookies = pickle.load(open(f'{self.cookie_name}', "rb"))
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        self.status_signal.emit(create_msg("Cookies loaded", "normal"))
        self.browser.get("https://secure.newegg.com/global/sa-en/Shop/Cart?submit=view")
        wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/section/div/div/form/div[2]/div[3]/div/div/div[3]/div/button'))).click()
        time.sleep(2)
        if self.browser.title == "Newegg.com Sign In":
            self.status_signal.emit(create_msg("Login page found logging in", "normal"))
            # email = self.browser.find_element_by_id("labeled-input-signEmail")
            # email.clear()
            # email.send_keys(self.account["account_email"])
            # sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signInSubmit"]')
            # sign_in_btn.click()
            self.status_signal.emit(create_msg("Email entered", "normal"))
            time.sleep(1.5)
            self.browser.find_element_by_xpath('//*[@id="signInSubmit"]').click()
            if self.browser.title == "Newegg.com - Protect Your Account":
                self.status_signal.emit(create_msg("Please verify the activity in your email fast", "normal"))
                time.sleep(9)
                self.browser.get("https://www.newegg.com/global/sa-en/")
                time.sleep(2)
                pickle.dump( self.browser.get_cookies() , open(f"{self.cookie_name}","wb"))
                self.status_signal.emit(create_msg("Cookies Dumped", "normal"))
                self.browser.get("https://secure.newegg.com/global/sa-en/Shop/Cart?submit=view")

            wait(self.browser, 7).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div/div[2]/form/div/div[2]/div')))

            password = self.browser.find_element_by_id("labeled-input-password")
            password.send_keys(self.account["account_pass"])
            time.sleep(.5)
            sign_in_btn = self.browser.find_element_by_xpath('//*[@id="signInSubmit"]')
            sign_in_btn.click()
            self.status_signal.emit(create_msg("Password entered", "normal"))
            time.sleep(1)
            self.browser.get("https://www.newegg.com/global/sa-en/")
            time.sleep(.2)
            pickle.dump( self.browser.get_cookies() , open(f"{self.cookie_name}","wb"))
            self.status_signal.emit(create_msg("Cookies Dumped", "normal"))
            self.browser.get("https://secure.newegg.com/global/sa-en/Shop/Cart?submit=view")
        else:
            self.status_signal.emit(create_msg("Password not found Continuing", "normal"))

        try:
            if self.browser.title == "Newegg.com Shopping Cart":
                wait(self.browser, 6).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/section/div/div/form/div[2]/div[3]/div/div/div[3]/div/button'))).click()
        except (TimeoutException, NoSuchElementException,
                StaleElementReferenceException) as e:
                pass
        self.status_signal.emit(create_msg("carted", "carted"))
        self.submit_billing()



    def submit_billing(self):
        WebDriverWait(self.browser, 10).until(
        lambda x: "Newegg.com Checkout" in self.browser.title
        )

        self.status_signal.emit(create_msg("Entering National ID #", "normal"))
        continue_to_taxid = wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="deliveryItemCell"]/div/div[3]/button')))
        continue_to_taxid.click()

        wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, "form-text.is-wide")))
        nat_input = self.browser.find_element_by_xpath('//*[@id="taxIDItemCell"]/div/div[2]/div/div[2]/div[4]/input')
        nat_input.send_keys(self.profile["nationalid"])
        continue_to_payment = self.browser.find_element_by_xpath('//*[@id="taxIDItemCell"]/div/div[3]/button')
        continue_to_payment.click()

        self.status_signal.emit(create_msg("Entering CVV #", "normal"))
        wait(self.browser, self.LONG_TIMEOUT).until(EC.visibility_of_element_located((By.XPATH, "//input[@class='form-text mask-cvv-4'][@type='text']")))
        cvv_input = self.browser.find_element_by_xpath("//input[@class='form-text mask-cvv-4'][@type='text']")
        time.sleep(.1)
        cvv_input.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + self.profile["card_cvv"])
        order_review_btn = self.browser.find_element_by_xpath('//*[@id="paymentItemCell"]/div/div[3]/button')
        order_review_btn.click()
        self.submit_order()

    def submit_order(self):
        WebDriverWait(self.browser, 10).until(
            lambda x: "Newegg.com Checkout" in self.browser.title
        )

        self.status_signal.emit(create_msg("Submitting Order..", "normal"))
        time.sleep(.5)

        if not settings.dont_buy:
            order_buy_btn = wait(self.browser, self.LONG_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnCreditCard"]')))
            order_buy_btn.click()
            self.status_signal.emit(create_msg("Order Placed", "normal"))
            send_webhook("OP", "NewEggcombo", self.profile["profile_name"], self.product, self.account["account_name"], self.product_image)
            self.payment_auth()
        else:
            send_webhook("OP", "NewEggcombo", self.profile["profile_name"], self.product, self.account["account_name"], self.product_image)
            self.browser.get("https://www.newegg.com/global/sa-en/")
            time.sleep(.5)
            pickle.dump( self.browser.get_cookies() , open(f"{self.cookie_name}","wb"))
            time.sleep(.5)
            self.browser.close()
            self.status_signal.emit(create_msg("Mock Order Placed", "success"))

    def payment_auth(self):
        try:
            WebDriverWait(self.browser, 4).until(
                lambda x: "Newegg.com Authentication" in self.browser.title
            )
            self.status_signal.emit(create_msg("Newegg auth page found", "normal"))
        except (TimeoutException, NoSuchElementException,
                StaleElementReferenceException) as e:
                self.status_signal.emit(create_msg("Newegg auth page not found skipping", "normal"))
                pass
        try:
            WebDriverWait(self.browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@id='Cardinal-CCA-IFrame']")))
            WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ExitLink"]'))).click()
            time.sleep(2)
            self.status_signal.emit(create_msg("Payment auth skipped", "normal"))
        except (TimeoutException, NoSuchElementException,
                StaleElementReferenceException) as e:
                self.status_signal.emit(create_msg("Payment auth not found hmmm", "normal"))
                pass
        self.browser.get("https://www.newegg.com/global/sa-en/")
        time.sleep(.5)
        pickle.dump( self.browser.get_cookies() , open(f"{self.cookie_name}","wb"))
        if self.end_less != False:
            self.monitor()
        self.browser.close()

        self.status_signal.emit(create_msg("Order secured", "success"))
