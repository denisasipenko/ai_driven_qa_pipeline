from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    """Page object for the Swag Labs login page."""

    # Locators
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    LOGIN_CONTAINER = (By.CSS_SELECTOR, "[data-test='login-container']")
    LOGIN_CREDENTIALS = (By.CSS_SELECTOR, "[data-test='login-credentials']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "[data-test='login-password']")
    ERROR_MESSAGE_CONTAINER = (By.CSS_SELECTOR, ".error-message-container")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.url = "https://www.saucedemo.com/"

    def open(self):
        """Opens the login page."""
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.USERNAME_FIELD))

    def enter_username(self, username: str):
        """Enters text into the username field."""
        self.driver.find_element(*self.USERNAME_FIELD).send_keys(username)

    def enter_password(self, password: str):
        """Enters text into the password field."""
        self.driver.find_element(*self.PASSWORD_FIELD).send_keys(password)

    def click_login_button(self):
        """Clicks the login button."""
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def get_login_credentials(self) -> str:
        """Returns the text of the login credentials."""
        return self.driver.find_element(*self.LOGIN_CREDENTIALS).text

    def get_login_password(self) -> str:
        """Returns the text of the login password."""
        return self.driver.find_element(*self.LOGIN_PASSWORD).text

    def is_error_message_present(self) -> bool:
        """Checks if the error message container is present."""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.ERROR_MESSAGE_CONTAINER)
        ).is_displayed()

    def is_on_products_page(self) -> bool:
        """Checks if the current page is the products page after login.
        Note: This method assumes successful login redirects to '/inventory.html'.
        """
        return "/inventory.html" in self.driver.current_url