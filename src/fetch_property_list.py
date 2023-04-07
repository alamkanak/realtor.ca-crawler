from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from dotenv import load_dotenv

load_dotenv()

# ================== FUNCTIONS ==================

def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument(r"user-data-dir=" + os.environ.get('CHROME_USER_DATA_DIR'))
    chrome_options.set_capability("browserVersion", "98")
    if os.environ.get('ENV') == 'docker':
        driver = webdriver.Remote(
            "http://chrome:4444/wd/hub", 
            DesiredCapabilities.CHROME,
            options=chrome_options
        )
    else:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

# ================== MAIN ==================

# Init driver
driver = init_driver()

# Define the starting page
start_url = "https://www.realtor.ca/map#ZoomLevel=12&Center=43.802332%2C-79.411224&LatitudeMax=43.89209&LongitudeMax=-79.24969&LatitudeMin=43.71244&LongitudeMin=-79.57276&CurrentPage=2&Sort=6-D&PropertyTypeGroupID=1&PropertySearchTypeId=0&TransactionTypeId=3&RentMin=2000&RentMax=3000&BedRange=2-0&BuildingTypeId=17&Currency=CAD"
driver.get(start_url)

# Create an empty list to hold the results
results = []

def tryCatch(function):
    try:
        return function()
    except:
        return None

# Start the loop
while True:

    # Wait for the search list to load
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mapSidebarBodyCon")))

    # Parse the search list
    property_list_container = driver.find_element(By.CSS_SELECTOR, "#mapSidebarBodyCon")
    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".select2-container--disabled")))
    properties = property_list_container.find_elements(By.CSS_SELECTOR, ".cardCon")

    # Add the results to the list
    for child_element in properties:
        result = {}

        bedrooms = tryCatch(lambda: [el for el in child_element.find_elements(By.CSS_SELECTOR, ".smallListingCardIconCon") if "Bedrooms" in el.get_attribute("innerHTML")][0].find_element(By.CSS_SELECTOR, ".smallListingCardIconTopCon").text.strip())
        bathrooms = tryCatch(lambda: [el for el in child_element.find_elements(By.CSS_SELECTOR, ".smallListingCardIconCon") if "Bathrooms" in el.get_attribute("innerHTML")][0].find_element(By.CSS_SELECTOR, ".smallListingCardIconTopCon").text.strip())
        price = tryCatch(lambda: float(child_element.find_element(By.CSS_SELECTOR, ".smallListingCardPrice").text.replace("$", "").replace(",", "").replace("/Monthly", "").strip()))
        address = tryCatch(lambda: child_element.find_element(By.CSS_SELECTOR, ".smallListingCardAddress").text.strip())
        add_time = tryCatch(lambda: lambda: child_element.find_element(By.CSS_SELECTOR, ".smallListingCardTagLabel").text.strip())
        url = tryCatch(lambda: child_element.find_element(By.CSS_SELECTOR, ".listingDetailsLink").get_attribute("href"))
    
        results.append({
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "price": price,
            "address": address,
            "url": url,
            "add_time": add_time
        })

    # Check if there is a link to the next page
    next_link = driver.find_elements(By.CSS_SELECTOR, ".lnkNextResultsPage")
    if len(next_link) == 0:
        break 
    if next_link[0].get_attribute("disabled") == "disabled":
        break
    
    # Click on the next page link
    next_link[0].click()

# Print the final results
df = pd.DataFrame(results)
df.to_csv("properties.csv", index=False)
print(df)

# Close the web driver
driver.quit()