import os
import random
import wget
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
from username_password import username, password



class FacebookMarketplaceBot:

    def __init__(self):
        options = Options()
        options.add_argument('--disable-notifications')
        self.driver = webdriver.Chrome(options=options)

    def login(self, username, password):
        
        self.driver.get("https://www.facebook.com/login")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "email")))

        #fill in the username and password and click the login button
        email_in = self.driver.find_element(By.ID, "email")
        print("email_in = self.driver.find_element(By.ID, email)")
        email_in.send_keys(username)
        print("email_in.send_keys(username)")

        password_in = self.driver.find_element(By.ID, "pass")
        password_in.send_keys(password)

        login_btn = self.driver.find_element(By.ID, "loginbutton")
        login_btn.click()

        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@role="navigation"]')))
            print("Logged in successfully")
            return True
        except TimeoutException:
            print("Login failed. Check your credentials or the login page structure.")
            return False

 

    def download_img(self):
        time.sleep(5)
        images = []
        #maxmimum number of images i want
        max_images = 600

        # Navigate to Facebook Marketplace for Mauritania and search for cars
        self.driver.get("https://www.facebook.com/marketplace/105706327804136/")
        print("self.drive navigation")
        time.sleep(5)

        search_box = self.driver.find_element(By.XPATH, '//input[@aria-label="Search Marketplace"]')
        search_box.send_keys("cars")
        search_box.send_keys(Keys.RETURN)
        #print("dubuging: searching for cars")
        time.sleep(5)

        # Scroll down to load more listings
        for _ in range(5):  # Adjust the range for more scrolling
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("scrolling")
            time.sleep(5)

        # Get all listing elements and handle stale elements
        listings = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/marketplace/item/")]')
        listing_urls = [listing.get_attribute('href') for listing in listings]
        print("Found {} listing URLs".format(len(listing_urls)))
        #limite the listings for time sake
        listing_urls = listing_urls[:20]

        for listing_url in listing_urls:
            print("Processing listing URL: {}".format(listing_url))
            try:
                self.driver.get(listing_url)
                print("Navigated to listing page")
                time.sleep(5)

                # Wait for image elements to load
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'img')))
                
                #find images element in the listing url and print the number of image element
                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                print("Found {} image elements".format(len(img_elements)))
                for img in img_elements:
                    #get the source 
                    src = img.get_attribute('src')
                    #scontent is part of the facebook listing url to exclude profile img
                    if src and "scontent" in src:
                        images.append(src)
                        print(f"Image found: {src}")
                    else:
                        print("Not a valid image URL: {}".format(src))

            except StaleElementReferenceException as e:
                print(f"StaleElementReferenceException encountered for URL: {listing_url}. Skipping...")
            except TimeoutException as e:
                print(f"TimeoutException encountered for URL: {listing_url}. Skipping...")

        print('I scraped {} images!'.format(len(images)))
        
        #saving the images
        path = os.getcwd()
        #optional : random number for not renaming the folder every time run the code
        rando = random.randint(0, 1000)
        path = os.path.join(path, "FB_MAURITANIA_CARS_" + str(rando))

        if not os.path.exists(path):
            os.mkdir(path)

        #set a counter for not downloading more images than what we need 
        counter = 0
        for image in images:
            if counter >= max_images:
                break
            if image.startswith("http"):
                try:
                    save_as = os.path.join(path, str(counter) + '.jpg')
                    wget.download(image, save_as)
                    counter += 1
                    
                except Exception as e:

                    print(f"Failed to download {image}: {e}")

# Use the bot
bot = FacebookMarketplaceBot()
bot.login(username, password)
if bot.login:

    bot.download_img()
else:
    print("login first")
