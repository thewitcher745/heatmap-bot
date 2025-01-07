import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from PIL import Image

import constants
from utils.logger import logger

class Chart:
    def __init__(self, pair_list: list | str, headless_mode: bool = True):
        options = webdriver.ChromeOptions()

        if headless_mode:
            options.add_argument('--headless')  # Run in headless mode

        # Set the download directory.
        download_dir = os.path.join(os.path.abspath(os.getcwd()), 'output_images')
        prefs = {'download.default_directory': download_dir}
        options.add_experimental_option('prefs', prefs)

        # Initiate the driver.
        driver = webdriver.Chrome(options=options)

        # Set the window size to a large value, in a square aspect ratio
        driver.set_window_size(constants.WEBPAGE_WIDTH, constants.WEBPAGE_WIDTH)

        self.download_dir = download_dir
        self.driver = driver

        # If a single pair is given instead of a list of pairs, convert it to a list to standardize it.
        if isinstance(pair_list, list):
            self.pair_list = pair_list
        else:
            self.pair_list = [pair_list]

        self.download_dir = download_dir

    def click_element(self, css_selector):
        # Simply click on an element given its CSS selector. Replace : and - characters with \: and \-

        # Wait until the chart element appears.
        element: WebElement = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )

        # This method simply clicks on an element, given its CSS selector.
        self.driver.execute_script(f"arguments[0].click();", element)

    def remove_cookie_consent_window(self) -> None:
        # This method removes the ask-for-consent window from the DOM, allowing for a clear vision of the chart.

        # The cookie consent window may or may not show. So a try-except block is required.
        try:
            self.driver.execute_script(f"document.querySelector('{constants.CONSENT_ROOT_ELEMENT_SELECTOR}').remove();")
        except:
            pass

    def click_symbol_button(self):
        # This method clicks on the Symbol button

        # Wait until the buttons are present
        buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'button'))
        )

        # Iterate through the buttons and find the one with innerHTML "Symbol"
        for button in buttons:
            if button.get_attribute('innerHTML') == 'Symbol':
                # Click the button or perform any other action
                button.click()
                break

    def select_pair_from_list(self, pair_name):
        # Fetches the list of pairs from the GUI, then clicks on the one which has its innerHTML matched with the pair name.

        # Get the list of available pairs
        dropdown_list: WebElement = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, constants.DROPDOWN_LIST_ELEMENT_SELECTOR))
        )

        menu_items = dropdown_list.find_elements(By.CSS_SELECTOR, 'li')

        # If the list of symbols hasn't loaded in, return "LIST_INCOMPLETE"
        if len(menu_items) < 5:
            return "LIST_INCOMPLETE"

        # Iterate through the menu items and click the one that matches the pair_name
        for item in menu_items:
            if item.get_attribute("innerHTML") == pair_name:
                item.click()

                return "DONE"

        # If the pair's name, for whatever reason, isn't found, return "PAIR_NOT_FOUND"
        return "PAIR_NOT_FOUND"


    def get_chart_into_view(self, element) -> tuple[dict, dict]:
        # This function scrolls the chart into view if for whatever reason it isn't in the view already. This function should never really execute.
        # It returns the location and size of the element on the webpage, which get used in screenshotting it.
        # Get the element's location and size
        location = element.location
        size = element.size

        distance_from_bottom = self.driver.execute_script("return window.innerHeight - arguments[0].getBoundingClientRect().bottom", element)
        if distance_from_bottom < 0:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)

            # Update the element's location and size after scrolling
            location = element.location
            size = element.size

        return location, size

    def crop_and_save_charts(self, pair: str, location, size):
        # This function takes the location and size of the element, screenshots  the webpage, and then crops the full screenshot to only leave the
        # chart intact. It saves both files to /output_images/.

        # Take a full-page screenshot
        screenshot_path = os.path.join(self.download_dir, 'full_screenshot.png')
        self.driver.save_screenshot(screenshot_path)

        # Open the screenshot and crop the desired area
        image = Image.open(screenshot_path)
        left = location['x'] - constants.CHART_X_OFFSET
        top = location['y'] - constants.CHART_Y_OFFSET
        right = location['x'] + size['width'] + constants.CHART_X_OFFSET
        bottom = location['y'] + size['height'] + constants.CHART_Y_OFFSET
        cropped_image = image.crop((left, top, right, bottom))

        # Save the cropped image
        output_path = os.path.join(self.download_dir, f'heatmap_{pair}.png')

        cropped_image.save(output_path)

    def download_chart(self):
        try:
            while True:
                self.driver.get(constants.CHART_URL)

                self.remove_cookie_consent_window()

                self.click_symbol_button()
                time.sleep(1)  # Just to be safe

                # Find each pair in the pair_list property in the list and save its chart
                for pair in self.pair_list:
                    self.click_element(constants.SYMBOL_DROPDOWN_BUTTON_SELECTOR)

                    pair_selection = self.select_pair_from_list(pair)

                    # If anything goes wrong with selecting the pair from the list, handle the error by either skipping the pair or refreshing.
                    if pair_selection == "PAIR_NOT_FOUND":
                        logger.error(f'Chart for pair {pair} not found. Consider removing.')
                        continue

                    elif pair_selection == "LIST_INCOMPLETE":
                        break

                    # Wait until the chart element appears.
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, constants.CHART_ELEMENT_SELECTOR))
                    )

                    # Wait for element to load
                    time.sleep(5)

                    location, size = self.get_chart_into_view(element)

                    self.crop_and_save_charts(pair, location, size)

                else:
                    break

        finally:
            self.driver.quit()
