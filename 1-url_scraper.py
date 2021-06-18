

import time
import requests
import random
import json
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager    
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#browser = webdriver.Firefox()#Chrome('./chromedriver.exe')
PATIENCE_TIME = 60
BRANDS = ['other-sneakers/other-sneakers-other']

params = 'fit=fill&bg=FFFFFF&w=1024&h=1024&auto=format,compress&trim=color&q=90&dpr=1'

#return type list per brand
def get_types(brand):
    #account for unique identifiers
    # if brand == 'jordan':
    #     brand = 'retro-jordans'
    # elif brand == 'other':
    #     brand = 'other-sneakers'
    # brand = "other-sneakers/balenciaga-sneakers"
    type_list = []
    # driver = webdriver.Chrome('./chromedriver')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://stockx.com/{}".format(brand))
    while True:
        try:
            #if load more button present, click!
            loadMoreButton = driver.find_element_by_xpath("//div[@class='subcategory show-more']")
            print( loadMoreButton )
            time.sleep(2)
            loadMoreButton.click()
            time.sleep(5)
        #else -> continue
        except Exception as e:
            print(e)
            break
    #capture type divs
    elems = driver.find_elements_by_xpath("//div[@class='subcategoryList']/div[@class='form-group']/div[@class='checkbox subcategory']")
    for elem in elems:
        item = elem.find_element_by_tag_name('label').get_attribute('innerHTML')
        #account for unique identifiers
        if len(item.split(' ')) > 0:
            item = '-'.join(item.split(' '))
        if item == 'Other':
            item = 'footwear'
        if item.isdigit():
            item = 'air-jordan-'+item
        type_list.append(item.lower())
    driver.quit()
    print( type_list)
    return type_list

def page_information():
    brand_dict = {}
    missing = []
    sneaker_counter = 0
    #iterate through brand & types ex. AirForce, Lebron, etc. 
    for b in BRANDS:
        type_dict = {}
        page_dict = {}
        #account for unique identifier
        print( "Starting "+b.capitalize())
        #open URL with webdriver
        for i in range(12):
            driver = webdriver.Chrome('./chromedriver')
            url    = "https://stockx.com/{}?page={}".format(b, i)
            result = True
            time.sleep(5)
            driver.get(url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1/(random.randint(1,100)*10000))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                no_result = driver.find_element_by_xpath(".//div[@class='no-results']")
                check     = no_result.get_attribute("innerHTML").split(' ')[0]
                if check == "NOTHING":
                    print( 'No results found. Going to next page.')
                    driver.quit()
                    continue
            except NoSuchElementException as e:
                result = True
                print( e)
            if result:
                #while True, Search for presence of loading button
                print( "Beginning Extraction")
                #capture divs loaded from fully loaded page
                elems = driver.find_elements_by_xpath("//div[@class='browse-grid']/div[@class='tile browse-tile updated']/div[@class='tile css-1bonzt1 e1yt6rrx0']")
                #search divs for name,href,src
                for elem in elems:
                    sneaker_counter+=1
                    #contains parent div
                    href      = elem.find_element_by_tag_name('a').get_attribute("href")
                    #search for //div/img
                    imgUrl = elem.find_element_by_xpath(".//div[@class=' css-1c5ij41 e1sjmub50']").find_element_by_xpath(".//*").get_attribute("src")
                    # img_tag   = elem.find_element_by_xpath(".//div[@class='css-1c5ij41 euld1y70']").find_element_by_xpath(".//div[@class='css-10klw3m e1372ynp0']").get_attribute("innerHTML")
                    print(imgUrl)
                    if imgUrl is not None:
                        clip = imgUrl.split('?')
                        imgUrl = clip[0]+'?'+params
                        download_image(imgUrl)

                    data = {
                        "href": href,
                        "src" : imgUrl
                    }
                    page_dict[sneaker_counter] = data
                    time.sleep(1/(random.randint(1,100)*10000))
                #if scraper encounters an error, the count will be zero
                #identify what page is missing
                driver.quit()
                print( 'Total Count: '+str(sneaker_counter))
                #seed page_dict[name] into type_dict
                type_dict[b] = page_dict
                print( "SEEDING TYPE...")
            #seed type_dict into total
        brand_dict[b] = type_dict
        print( "SEEDING BRANDS...")
    #return final dictionary
    with open('total.json', 'w') as outfile:  

        json.dump(brand_dict, outfile, indent=4)
    with open('missing.json', 'w') as outfile:  
        json.dump(missing, outfile, indent=4)
    print( "Complete.")
    print( missing )

def download_image(image):
    response = requests.get(image, stream=True)
    filename = response.headers['X-Imgix-ID']
    f_ext = os.path.splitext(image)[-1].split('?')[0]
    f_name = ('./images/{}{}').format(filename, f_ext)
    print(f_name)
    with open(f_name, 'wb') as f:
      f.write(response.content)
    del response

if __name__ == "__main__":
    page_information()