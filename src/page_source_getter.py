# src/page_source_getter.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PageSourceGetter:
    """A utility to get the page source HTML of a given URL."""

    @staticmethod
    def get_source(url: str) -> str:
        """
        Opens a URL in a headless browser and returns its page source.

        Args:
            url: The URL to fetch.

        Returns:
            The page source HTML as a string.
        """
        print(f"Fetching page source for: {url}")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        page_source = ""
        try:
            driver.get(url)
            # Wait for the body tag to be present, a good sign the page has started loading
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = driver.page_source
            print("-> Successfully fetched page source.")
        except Exception as e:
            print(f"Error fetching page source for {url}: {e}")
            raise
        finally:
            driver.quit()
            
        return page_source
