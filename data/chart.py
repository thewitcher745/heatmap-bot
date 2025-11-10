import shutil
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

import constants
from utils.logger import logger


class Chart:
    def __init__(self, pair_list: list | str, headless_mode: bool = False):
        options = webdriver.ChromeOptions()

        if headless_mode:
            options.add_argument("--headless")  # Run in headless mode

        # Set the download directory.
        download_dir = os.path.abspath("output_images")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = "eager"
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

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
        self.driver.execute_script("arguments[0].click();", element)

    def hide_cookie_consent_window(self) -> None:
        # This method removes the ask-for-consent window from the DOM, allowing for a clear vision of the chart.

        # The cookie consent window may or may not show. So a try-except block is required.
        try:
            self.driver.execute_script(
                f"document.querySelector('{constants.CONSENT_ROOT_ELEMENT_SELECTOR}').remove();"
            )
            self.driver.execute_script(
                f"document.querySelector('{constants.CONSENT_ROOT_ELEMENT_SELECTOR}').remove();"
            )
        except:
            pass

    def prevent_cookie_window(self):
        # Inject JavaScript to remove the element with the given CSS selector
        script = f"""
        var style = document.createElement('style');
        style.innerHTML = '{constants.CONSENT_ROOT_ELEMENT_SELECTOR}{{ display: none !important }}';
        document.head.appendChild(style);
        """

        self.driver.execute_script(script)

    def hide_loading_elements(self):
        # Inject JavaScript to hide the loading elements, aka the blur and the spinner.
        script1 = f"""
                var style1 = document.createElement('style');
                style1.innerHTML = '{constants.BLUR_ELEMENT_SELECTOR}{{ visibility: hidden !important }}';
                document.head.appendChild(style1);
                """

        script2 = f"""
                var style2 = document.createElement('style');
                style2.innerHTML = '{constants.LOADER_SPINNER_SELECTOR}{{ visibility: hidden !important }}';
                document.head.appendChild(style2);
                """

        self.driver.execute_script(script1)
        self.driver.execute_script(script2)

    def chart_has_finished_loading(self):
        # Finds the elements with z-index -1 and opacity 0, which would be the loading blur and the spinner if the chart has finished loading.
        # Also checks if the canvas element exists.
        try:
            # JavaScript function to check if the chart has loaded
            js_script = """
                    var chartCanvases = document.querySelectorAll("canvas");
                    var isLoadingComplete = Array.from(document.querySelectorAll('*')).filter(el => {
                        const style = window.getComputedStyle(el);
                        return style.zIndex === '-1' && style.opacity !== '0';
                    });
                    return (chartCanvases.length > 0) && (isLoadingComplete.length >= 2);
                    """

            # Execute the JavaScript and return the result
            is_loaded = self.driver.execute_script(js_script)
            return is_loaded

        except:
            return False

    def download_chart_with_button(self):
        # This function clicks the download button to download the chart.
        download_button_selector = constants.DOWNLOAD_CHART_BUTTON_SELECTOR
        if not download_button_selector:
            raise ValueError(
                "DOWNLOAD_CHART_BUTTON_SELECTOR is not set in environment variables"
            )

        download_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, download_button_selector))
        )
        download_button.click()

    def download_chart(self):
        try:
            # Loop indefinitely
            while True:
                # Find each pair in the pair_list property in the list and save its chart
                for pair in self.pair_list:
                    request_url = f"{constants.CHART_URL}?coin={pair}&type=symbol"
                    self.driver.get(request_url)
                    self.prevent_cookie_window()
                    self.hide_loading_elements()

                    WebDriverWait(self.driver, 30).until(
                        lambda driver: self.chart_has_finished_loading()
                    )
                    time.sleep(1)

                    # Find the chart element
                    chart_selector = constants.CHART_ELEMENT_SELECTOR
                    if not chart_selector:
                        raise ValueError(
                            "CHART_ELEMENT_SELECTOR is not set in environment variables"
                        )

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, chart_selector)
                        )
                    )

                    self.download_chart_with_button()

                time.sleep(3)

                # Clear the download directory
                self.clear_download_directory()

                break

        except Exception as e:
            logger.error(f"Error downloading chart: {e}")

        finally:
            # Close the driver
            self.driver.quit()
            pass

    def clear_download_directory(self):
        """Cleans up the download directory by:
        1. Removing non-PNG files
        2. Renaming PNG files to keep only the pair name in the format 'pair.png'
        """

        for filename in os.listdir(self.download_dir):
            file_path = os.path.join(self.download_dir, filename)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            # Remove non-PNG files
            if not filename.lower().endswith(".png"):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    pass
                continue

            # Process PNG files - extract the pair name and rename
            try:
                # Extract the pair name which is between the first and second underscore
                if "_" in filename and "heatmap" not in filename:
                    # Split by underscore and get the second part (index 1)
                    parts = filename.split("_")
                    if len(parts) > 1:
                        # The pair name is in the second part (index 1). When separated again using a space, it's the 0-th element.
                        pair = parts[1].split(" ")[0]
                        new_filename = f"heatmap_{pair}.png"
                        new_filepath = os.path.join(self.download_dir, new_filename)

                        # Remove if a file with the new name already exists
                        if os.path.exists(new_filepath):
                            os.unlink(new_filepath)

                        # Rename the file
                        os.rename(file_path, new_filepath)
                        logger.info(f"Renamed {filename} to {new_filename}")

            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
