from utils.or_loader import resolve_locator
from .base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage(BasePage):
    def open(self):
        self.goto(self.cfg["base_url"])

    def await_loaded(self, timeout=10):
        # Wait for either Register link or Login username field to appear
        register_loc = resolve_locator(self.or_map, "home_page", "register_link")
        login_user_loc = resolve_locator(self.or_map, "login_page", "username")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.any_of(
                    EC.presence_of_element_located(register_loc),
                    EC.presence_of_element_located(login_user_loc),
                )
            )
        except Exception:
            # Best-effort; page might still be usable
            pass

    def go_to_register(self):
        self.click(resolve_locator(self.or_map, "home_page", "register_link"))

    def logout_if_present(self):
        loc = resolve_locator(self.or_map, "home_page", "logout_link")
        if self.exists(loc, timeout=2):
            self.click(loc)
