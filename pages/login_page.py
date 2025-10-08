from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.or_loader import resolve_locator
from .base_page import BasePage

class LoginPage(BasePage):
    def loc(self, key):
        return resolve_locator(self.or_map, "login_page", key)

    def login(self, username, password, timeout=15):
        u_loc = self.loc("username")
        p_loc = self.loc("password")
        btn_loc = self.loc("btn_login")

        # Fields visible
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(u_loc))
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(p_loc))

        # Type cleanly
        u_el = self.driver.find_element(*u_loc)
        p_el = self.driver.find_element(*p_loc)
        u_el.clear(); u_el.send_keys(username)
        p_el.clear(); p_el.send_keys(password)

        # Click if possible, else press Enter
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(btn_loc)).click()
        except Exception:
            p_el.send_keys(Keys.ENTER)

        # Wait for outcome: success OR error
        overview = resolve_locator(self.or_map, "accounts_page", "overview_link")
        err = resolve_locator(self.or_map, "login_page", "error")
        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(overview),
                EC.presence_of_element_located(err)
            )
        )

    def has_error(self):
        err = resolve_locator(self.or_map, "login_page", "error")
        try:
            el = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(err))
            return True, (el.text or "").strip()
        except Exception:
            return False, ""
