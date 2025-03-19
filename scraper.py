# Name = //span[contains(@itemprop,'name')]
# price = //span[contains(@itemprop,'price')]
#discounted = //span[contains(@class,'itemtile-price-strikethrough')]
# link = //div[contains(@class,'dne-itemtile-detail')]//a.gethref

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless")  # Uncomment if you want headless mode
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Rotate User-Agent to prevent detection
ua = UserAgent()
options.add_argument(f"user-agent={ua.random}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Define the target website (CoinMarketCap Bitcoin page)
URL = "https://www.ebay.com/globaldeals/tech"

def scroll_to_load_all_products():
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
            
        last_height = new_height
def scrape_ebay_data():
    driver.get(URL)
    time.sleep(5) 
    scroll_to_load_all_products()
    all_data =[]
    try:
        product_items = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".dne-itemtile"))
        )
    except :
        print(f"Error locating product items:")
        product_items = []
    for item in product_items:

        try:
            name = item.find_element(By.XPATH,'.//span[contains(@itemprop,"name")]').text

            price = item.find_element(By.XPATH, ".//span[contains(@itemprop,'price')]").text

            try:
                discounted = item.find_element(By.XPATH,".//span[contains(@class,'itemtile-price-strikethrough')]").text
            except:
                discounted = price

            url = item.find_element(By.XPATH, ".//div[contains(@class,'dne-itemtile-detail')]//a").get_attribute("href")

            try:
                shipping =item.find_element(By.XPATH, ".//span[contains(@class,'dne-itemtile-delivery')]").text
            except:
                shipping="N/A"

    #    //span[contains(@class,'dne-itemtile-delivery')]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        
            ebay_data = {
                "timestamp": timestamp,
                "price": price,
                "original_price": discounted,
                "title": name,
                "shipping": shipping,
                "item_url": url,
            }
            all_data.append(ebay_data)
        except Exception as e :
            print("Error occurred:",e)
            return None
    return all_data


def save_to_csv(data_list):
    file_name = "ebay_tech_deals.csv"
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp", "title", "price", "original_price", "shipping", "item_url"])
    new_rows = pd.DataFrame(data_list)
    df = pd.concat([df, new_rows], ignore_index=True)
    df.to_csv(file_name, index=False)



if __name__ == "__main__":
    print("Scraping ebay Data...")
    scraped_data = scrape_ebay_data()

    if scraped_data:
        save_to_csv(scraped_data)
        print("Data saved to ebaydata.csv")

    driver.quit()



