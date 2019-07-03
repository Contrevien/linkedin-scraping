from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import json
def search_profile_url(keyword, page):
    keyword = "%20".join(keyword.split())
    return 'https://www.linkedin.com/search/results/people/?keywords=' + keyword + '&origin=GLOBAL_SEARCH_HEADER&page=' + str(page)

def scrape_general(li):
    temp = {}
    link = ""
    try:
        link = li.find_element_by_class_name("search-result__result-link").get_attribute("href")
    except:
        return False
        
    temp["name"] = li.find_element_by_css_selector("span.actor-name").text
    temp["headline"] = li.find_element_by_css_selector("p.subline-level-1").text
    temp["location"] = li.find_element_by_css_selector("p.subline-level-2").text
    try:
        temp["extra"] = li.find_element_by_class_name("search-result__snippets").text
    except:
        temp["extra"] = ""
    return [link, temp]


def scrapeLinkedinSearch(driver, wait, keyword, page, limitResults=False):
    search_results = {}

    fp = open('in_test_generals.json', encoding="utf8")
    results = json.load(fp)
    results["old_results"].update(results["new_results"])
    results["new_results"] = {}
    driver.get(search_profile_url(keyword, page))
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    ul = driver.find_element_by_class_name("search-results__list")
    lis = ul.find_elements_by_css_selector("li.search-result")
    for i,li in enumerate(lis):
        results["progress"] = "{0}/{1}".format(i+1, len(lis))
        ret = scrape_general(li)
        if ret == False:
            print("{0}/{1} ditched".format(i+1, len(lis)))
            continue
        else:
            print("{0}/{1}".format(i+1, len(lis)))
        search_results[ret[0]] = ret[1]
        results["new_results"] = search_results
        with open("in_test_generals.json", "w", encoding="utf8") as f:
            json.dump(results, f, ensure_ascii=False)

    lis = driver.find_element_by_class_name("artdeco-pagination__pages")
    num = int(lis.find_elements_by_tag_name("li")[-1].text)
    if page < num:
        page += 1
    results["page"] = str(page)
    with open("in_test_generals.json", "w", encoding="utf8") as f:
            json.dump(results, f, ensure_ascii=False)

