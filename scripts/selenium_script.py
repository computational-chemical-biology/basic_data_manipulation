from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # example
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
html_source = driver.page_source
html_source_code = driver.execute_script("return document.body.innerHTML;")

options = webdriver.ChromeOptions()
custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
options.add_argument(f'--user-agent={custom_user_agent}')
options.add_argument('--headless')
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
html_source = driver.page_source
html_source_code = driver.execute_script("return document.body.innerHTML;")

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': custom_user_agent})
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    # other user agents...
]
options = webdriver.ChromeOptions()
options.add_argument(f'--user-agent={user_agents[1]}')
options.add_argument('--headless')
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
html_source = driver.page_source

driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--enable-javascript")
options.add_argument(f'--user-agent={user_agents[1]}')
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
html_source = driver.page_source

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--enable-javascript")
options.add_argument(f'--user-agent={user_agents[1]}')
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
driver.implicitly_wait(10)
html = driver.page_source

from pyppeteer import launch
import asyncio
from bs4 import BeautifulSoup

async def main(): 
    browser = await launch() 
    page = await browser.newPage() 
    await page.goto('http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/') 
    html = await page.content() 
    await browser.close() 
    soup = BeautifulSoup(html, 'html.parser') 
    return soup

s = asyncio.get_event_loop().run_until_complete(main())

from requests_html import HTMLSession
session = HTMLSession()
r = session.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
r.html.render()
r.html.html

import requests
url = "http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/"

s = requests.Session()
s.cookies["cf_clearance"] = "cb4c883efc59d0e990caf7508902591f4569e7bf-1617321078-0-150"
s.headers.update({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        })
r = s.get(url)
r.text

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # example
driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
driver = webdriver.Remote("http://chrome:4444/wd/hub", options=options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/") 

myElem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'h4')))  

WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "h4")))
time.sleep(1)
titles = []
txt = []
dts = []
#followers_els = driver.find_elements_by_css_selector(".item-value-data")
title_els = driver.find_elements(By.TAG_NAME, "h4")
for el in title_els:
    titles.append(el.text)

txt_els = driver.find_elements(By.TAG_NAME, "p")
for el in txt_els:
    txt.append(el.text)

dts_els = driver.find_elements(By.CLASS_NAME, "datas") 
for el in dts_els:
    dts.append(el.text)

from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
driver.get("http://memoria2.cnpq.br/web/guest/chamadas-publicas?p_p_id=resultadosportlet_WAR_resultadoscnpqportlet_INSTANCE_0ZaM&filtro=abertas/")
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME, "h4")))
time.sleep(1)
titles = []
txt = []
dts = []
#followers_els = driver.find_elements_by_css_selector(".item-value-data")
title_els = driver.find_elements(By.TAG_NAME, "h4")
for el in title_els:
    titles.append(el.text)

