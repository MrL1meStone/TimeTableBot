from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import openpyxl
import os
def parsing_html(path=r"C:\WebDrivers\WebDriverschromedriver140\chromedriver.exe", regime="PC"):
    # Путь к chromedriver
    chromedriver_path = path
    regimes = {"PC" : r"C:\Users\Валентин\Downloads\\", "server" : ""}
    # Настройка сервиса и опций
    service = Service(chromedriver_path)
    options = Options()
    # options.add_argument("--headless")  # если хотите запускать без окна браузера
    # Создаем драйвер
    driver = webdriver.Chrome(service=service, options=options)
    time.sleep(9)  # ждем загрузки страницы (лучше использовать WebDriverWait)
    wait = WebDriverWait(driver, 13)
    actions = ActionChains(driver)
    try:
        with open('schedule.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
        with open('schedule.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)
    try:
        # Открываем Google Диск (пример)
        driver.get("https://drive.google.com/drive/folders/1jfQFPUpOuv_tNLyQIoipPVsLQHv_H5UQ")
        # Ждем появления элементов с классом KL4NAf (файлы)
        file_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "KL4NAf")))
        current_files, new_files = [], []
        with open('schedule.json', 'r', encoding='utf-8') as file1:
            data1 = json.load(file1)
        for file in file_elements:
            current_files.append(file.text)
        download_container = wait.until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.YM8blb.M3pype")))
        doc_list = {}
        for i in range(len(current_files)):
            if not(current_files[i] in data1):
                document = {}
                actions.move_to_element(file_elements[i]).perform()
                # Внутри этого контейнера ищем кнопку с aria-label="Скачать"
                download_button = download_container[i].find_element(By.CSS_SELECTOR, "div[aria-label='Скачать']")
                # Кликаем по кнопке
                download_button.click()
                time.sleep(10)
                workbook = openpyxl.load_workbook(regimes['PC']+current_files[i])
                sheet = workbook.active
                for row in sheet.iter_rows():
                    rowl = []
                    for cell in row:
                        if cell.value is not None:
                            rowl.append(cell.value)
                            #  print(cell.value)
                    document[row] = rowl
                doc_list[current_files[i]] = list(document.values())
                path = regimes['PC']+current_files[i]
                os.remove(path)
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(current_files, f)
        return doc_list
    finally:
        driver.quit()
p = parsing_html()
for p1 in p:
    print(p1)
    for p2 in p[p1]:
        print(p2)
        print()
