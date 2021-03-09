from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import re
import sys
import requests

def get_credentials():
    try:
        file = open('credentials.txt', "r")
        credentials = file.readlines()
        file.close()
        return credentials
    except:
         raise Exception("No se encontró el archivo credentials.txt")

def init_driver(timeout):
    options = Options()
    options.headless = True
    options.add_argument('log-level=2')
    driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')
    driver.maximize_window()
    driver.implicitly_wait(timeout)
    return driver

def get_cabal_page(driver):
    print("ingresando en cabal one...")
    driver.get("https://cabal.one/")

def log_in(driver, credentials):
    print("ingresando credenciales...")
    driver.find_element_by_xpath("//a[@class='cc-btn cc-dismiss']").click()
    driver.find_element_by_xpath("//a[@data-title='LOGIN']").click()
    driver.find_element_by_id("loginform-username").send_keys(credentials[0])
    driver.find_element_by_id("loginform-password").send_keys(credentials[1])
    driver.find_element_by_xpath("//button[@class='button-big']").click()
    time.sleep(2)
    error = driver.find_element_by_xpath("//p[@class='help-block help-block-error']").text
    if (len(error) > 0):
        raise Exception(error)
    
def vote(driver, number):
    countdown = None
    print("votando en sitio " + str(number) + "...")
    driver.get("https://cabal.one/site/vote?id=" + str(number))
    time.sleep(3)
    title = driver.title
    print(title)
    if title == "Cabal One - Vote":
        try:
          countdown = driver.find_element_by_class_name("event-timer").text
        except:
          countdown = "12 hrs"
    else:
        countdown = "12 hrs"
    return countdown

def print_coins(driver):
    print("verificando coins...")
    driver.get("https://cabal.one/account")
    time.sleep(2)
    print(driver.find_element_by_xpath("//tbody/tr[7]").text)

def teardown_driver(driver):
    driver.close()

def calculate_next_iteration(countdown):
    hours = minutes = seconds = None
    try:
        hours = re.findall(r'\d+(?= hr)', countdown)[0]
    except:
        hours = 0
    try:
        minutes = re.findall(r'\d+(?= min)', countdown)[0]
    except:
        minutes = 0
    try:
        seconds = re.findall(r'\d+(?= sec)', countdown)[0]
    except:
        seconds = 0
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    return total_seconds

def get_timeout():
    try:
        timeout = sys.argv[1]
    except:
        timeout = 30
    return int(timeout)

def has_internet(timeout):
    url = "https://cabal.one/"
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False

def vote_cabal(timeout):
        start_time = time.time()
        credentials = get_credentials()
        driver = init_driver(timeout)
        get_cabal_page(driver)
        log_in(driver, credentials)
        print_coins(driver)
        countdown_text1 = vote(driver, 1)
        countdown1 = calculate_next_iteration(countdown_text1)
        countdown_text2 = vote(driver, 2)
        countdown2 = calculate_next_iteration(countdown_text2)
        print_coins(driver)
        checkgoals(driver)
        teardown_driver(driver)
        final_countdown = countdown2 if countdown2 > countdown1 else countdown1
        total_hours = final_countdown/3600
        execution_time = round(time.time() - start_time, 2)
        print("----- ejecutado en " + str(execution_time) + " segundos -----")
        print("----- esperando " + str(round(total_hours, 2)) + " horas (" + str(final_countdown) + " segundos) -----")
        time.sleep(final_countdown)
        
def main():
    while True:
        timeout = get_timeout()
        if (has_internet(timeout)):
            print("timeout: " + str(timeout))
            vote_cabal(timeout)
        else:
            print("no se detecto conexion a internet, intentando nuevamente en 10 minutos...")
            time.sleep(600)

def checkgoals(driver):
    driver.get("https://cabal.one/account/goals")
    print("verificando goals...")
    goals = driver.find_elements_by_xpath("//button[@data-progress=100]")
    print("goals reclamables: " + str(len(goals)))
    goals_url = []
    for index, goal in enumerate(goals):
        goal_url = "https://cabal.one" + goal.get_attribute("data-url")
        goals_url.append(goal_url)
    for index, goal_url in enumerate(goals_url):
        print("reclamando goal " + str(index + 1) + "...")
        time.sleep(2)
        driver.get(goal_url)

main()
    
    

    


