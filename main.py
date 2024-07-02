# IMPORTS
import random
import time
import math

from bs4 import BeautifulSoup

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

scroll_origin = ScrollOrigin.from_viewport(500, 500) #define scroll origin

#
# STORE FINAL VARIABLES
#

mmyModel = []
mmyGeneration = []
mmyStartYear = []
mmyEndYear = []
mmyFuelType = []

options = Options()
options.add_experimental_option("detach", True) #ensure window stays open

driver = webdriver.Chrome(options=options)
driver.get("https://www.car.info/en-se/XPENG") #change car brand here

# currentSeries = int(driver.find_element(By.XPATH, '//*[@id="hierarchy_list_current"]/td/span/span').text)
# historicSeries = int(driver.find_element(By.XPATH, '//*[@id="hierarchy_list_historic"]/td/span/span').text)

print('loadBrandPage executed')
#Comment out these scrollPage functions if there isn't a plus button

try:
    driver.find_element(By.XPATH, f"//*[text()='Show all current series']").click()
except:
    print("no extension found")

try:
    driver.find_element(By.XPATH, f"//*[text()='Show all historic series']").click()
except:
    print("no extension found")

#
# COLLECT ALL SERIES FOR CAR
#

soup = BeautifulSoup(driver.page_source, "html.parser")
current_series = soup.find_all(
            "table",
            class_="table ci-table table-md table-striped mb-2",
        )

test = str(current_series[0]).split('href="')
links = set()
for i in test:
    if "https" in i:
        fullLink = i.split('"')
        partial = fullLink[0].split("en-se/")
        # print(partial)
        split = partial[1].split("/")
        # print(partial[0] + split[0] + "/" + split[1])
        fullLink = partial[0] + split[0] + "/" + split[1]
        #temp = temp[0].split("en-se/")
        links.add(fullLink)
            
print(f'Number of Series: {len(links)}')
links = list(links)
links.sort() #series

#
#   FOR EVERY LINK, STORE MODELS
#   STORE TEMP VARIABLES
#

# for i in range(10):
#     link = links[i]
for link in links:

    print(f'Fetching link: {link}')
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        driver.find_element(By.XPATH, f"//*[text()='Show all models']").click()
        # print("case 1")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        models = soup.find_all(
                "tr",
                class_="list_item show_condensed show_expanded_list",
            )
        models2 = soup.find_all(
                "tr",
                class_="list_item show_not_condensed show_expanded_list",
            )
        models.extend(models2)
    except:
        # print("case 2")
        models = soup.find_all(
                "tr",
                class_="list_item show_condensed",
            )
    
    try:
        seriesAppend = str(driver.find_element(By.XPATH, '//*[@id="content"]/main/div[2]/div[1]/div[1]/div[2]/div[2]').text)
    except:
        print('PAGE LOADING ERROR')
        continue

    modelLinks = {}
    for i in models:
        stringModel = str(i)
        if 'data-type="models"' in stringModel:
            m = stringModel.split('aria-label="')[1].split('<')[0].strip().split('"')[0]
            temp = stringModel.split('href="')
            temp = temp[1].split('">')
            if str(seriesAppend) not in m:
                m = seriesAppend + " " + m
            modelLinks[temp[0]] = m #add model link to hashmap
    if len(modelLinks) == 0:
        print("EMPTY MODELLINKS PROTOCOL")
        m = driver.find_element(By.XPATH, '//*[@id="content"]/main/div[2]/div[1]/div[1]/div[2]/div[2]').text
        modelLinks[link] = m #add model link to hashmap
    # print(modelLinks)
    print(f'Total of {len(modelLinks)} models detected')

    # print("iterating through models")
    for modelLink in modelLinks: #iterate through every model

        #
        #   LOOK THROUGH ALL MODELS VIA LINK AND APPEND GENERATIONS
        #

        driver.get(modelLink)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            driver.find_element(By.XPATH, f"//*[text()='Show all generations']").click()
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            generations = soup.find_all(
                    "tr",
                    class_="list_item show_condensed show_expanded_list",
                )
            generations2 = soup.find_all(
                    "tr",
                    class_="list_item show_not_condensed show_expanded_list",
                )
            generations.extend(generations2)
        except:
            generations = soup.find_all(
                    "tr",
                    class_="list_item show_condensed",
                    )
        print(f'{len(generations)} generations detected')
        genNumerated = 0
        generationLabels = {}

        for generation in generations:
            type = str(generation)
            if type.split('data-type="')[1].split('"')[0] == "generations": #identify list of generations
                gen = type.split('aria-label="')[1].split('<')[0].strip().split('"')[0]
                generationLabels[gen] = []
                # print(gen)

                tempFuelTypes = ""
                fuel = type.split('make_tooltip" data-tooltip="')
                for i in range(1, len(fuel)):
                    tempFuelTypes += fuel[i].split('"')[0].lower()
                if 'hybrid' in tempFuelTypes:
                    generationLabels[gen].append('Hybrid')
                elif 'electric' in tempFuelTypes and 'petrol' in tempFuelTypes:
                    generationLabels[gen].append('Electric & Gas')
                elif 'electric' in tempFuelTypes and 'petrol' not in tempFuelTypes:
                    generationLabels[gen].append('Electric')
                elif 'electric' not in tempFuelTypes and ('petrol' in tempFuelTypes or 'ethanol' in tempFuelTypes):
                    generationLabels[gen].append('Gas')
                else:
                    generationLabels[gen].append('Unknown')

                date = type.split('cell">')[1].split('<')[0].strip().split("-")
                try:
                    if int(date[0]) < 1980:
                        generationLabels[gen].append("pre-1980")
                    else:
                        generationLabels[gen].append(date[0])
                except:
                    generationLabels[gen].append("ERROR")
                
                try:
                    if date[1] == '':
                        generationLabels[gen].append("2024")
                    elif int(date[1]) < 1980:
                        generationLabels[gen].append("pre-1980")
                    else:
                        generationLabels[gen].append(date[1])
                except:
                    generationLabels[gen].append("ERROR")
        generationLabels = dict(sorted(generationLabels.items()))
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- pregen labels")
        print(generationLabels)

        for g in generationLabels:
            if "Concept" in g:
                generationLabels[g].append("Concept")
            elif "Facelift" not in g:
                genNumerated += 1
                genNumerated = math.floor(genNumerated)
                generationLabels[g].append(math.floor(genNumerated))
            else:
                genNumerated += 0.1
                generationLabels[g].append(f'{genNumerated:.1f}') # will face error if there are more than 10 facelifts for some reason

        #
        # add everything to list
        #
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- generation labels")
        print(generationLabels)
        for key in generationLabels:
            mmyModel.append(modelLinks[modelLink])
            mmyGeneration.append(generationLabels[key][3])
            mmyFuelType.append(generationLabels[key][0])
            mmyStartYear.append(generationLabels[key][1])
            mmyEndYear.append(generationLabels[key][2])


print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- final mmy")

for i in range(len(mmyModel)):
    print(f'{mmyModel[i]} Generation: {mmyGeneration[i]}; Fuel Type: {mmyFuelType[i]}; {mmyStartYear[i]} - {mmyEndYear[i]}')
print(f'{len(mmyModel)} entries')

data = {"Model": mmyModel, "Generation": mmyGeneration, "Start Year": mmyStartYear, "End Year": mmyEndYear, "Fuel Type": mmyFuelType}
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)
print("Data successfully saved to data.csv file")

read_file = pd.read_csv('data.csv')
read_file.to_excel('dataSpreadsheet.xlsx', index=None, header=True)

driver.close()