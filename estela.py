from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build



import os
import json

import time

# inicializar API do google sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=creds)

sheet = service.spreadsheets()

SPREADSHEET_ID = "1QCmmgq-d9DNWk6w2hI-FgYVHZ8qveAuov44qUiGTkYs"

#inicializar objetos
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://podcastcharts.byspotify.com/br")

wait = WebDriverWait(driver, 10)

# seleciona somente os podcasts da categoria ciência
dropdowns = wait.until(
    expected_conditions.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "button[data-encore-id='dropdown']")
    )
)

dropdown = dropdowns[2]  # "Top Podcasts"


dropdown.click()
time.sleep(2)

dropdown_list = wait.until(
    expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, "[data-encore-id='dropdownList']")
    )
)

# NOW search inside the list
options = dropdown_list.find_elements(
    By.CSS_SELECTOR, "[data-encore-id='dropdownLink']"
)

for option in options:
    if option.text == "Science":
        science = option

driver.execute_script("arguments[0].click();", science)

time.sleep(0.5)

podcast_list = wait.until(
    expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, "[class*='PodcastList_list']")
    )
)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

items = podcast_list.find_elements(By.CSS_SELECTOR, "[class*='PodcastListRow_row']")

top = [[], []]
for item in items:
    text = item.text.split('\n')
    top[0].append(text[2])
    top[1].append(text[3])
    print(top[0], top[1])
driver.quit()

currentDay = int(
    sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="config!B1"
    ).execute().get("values", [])[0][0]
) + 1


currentDay = int(currentDay)
sheet.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="config!B1",
    valueInputOption="RAW",
    body = {
    "values": [
        [str(currentDay)]
        ]
    }
).execute()

# Atualiza planilha na posição adequada
sheet.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"Página1!A{(currentDay*2) - 1}",
    valueInputOption="RAW",
    body={
        "values": top
    }
).execute()

# AGORA PRO DICIONARIO
podcasts = dict(sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="info!A:B"
    ).execute()["values"])

for i in range(len(top[0])):
    factor = (50 - i)/50
    if top[0][i] in podcasts:
        podcasts[top[0][i]] = round((float(podcasts[top[0][i]].replace(',', '.')) + factor), 4)
    else:
        podcasts[top[0][i]] = factor

# atualizar values
vezes = []
for podcast in podcasts:
    vezes.append([podcast, str(podcasts[podcast]).replace(',', '.')])
vezes.sort(key=lambda x: float(x[1]), reverse=True)

sheet.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="info!A1",
    valueInputOption="RAW",
    body={
        "values": vezes
    }
).execute()
