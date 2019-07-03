from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
import os
import getpass
from scrapeLinkedInAccounts import scrapeLinkedInAccounts, login
from scrapeLinkedinSearch import scrapeLinkedinSearch
import json

ch = os.getcwd() + '/tools/chromedriver.exe'

options = Options()
options.add_argument("--headless")
options.add_argument("log-level=3")
options.add_argument("--incognito")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options, executable_path=ch)
wait = WebDriverWait(driver, 10)
driver.implicitly_wait(0.5)

try:
    driver.get("https://www.linkedin.com/login/")

    fp = open('in_test_generals.json', encoding="utf8")
    results = json.load(fp)

    # results["old_results"] = {}
    # results["new_results"] = {}
    # results["progress"] = ""
    # results["page"] = "1"

    results["old_results"].update(results["new_results"])
    with open('in_test_generals.json', 'w') as f:
        json.dump(results, f)


    time.sleep(1)
    print("Welcome to linkedin test")
    time.sleep(1)
    username = input("Please enter your linkedin username: ")
    password = getpass.getpass()
    print("trying to log in...")
    login(driver, wait, username, password)

    if 'checkpoint/challenge' in driver.current_url:
        code = input("Please enter the verification code on your registered EMail: ")
        driver.find_element_by_id("input__email_verification_pin").send_keys(code)
        driver.find_element_by_id("email-pin-submit-button").click()

        if 'feed' in driver.current_url:
            pass
        else:
            print("Wrong code, exiting...")
            exit()

    elif 'feed' in driver.current_url:
        pass
    else:
        print("Wrong crendentials, exiting...")
        exit()

    print("logged in")
    time.sleep(1)
    keyword = input("Enter keyword: ")
    print("searching for people with that keyword...")

    # done = False
    # while not done:
    #     fp = open('in_test_generals.json', encoding="utf8")
    #     results = json.load(fp)
    #     page = results["page"]
    #     scrapeLinkedinSearch(driver, wait, keyword, int(page))
    #     if input("Do you want to scrape more results? (y/n): ") not in ["y", "Y"]:
    #         done = True

    # fp = open('in_test_generals.json', encoding="utf8")
    # results = json.load(fp)
    # results["old_results"].update(results["new_results"])

    # with open('in_test_generals.json', 'w') as f:
    #     json.dump(results, f)

    print("Demonstrating full profile scrape...")

    print("Dumped the results in in_test_generals.json")
    time.sleep(1)

    print("Demonstrating full profile scraping using these proflies")
    time.sleep(1)

    fp = open('in_test_generals.json', encoding="utf8")
    test = json.load(fp)["old_results"]
    data = {}
    for i,link in enumerate(test.keys()):
        try:
            print("{0}/{1}".format(i,len(test.keys())))
            data[link] = scrapeLinkedInAccounts(driver, wait, link)
        except:
            continue
    with open("in_test_complete.json", "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)

except:
    print("something went wrong")
driver.quit()