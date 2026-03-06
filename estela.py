from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import time

# inicializar API do google sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=creds)

sheet = service.spreadsheets()

SPREADSHEET_ID = "1QCmmgq-d9DNWk6w2hI-FgYVHZ8qveAuov44qUiGTkYs"
RANGE = "Página1!A1:C10"


# inicializar objetos
driver = webdriver.Chrome()
driver.get("https://podcastcharts.byspotify.com/br")
wait = WebDriverWait(driver, 10)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)

list_container = wait.until(
    expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, ".List_list__0oF1W")
    )
)

items = list_container.find_elements(By.CSS_SELECTOR, ".Show_show__default__2x1b_")

top = []
for item in items:
    text = item.text.split('\n')
    podcast = [text[2], text[3]]
    top.append(podcast)

driver.quit()

body = {
    "values": top
}

sheet.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="Página1!A1",
    valueInputOption="RAW",
    body=body
).execute()