import os
import random
import requests
import cv2
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class VoursaBot:

    def __init__(self):
        options = Options()
        options.add_argument('--disable-notifications')
        self.driver = webdriver.Chrome(options=options)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    

    def download_img(self):
        time.sleep(5)
        images = []
        max_images = 600

        # Navigate to Voursa website for car listings
        self.driver.get("https://www.voursa.com/index.cfm?gct=1&sct=11&gv=13")
        print("Navigated to Voursa website")
        time.sleep(5)
        while True:
            # Scroll down to the bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolling")
            time.sleep(5)

            # Check if "Suivant" button is present and visible
            try:
                suivant_button = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//a[text()='Suivant']"))
                )
                if suivant_button.is_displayed():
                    suivant_button.click()
                    print("Clicked 'Suivant' button")
                    break
            except Exception as e:
                print("No 'Suivant' button found yet:", e)

        


        # Get all listing elements and handle stale elements
        listings = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/annonces.cfm")]')
        listing_urls = [listing.get_attribute('href') for listing in listings]
        print("Found {} listing URLs".format(len(listing_urls)))
        if len(listing_urls) > 200:

            listing_urls = listing_urls[:200]
        
        print("Limited to first 20 listing URLs")

        for listing_url in listing_urls:
            print("Processing listing URL: {}".format(listing_url))
            try:
                self.driver.get(listing_url)
                print("Navigated to listing page")
                time.sleep(5)

                # Wait for image elements to load
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))

                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                print("Found {} image elements".format(len(img_elements)))
                for img in img_elements:
                    src = img.get_attribute('src')
                    if src and "produit_bgph" in src:
                        images.append(src)
                        print(f"Image found: {src}")
                    else:
                        print(f"Not a valid image URL: {src}")

            except StaleElementReferenceException as e:
                print(f"StaleElementReferenceException encountered for URL: {listing_url}. Skipping...")
            except TimeoutException as e:
                print(f"TimeoutException encountered for URL: {listing_url}. Skipping...")

        print('Scraped {} images!'.format(len(images)))

        path = os.getcwd()
        rando = random.randint(0, 1000)
        path = os.path.join(path, "VOURSA_CARS_" + str(rando))

        if not os.path.exists(path):
            os.mkdir(path)

        counter = 0
        for image in images:
            if counter >= max_images:
                break
            if image.startswith("http"):
                try:
                    save_as = os.path.join(path,"web1_" + str(counter) + '.jpg')
                    response = requests.get(image, headers=self.headers)
                    if response.status_code == 200:
                        with open(save_as, 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded {image} as {save_as}")
                        counter += 1
                    else:
                        print(f"Failed to download {image}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"Failed to download {image}: {e}")
            else:
                print(f"Skipping invalid URL: {image}")

# Use the bot
bot = VoursaBot()
bot.download_img()

