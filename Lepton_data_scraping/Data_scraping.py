'''
There are some small changes made to the script from jupyter notebook to ensure smooth running of python script.
A try and except case of keyboard interrupt has been added so the script can be stopped at any desired time and the code
will still be executed.
'''

import time
import pandas as pd
import haversine as hs
from csv import reader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("NOTE: To exit before scraping data of all the stores and continue with the code, Press (CTRL + C) ")
print("AFTER ITERATING THROUGH ATLEAST 1 PIN CODE")
print("Please wait for few seconds after pressing CTRL + C\n")
print("Scraping all the data may take few hours. Total 16000+ rows of data")
time.sleep(4)

website = "https://www.asianpaints.com/store-locator.html"
path = Service('C:/Users/khale/Downloads/chromedriver_win32')
driver = webdriver.Chrome(service=path)
driver.get(website)

name = []
address = []
timings = []
coordinates = []
phone = []
df = pd.DataFrame(
    {'name': name, 'address': address, 'timings': timings, 'coordinates': coordinates, 'phone number': phone})

with open('district_pincodes.csv', 'r') as read_obj:
    pincodes = reader(read_obj)
    i = 0
    j = 0
    # This try and except is not present in jupyter notebook. It is to stop the loop at any desired time.
    try:
        #This loop iterates over all the pin codes from the district_pincodes.csv
        for pincode in pincodes:

            print("For pincode: {} --- S.No: {}".format(pincode, j))
            j += 1

            text_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "search-input")))
            text_box.clear()
            text_box.send_keys(pincode)
            text_box.submit()
            time.sleep(5)
            # time.sleep() is added to let the page reload after entering the pin codes.

            # divlist contains list of stores elements. Each element contains data of a single store
            divlist = driver.find_elements(By.XPATH, "//div[@class='primary-layout_listview_lists newVarientForMap']")

            for div in divlist:
                # This loop is used to iterate over all the elements in the div

                # Extracting data from each element in store list element.
                try:
                    str_name = div.find_element(By.XPATH, ".//h4[@class='d-md-block storeBlock']").text
                except NoSuchElementException:
                    name.append(None)
                    str_name = None
                else:
                    name.append(str_name)

                print("{}--  {}".format(i, str_name))
                i += 1

                try:
                    latlong_element = div.find_element(By.XPATH,
                                                       ".//span[@class='spriteIcon-AprevampPhase3 directionIco']")
                except NoSuchElementException:
                    coordinates.append(None)
                else:
                    latlong = latlong_element.get_attribute('data-directionurl')
                    latlong = latlong[(latlong.rindex("/") + 1):]
                    coordinates.append(latlong)

                try:
                    add = div.find_element(By.XPATH, ".//p[@class='description']").text
                except NoSuchElementException:
                    address.append(None)
                else:
                    address.append(add)

                try:
                    ph = div.find_element(By.XPATH, ".//span[@class='open-close d-none d-md-inline-block ml-4']")
                except NoSuchElementException:
                    phone.append(None)
                else:
                    phone.append(ph.text[4:])

                try:
                    store_time = div.find_element(By.XPATH, ".//span[@class='open-close js-open-close']")
                except NoSuchElementException:
                    timings.append(None)
                else:
                    timings.append(store_time.text)
            # Storing data of all stores of each pin code
            df1 = pd.DataFrame(
                {'name': name, 'address': address, 'timings': timings, 'coordinates': coordinates,
                 'phone number': phone})
            #df = df.append(df1, ignore_index=True)
            df = pd.concat([df,df1], ignore_index = True)
            name[:] = []
            address[:] = []
            timings[:] = []
            coordinates[:] = []
            phone[:] = []


    except  KeyboardInterrupt:
        pass

driver.quit()
# Removing duplicates from the table
df = df.drop_duplicates()
# File name has been changed so that the original file remains unchanged.
df.to_csv('asianpaints_data_scraping_copy.csv', index=False)

# Filter the nearest stores to the user.
# Initializing new Data frame for data analysis.
df3 = pd.DataFrame()
df3 = df

# Storing user coordinates to calculate distance between the user and stores.
print("Sample input- Latitude:28.644800, Longitude:77.216721")
lat = float(input("Enter latitude"))
long = float(input("Enter longitude"))

loc1 = (lat, long)

# Calculating distance
def dist(loc):
    loc2 = tuple(map(float, loc.split(',')))
    return hs.haversine(loc1, loc2)


dist_list = map(dist, df['coordinates'])
df3['distance'] = list(dist_list)

# Printing 10 nearest stores
df3 = df3.round({'distance': 4})
# File name has been changed so that the original file remains unchanged.
df3.sort_values(by=['distance']).head(10).to_csv('nearest_stores1.csv', index= False)
print(df3.sort_values(by=['distance']).head(10))
