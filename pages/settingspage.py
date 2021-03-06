import platform
import settings
import sys
from selenium import webdriver
import pickle, time
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from chromedriver_py import binary_path
import colorama
import json
from utils.useragentlist import user_agent

from PyQt5 import QtCore, QtGui, QtWidgets
from colorama import Fore, Style

from theming.styles import globalStyles
from utils import return_data, write_data, Encryption, data_exists, BirdLogger, validate_data


def no_abort(a, b, c):
    sys.__excepthook__(a, b, c)


sys.excepthook = no_abort
logger = BirdLogger()


class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SettingsPage, self).__init__(parent)
        self.header_font = self.create_font("Roboto", 18)
        self.small_font = self.create_font("Roboto", 13)
        self.setup_ui(self)

    def create_font(self, family, pt_size) -> QtGui.QFont:
        font = QtGui.QFont()
        font.setPointSize(pt_size) if platform.system() == "Darwin" else font.setPointSize(pt_size * .75)
        font.setFamily(family)
        font.setWeight(50)
        return font

    def create_header(self, parent, rect, font, text) -> QtWidgets.QLabel:
        header = QtWidgets.QLabel(self.settings_card)
        header.setParent(parent)
        header.setGeometry(rect)
        header.setFont(font)
        header.setStyleSheet("color: rgb(212, 214, 214);border: none;")
        header.setText(text)
        return header

    def create_checkbox(self, rect, text) -> QtWidgets.QCheckBox:
        checkbox = QtWidgets.QCheckBox(self.settings_card)
        checkbox.setGeometry(rect)
        checkbox.setStyleSheet("color: #FFFFFF;border: none;")
        checkbox.setText(text)
        return checkbox

    def create_edit(self, parent, rect, font, placeholder) -> QtWidgets.QLineEdit:
        edit = QtWidgets.QLineEdit(parent)
        edit.setGeometry(rect)
        edit.setStyleSheet("outline: 0;border: 1px solid #5D43FB;border-width: 0 0 2px;color: rgb(234, 239, 239);")
        edit.setFont(font)
        edit.setPlaceholderText(placeholder)
        edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        return edit

    def setup_ui(self, settingspage):
        self.settingspage = settingspage
        self.settingspage.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.settingspage.setGeometry(QtCore.QRect(60, 0, 1041, 601))
        self.settingspage.setStyleSheet(
            "QComboBox::drop-down {    border: 0px;}QComboBox::down-arrow {    image: url(images/down_icon.png);    width: 14px;    height: 14px;}QComboBox{    padding: 1px 0px 1px 3px;}QLineEdit:focus {   border: none;   outline: none;}")
        self.settings_card = QtWidgets.QWidget(self.settingspage)
        self.settings_card.setGeometry(QtCore.QRect(30, 70, 941, 501))
        self.settings_card.setFont(self.small_font)
        self.settings_card.setStyleSheet("background-color: #101124;border-radius: 20px;border: 1px solid #2e2d2d;")

        self.webhook_edit = self.create_edit(self.settings_card, QtCore.QRect(30, 50, 411, 21), self.small_font,
                                             "Webhook Link")
        self.webhook_header = self.create_header(self.settings_card, QtCore.QRect(20, 10, 101, 31), self.header_font,
                                                 "Webhook")

        self.savesettings_btn = QtWidgets.QPushButton(self.settings_card)
        self.savesettings_btn.setGeometry(QtCore.QRect(30, 450, 86, 32))
        self.savesettings_btn.setFont(self.small_font)
        self.savesettings_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.savesettings_btn.setStyleSheet(
            "color: #FFFFFF;background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(
                globalStyles["primary"]))
        self.savesettings_btn.setText("Save")
        self.savesettings_btn.clicked.connect(self.save_settings)

        self.browser_checkbox = self.create_checkbox(QtCore.QRect(30, 90, 300, 20), "Browser Opened")
        self.order_checkbox = self.create_checkbox(QtCore.QRect(30, 120, 221, 20), "Order Placed")
        self.paymentfailed_checkbox = self.create_checkbox(QtCore.QRect(30, 150, 121, 20), "Payment Failed")

        self.general_header = self.create_header(self.settings_card, QtCore.QRect(20, 180, 101, 31), self.header_font,
                                                 "General")
        self.onfailed_checkbox = self.create_checkbox(QtCore.QRect(30, 220, 221, 20), "Open browser on payment failed")
        self.headless_browser_checkbox = self.create_checkbox(QtCore.QRect(160, 90, 221, 20), "Headless")
        self.buy_one_checkbox = self.create_checkbox(QtCore.QRect(30, 240, 221, 20), "Stop after success")
        self.dont_buy_checkbox = self.create_checkbox(QtCore.QRect(30, 260, 290, 20),
                                                      "Don't actually buy items. (Used for dev and testing)")
        self.random_delay_start = self.create_edit(self.settings_card, QtCore.QRect(30, 310, 235, 20),
                                                   self.small_font, "Random Start Delay (Default is 10ms)")
        self.random_delay_stop = self.create_edit(self.settings_card, QtCore.QRect(30, 335, 235, 20),
                                                  self.small_font, "Random Stop Delay (Default is 40ms)")
        self.proxies_header = self.create_header(self.settingspage, QtCore.QRect(30, 10, 81, 31),
                                                 self.create_font("Roboto", 22), "Settings")
        self.gencookies_btn = QtWidgets.QPushButton(self.settings_card)
        self.gencookies_btn.setGeometry(QtCore.QRect(300, 450, 130, 32))
        self.gencookies_btn.setFont(self.small_font)
        self.gencookies_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.gencookies_btn.setStyleSheet(
            "color: #FFFFFF;background-color: {};border-radius: 10px;border: 1px solid #2e2d2d;".format(
                globalStyles["primary"]))
        self.gencookies_btn.setText("Generate Cookies")
        self.gencookies_btn.clicked.connect(self.gen_cookies)
        self.gencookies_header = self.create_header(self.settings_card, QtCore.QRect(300, 420, 300, 31), self.small_font,
                                                 "Please Generate cookie before starting using the app")
        self.gencookies_edit = self.create_edit(self.settings_card, QtCore.QRect(450, 445, 150, 31),
                                                   self.small_font, "Cookie name")


        self.set_data()
        QtCore.QMetaObject.connectSlotsByName(settingspage)

    def set_data(self):

        settings_default = return_data("./data/settings_default.json")
        if data_exists("./data/settings.json"):
            settings = return_data("./data/settings.json")
        else:
            logger.alt("Set-Settings-Data", "No existing settings found to be parsed, creating new from default.")
            write_data("./data/settings.json", settings_default)
            settings = return_data("./data/settings.json")

        if not validate_data(settings, settings_default):
            logger.error("Set-Settings-Data", "Parsed settings data is malformed! "
                                              "This will most likely cause a fatal exception. "
                                              "Try removing existing settings.json")

        self.webhook_edit.setText(settings["webhook"])
        if settings["webhookonbrowser"]:
            self.browser_checkbox.setChecked(True)
        if settings["webhookonorder"]:
            self.order_checkbox.setChecked(True)
        if settings["webhookonfailed"]:
            self.paymentfailed_checkbox.setChecked(True)
        if settings["browseronfailed"]:
            self.onfailed_checkbox.setChecked(True)
        if settings['headless_browser']:
            self.headless_browser_checkbox.setChecked(True)
        if settings['onlybuyone']:
            self.buy_one_checkbox.setChecked(True)
        if settings['dont_buy']:
            self.dont_buy_checkbox.setChecked(True)
        if settings['random_delay_start']:
            self.random_delay_start.setText(settings["random_delay_start"])
        if settings['random_delay_stop']:
            self.random_delay_stop.setText(settings["random_delay_stop"])

        self.update_settings(settings)

    def save_settings(self):
        settings = {"webhook":            self.webhook_edit.text(),
                    "webhookonbrowser":   self.browser_checkbox.isChecked(),
                    "webhookonorder":     self.order_checkbox.isChecked(),
                    "webhookonfailed":    self.paymentfailed_checkbox.isChecked(),
                    "browseronfailed":    self.onfailed_checkbox.isChecked(),
                    "headless_browser":   self.headless_browser_checkbox.isChecked(),
                    "onlybuyone":         self.buy_one_checkbox.isChecked(),
                    "dont_buy":           self.dont_buy_checkbox.isChecked(),
                    "random_delay_start": self.random_delay_start.text(),
                    "random_delay_stop": self.random_delay_stop.text(),}

        write_data("./data/settings.json", settings)
        self.update_settings(settings)
        QtWidgets.QMessageBox.information(self, "N2r Bot", "Saved Settings")

    def update_settings(self, settings_data):
        global webhook, webhook_on_browser, webhook_on_order, webhook_on_failed, browser_on_failed, headless_browser, dont_buy, random_delay_start, random_delay_stop
        settings.webhook, settings.webhook_on_browser, settings.webhook_on_order, settings.webhook_on_failed, settings.browser_on_failed, settings.headless_browser, settings.buy_one, settings.dont_buy = settings_data["webhook"], settings_data["webhookonbrowser"], settings_data["webhookonorder"], settings_data["webhookonfailed"], settings_data["browseronfailed"], settings_data['headless_browser'], settings_data['onlybuyone'], settings_data['dont_buy']

        if settings_data.get("random_delay_start", "") != "":
            settings.random_delay_start = settings_data["random_delay_start"]
        if settings_data.get("random_delay_stop", "") != "":
            settings.random_delay_stop = settings_data["random_delay_stop"]

    def gen_cookies(self):
        # open Chrome and navigate to the Newegg homepage page
        driver_manager = ChromeDriverManager()
        driver_manager.install()
        chrome_options = Options()
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument(f"User-Agent={settings.userAgent}")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(binary_path ,options=chrome_options)

        driver.maximize_window()

        time.sleep(1)
        
        driver.get("https://www.newegg.com/global/sa-en/")
        WebDriverWait(driver, 10).until(
            lambda x: "Computer parts, laptops, electronics, and more - Newegg Saudi Arabia" in driver.title
        )
        time.sleep(2)

        driver.get("https://www.newegg.com/global/sa-en/")
        print(Fore.CYAN + "Homepage reached going to login page...")
        time.sleep(1)
        driver.get("https://secure.newegg.com/global/sa-en/login/signin?nextpage=https%3A%2F%2Fwww.newegg.com%2Fglobal%2Fsa-en%2F")
        WebDriverWait(driver, 10).until(
            lambda x: "Newegg.com Sign In" in driver.title
        )
        print(Fore.CYAN + "Please insert your email and password")

        if driver.title == "Newegg.com - Protect Your Account":
                    print(Fore.CYAN + "Please verify the activity in your email fast")
                    WebDriverWait(driver, 60).until(
                    lambda x: "Computer parts, laptops, electronics, and more - Newegg Saudi Arabia" in driver.title
                    )
        
        WebDriverWait(driver, 30).until(
            lambda x: "Computer parts, laptops, electronics, and more - Newegg Saudi Arabia" in driver.title
        )
        driver.get("https://secure.newegg.com/global/sa-en/account/settings")
        time.sleep(3)
        driver.get("https://www.newegg.com/global/sa-en/")
        main_window = driver.window_handles[0]
        driver.execute_script("window.open();")
        next_window = driver.window_handles[1]
        driver.switch_to_window(next_window)
        driver.get("https://pf.newegg.com/")
        driver.switch_to_window(main_window)
        driver.refresh()

        time.sleep(2)

        print(Fore.GREEN + "Logged in successfully and generated cookies")
        if not WebDriverWait:
            print(Fore.RED + "Something went wrong please try again")
        

        pickle.dump( driver.get_cookies() , open(f"{self.gencookies_edit.text()}","wb"))
        driver.switch_to_window(next_window)
        driver.close()
        driver.switch_to_window(main_window)


        time.sleep(1)
        print(Fore.GREEN + "Everything is done bye.")
        driver.close()
