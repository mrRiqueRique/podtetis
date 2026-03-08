from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

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

driver = webdriver.Chrome()
driver.get("https://podcastcharts.byspotify.com/br")

wait = WebDriverWait(driver, 10)

# seleciona somente os podcasts da categoria ciência
dropdown = driver.find_element(By.ID, "categoryDropdown")
dropdown.click()
buttons = driver.find_elements(By.CSS_SELECTOR, ".relative.transition-all")
for button in buttons:
    if button.text == "Ciências":
        ciencia = button    
    
ciencia.click()

time.sleep(2)

list_container = wait.until(
    expected_conditions.presence_of_element_located(
        (By.CSS_SELECTOR, ".List_list__0oF1W")
    )
)

items = list_container.find_elements(By.CSS_SELECTOR, ".Show_show__default__2x1b_")

top = [[], []]
for item in items:
    text = item.text.split('\n')
    top[0].append(text[2])
    top[1].append(text[3])

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
podcasts = dict(
    sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="info!A:B"
    ).execute()["values"]
)

for podcast in top[0]:
    if podcast in podcasts:
        podcasts[podcast] = int(podcasts[podcast]) + 1
    else:
        podcasts[podcast] = 1

# atualizar values
vezes = []
for podcast in podcasts:
    vezes.append([podcast, podcasts[podcast]])

sheet.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="info!A1",
    valueInputOption="RAW",
    body={
        "values": vezes
    }
).execute()



# vezes = sheet.values().get(
#     spreadsheetId=SPREADSHEET_ID,
#     range="info!B:B"
# ).execute()["values"]

# print(vezes)