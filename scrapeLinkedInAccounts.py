from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import json

errors = {}

def search_profile_url(searchType, keyword, page):
    keyword = "%20".join(keyword.split())
    return 'https://www.linkedin.com/search/results/' + searchType.lower() + '/?keywords=' + keyword + '&origin=GLOBAL_SEARCH_HEADER&page=' + str(page)

def login(driver, wait, userid, password):
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element_by_id("username").send_keys(userid)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_elements_by_class_name("btn__primary--large")[0].click()

def special_exp_scrape(li, ul):
    try:
        obj = {}
        text = li.text.split("\n")
        if text[0] == "Company Name":
            obj["company"] = text[1]
        try:
            obj["linkToCompany"] = li.find_element_by_tag_name(
                "a").get_attribute("href")
        except:
            obj["linkToCompany"] = "NA"
        if text[2] == "Total Duration":
            obj["totalDuration"] = text[3]
        obj["roles"] = []
        for x in ul.find_elements_by_css_selector("div.pv-entity__role-details-container"):
            temp = {}
            content = x.text.split("\n")
            temp["title"] = content[1]
            if len(text) > 2:
                for i in range(2, len(text), 2):
                    if text[i] == "Dates Employed":
                        temp["dates"] = text[i+1]
                    if text[i] == "Employment Duration":
                        temp["duration"] = text[i+1]
                    if text[i] == "Location":
                        temp["location"] = text[i+1]
            obj["roles"].append(temp)
        return obj
    except:
        return -1


def normal_exp_scrape(li):
    try:
        obj = {}
        text = li.text.split("\n")
        obj["company"] = text[2]
        try:
            obj["linkToCompany"] = li.find_element_by_tag_name("a").get_attribute("href")
        except:
            obj["linkToCompany"] = "NA"
        obj["title"] = text[0]
        if len(text) > 3:
            for i in range(3, len(text), 2):
                if text[i] == "Dates Employed":
                    obj["dates"] = text[i+1]
                if text[i] == "Employment Duration":
                    obj["duration"] = text[i+1]
                if text[i] == "Location":
                    obj["location"] = text[i+1]
        return obj
    except Exception as e:
        print(e)
        return -1


def scrape_experiences(driver, wait):
    exp_sec = ""
    try:
        exp_sec = driver.find_element_by_id("experience-section")
    except:
        return "NA"
    while True:
        try:
            exp_sec = driver.find_element_by_id("experience-section")
            el = exp_sec.find_element_by_class_name("pv-profile-section__see-more-inline")
            driver.execute_script("arguments[0].click();", el)
        except:
            break
    exp_sec = driver.find_element_by_id("experience-section")
    ul = exp_sec.find_element_by_tag_name("ul")
    exps = []
    for li in ul.find_elements_by_css_selector("li.pv-profile-section"):
        try:
            inner_ul = li.find_element_by_tag_name("ul")
            temp = special_exp_scrape(li, inner_ul)
            if temp == -1:
                continue
            exps.append(temp)
        except:
            temp = normal_exp_scrape(li)
            if temp == -1:
                continue
            exps.append(normal_exp_scrape(li))
    return exps


def scrape_education(driver, wait):
    edu_sec = ""
    try:
        edu_sec = driver.find_element_by_id("education-section")
    except:
        return "NA"
    while True:
        try:
            edu_sec = driver.find_element_by_id("education-section")
            el = edu_sec.find_element_by_class_name("pv-profile-section__see-more-inline")
            driver.execute_script("arguments[0].click();", el)
        except:
            break
    edu_sec = driver.find_element_by_id("education-section")
    ul = edu_sec.find_element_by_tag_name("ul")
    edu = []
    for li in ul.find_elements_by_css_selector("li.pv-profile-section__section-info-item"):
        obj = {}
        text = li.text.split("\n")
        obj["institution"] = text[0]
        try:
            obj["linkToInstitution"] = li.find_element_by_tag_name("a").get_attribute("href")
        except:
            obj["linkToInstitution"] = "NA"
        if len(text) > 1:
            for i in range(1, len(text), 2):
                if text[i] == "Degree Name":
                    obj["degree"] = text[i+1]
                if text[i] == "Field Of Study":
                    obj["fieldOfStudy"] = text[i+1]
                if "Dates" in text[i]:
                    obj["duration"] = text[i+1]
        edu.append(obj)
    return edu


def scrape_skills(driver, wait):
    skills = ""
    try:
        skills = driver.find_element_by_class_name("pv-skill-categories-section")
    except:
        return "NA"
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.pv-skills-section__additional-skills"))).click()
    except Exception as e:
        print(e)
    skillsArray = []
    for li in skills.find_elements_by_css_selector("li.pv-skill-category-entity"):
        try:
            temp = {}
            name = li.find_element_by_css_selector("div.pv-skill-category-entity__skill-wrapper")
            values = name.text.split("\n")
            temp["skill"] = values[0]
            try:
                count = name.find_element_by_class_name("pv-skill-category-entity__endorsement-count").text
                if count == "99+":
                    count = 99
                temp["endorsements"] = int(count)
            except:
                temp["endorsements"] = 0
            skillsArray.append(temp)
        except:
            continue
    return skillsArray


