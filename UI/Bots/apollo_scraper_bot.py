from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def apollo_driver_setup(apollo_username,apollo_password):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://app.apollo.io/#/login")
    time.sleep(2)
    login_email = driver.find_element(By.NAME,'email')
    login_password = driver.find_element(By.NAME,'password')
    login_email.send_keys(apollo_username)
    login_password.send_keys(apollo_password)
    time.sleep(1)
    login_password.send_keys(Keys.ENTER)
    time.sleep(2)
    return driver

def clear_input_field(element):
    element.send_keys(Keys.CONTROL + 'a')
    element.send_keys(Keys.BACKSPACE)

def fetch_mail_from_apollo(driver, key):
    try:
        search_bar = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Search Apollo"]')
        time.sleep(1)
        clear_input_field(search_bar)
        time.sleep(1)
        search_bar.send_keys(key)
        time.sleep(3)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(2)
        try:
            access_button = driver.find_element(By.XPATH, '//*[contains(text(), "Access Email & Phone")]')
            access_button.click()
            time.sleep(2)
        except:
            pass
        correct_mail = driver.find_element(By.XPATH, '//*[contains(@class, "zp-contact-email-envelope-container")]')
        time.sleep(2)
        correct_mail = correct_mail.text.split("\n")[0]
        clear_input_field(search_bar)
        return correct_mail
    except:
        return "Not found in Apollo"