def scrape_recommendations(driver, wait, rec_sec):
    try:
        ul = rec_sec.find_element_by_tag_name("ul")
    except:
        return "NA"
    while True:
        try:
            driver.execute_script("arguments[0].click();", rec_sec.find_element_by_class_name("pv-profile-section__see-more-inline"))
        except:
            break
    recs = []
    for li in ul.find_elements_by_css_selector("li.pv-recommendation-entity"):
        temp = {}
        text = li.text.split("\n")
        temp["name"] = text[0]
        try:
            temp["linkToProfile"] = li.find_element_by_tag_name("a").get_attribute("href")
        except:
            temp["linkToProfile"] = "NA"
        temp["headline"] = text[1]
        temp["date"] = ",".join(text[2].split(",")[:2])
        temp["relation"] = text[2].split(",")[2]
        temp["content"] = " ".join(text[3:])
        recs.append(temp)
    return recs

def scrape_hardest(el, heading):
    temp = {}
    if heading == "honors":
        try:
            temp["title"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["issuer"] = el.find_element_by_class_name("pv-accomplishment-entity__issuer").text.split("\n")[1]
        except:
            temp["issuer"] = "NA"
        try:
            temp["description"] = " ".join(el.find_element_by_class_name("pv-accomplishment-entity__description").text.split("\n")[1:])
        except:
            temp["description"] = "NA"
    if heading == "certifications":
        try:    
            temp["name"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["license"] = el.find_element_by_class_name("pv-accomplishment-entity__license").text
        except:
            temp["license"] = "NA"
        try:
            temp["issuer"] = el.find_element_by_class_name("pv-accomplishment-entity__photo").text.split("\n")[1]
        except:
            temp["issuer"] = "NA"
    if heading == "projects":
        try:
            temp["title"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["description"] = " ".join(el.find_element_by_class_name("pv-accomplishment-entity__description").text.split("\n")[1:])
        except:
            temp["description"] = "NA"
    if heading == "publications":
        try:
            temp["name"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["publisher"] = el.find_element_by_class_name("pv-accomplishment-entity__publisher").text.split("\n")[1]
        except:
            temp["publisher"] = "NA"
        try:
            temp["description"] = " ".join(el.find_element_by_class_name("pv-accomplishment-entity__description").text.split("\n")[1:])
        except:
            temp["description"] = "NA"
    if heading == "testScores":
        try:
            temp["name"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["score"] = ""
            dirty = el.find_element_by_class_name("pv-accomplishment-entity__score").text
            for d in dirty:
                if d != " " and d != "\n":
                    temp["score"] += d
        except:
            temp["score"] = "NA"
        try:
            temp["description"] = " ".join(el.find_element_by_class_name("pv-accomplishment-entity__description").text.split("\n")[1:])
        except:
            temp["description"] = "NA"
    if heading == "languages":
        try:
            return el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
    if heading == "courses":
        try:
            temp["name"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["courseNumber"] = el.find_element_by_class_name("pv-accomplishment-entity__course-number").text.split("\n")[1]
        except:
            temp["courseNumber"] = "NA"
    if heading == "organizations":
        try:
            temp["name"] = el.find_element_by_class_name("pv-accomplishment-entity__title").text.split("\n")[1]
        except:
            return -1
        try:
            temp["date"] = el.find_element_by_class_name("pv-accomplishment-entity__date").text.split("\n")[1]
        except:
            temp["date"] = "NA"
        try:
            temp["position"] = el.find_element_by_class_name("pv-accomplishment-entity__position").text.split("\n")[1]
        except:
            temp["position"] = "NA"
    return temp

def scrape_accomplishments(driver, wait):
    i = 0
    temp = {}
    acc = driver.find_element_by_class_name("pv-accomplishments-section")
    for sec in acc.find_elements_by_css_selector("section.pv-accomplishments-block"):
        driver.execute_script('document.querySelector(".pv-accomplishments-section").querySelectorAll(".pv-accomplishments-block__expand")[' + str(i) + '].click()')    
        heading = sec.find_element_by_css_selector("h3.pv-accomplishments-block__title").text.lower()
        if len(heading) == 0:
            continue
        if "honors" in heading:
            heading = "honors"
        if "test" in heading:
            heading = "test-scores"
        while True:
            try:
                driver.execute_script("arguments[0].click();", sec.find_element_by_css_selector("button.pv-profile-section__see-more-inline"))
            except:
                break
        if heading[-1] != "s":
            heading += "s"
        try:
            new_sec = driver.find_element_by_class_name(heading)    
        except:
            continue
        if heading == "test-scores":
            heading = "testScores"
        temp[heading] = []
        for li in new_sec.find_elements_by_class_name("pv-accomplishment-entity--expanded"):
            lo = scrape_hardest(li, heading)
            if lo == -1:
                continue
            temp[heading].append(lo)
        driver.execute_script('document.querySelector(".pv-accomplishments-section").querySelectorAll(".pv-accomplishments-block__expand")[' + str(i) + '].click()')    
        i += 1
    return temp

def scrape_current(driver, wait, x):
    arr = []
    for li in driver.find_elements_by_class_name("entity-list-item"):
        temp = {}
        text = li.text.split("\n")
        try:
            if x != "groups":
                temp["name"] = text[0]
                temp["link"] = li.find_element_by_tag_name("a").get_attribute("href")
                temp["followers"] = int("".join(text[-2][:-9].split(",")))
            else:
                temp["name"] = text[0]
                temp["link"] = li.find_element_by_tag_name("a").get_attribute("href")
                temp["members"] = int("".join(text[-1][:-7].split(",")))
        except:
            continue
        arr.append(temp)
    return arr


def scrape_interests(driver, wait):
    modal = driver.find_element_by_class_name("artdeco-modal")
    nav = modal.find_element_by_tag_name("nav")
    i = 0
    interests = {}
    links = []
    seq = []
    for a in nav.find_elements_by_tag_name("a"):
        links.append(a.get_attribute("href"))
        interests[a.text.lower()] = []
        seq.append(a.text.lower())
    for link in links:
        if i != 0:
            driver.get(link)
        interests[seq[i]] = scrape_current(driver, wait, seq[i])
        i += 1
    return interests

def scroll_all(driver, wait):
    profile_scroll = 100
    prevTop = -1
    while True:
        driver.execute_script("window.scrollTo(0, " + str(profile_scroll) + ");")
        time.sleep(0.2)
        if prevTop == driver.execute_script("return window.pageYOffset;"):
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            break
        prevTop = driver.execute_script("return window.pageYOffset;")
        profile_scroll += 500


def scrape_profile(driver, wait):
    obj = {}

    card = driver.find_element_by_class_name("pv-top-card-v3")
    our = card.find_element_by_class_name("mt2")
    uls = our.find_elements_by_tag_name("ul")

    try:
        obj["name"] = uls[0].find_elements_by_tag_name("li")[0].text
        if "name" in errors.keys():
            errors["name"] = 0
    except:
        obj["name"] = "NA"
        if "name" in errors.keys():
            errors["name"] += 1
        else:
            errors["name"] = 0

    try:
        obj["headline"] = our.find_element_by_tag_name("h2").text
        if "headline" in errors.keys():
            errors["headline"] = 0
    except:
        obj["headline"] = "NA"
        if "headline" in errors.keys():
            errors["headline"] += 1
        else:
            errors["headline"] = 0

    try:
        obj["location"] = uls[1].find_elements_by_tag_name("li")[0].text
        if "location" in errors.keys():
            errors["location"] = 0
    except:
        obj["location"] = "NA"
        if "location" in errors.keys():
            errors["location"] += 1
        else:
            errors["location"] = 0
    
    try:
        obj["connections"] = uls[1].find_elements_by_tag_name("li")[1].text.split()[1]
        if "connections" in errors.keys():
            errors["connections"] = 0
    except:
        obj["connections"] = "NA"
        if "connections" in errors.keys():
            errors["connections"] += 1
        else:
            errors["connections"] = 0

    scroll_all(driver, wait)

    obj["experience"] = scrape_experiences(driver, wait)
    obj["education"] = scrape_education(driver, wait)
    obj["skills"] = scrape_skills(driver, wait)
    rec_sec = ""
    try:
        rec_sec = driver.find_element_by_class_name("pv-recommendations-section")
    except:
        return "NA"
    artdecos_switch = rec_sec.find_elements_by_tag_name("artdeco-tab")
    artdecos = rec_sec.find_elements_by_tag_name("artdeco-tabpanel")
    for x in artdecos_switch:
        if "Received" in x.text:
            obj["recommendationsReceived"] = scrape_recommendations(driver, wait, artdecos[0])
            if len(artdecos_switch) == 2:
                driver.execute_script("arguments[0].click();", artdecos_switch[1])
        if "Given" in x.text:
            obj["recommendationsGiven"] = scrape_recommendations(driver, wait, artdecos[1])

    obj["accomplishments"] = scrape_accomplishments(driver, wait)

    driver.get(driver.current_url + "detail/interests")
    obj["interests"] = scrape_interests(driver, wait)

    return obj


def scrapeLinkedInAccounts(driver, wait, link, limitResults=0):
    driver.get(link)
    return scrape_profile(driver, wait)
