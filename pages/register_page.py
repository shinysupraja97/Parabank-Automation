from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.or_loader import resolve_locator
from .base_page import BasePage

class RegisterPage(BasePage):
    def loc(self, key): 
        return resolve_locator(self.or_map, "register_page", key)

    def register(self, data: dict, timeout=15):
        # Wait form visible
        fn_loc = self.loc("firstName")
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(fn_loc))

        # Fill fields
        fields = ["firstName","lastName","address","city","state","zip","phone","ssn","username","password","confirm"]
        for k in fields:
            val = data.get(k, "")
            if val != "__BLANK__":
                el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.loc(k)))
                el.clear()
                el.send_keys(val)

        # Click the Register submit INSIDE the registration form
        btn_loc = self.loc("btn_register")
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(btn_loc)).click()

        # Wait for either success or an error to show up
        success = self.loc("success_text")
        error = self.loc("general_error")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.any_of(
                    EC.presence_of_element_located(success),
                    EC.presence_of_element_located(error)
                )
            )
        except Exception:
            # Last chance: page might have navigated directly to logged-in landing
            pass

    def has_username_taken_error(self):
        try:
            txt = (WebDriverWait(self.driver, 1)
                   .until(EC.presence_of_element_located(self.loc("general_error"))).text or "").lower()
            return "username" in txt and ("exist" in txt or "already" in txt or "taken" in txt)
        except Exception:
            return False

    def has_validation_error(self):
        try:
            _ = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located(self.loc("general_error")))
            return True
        except Exception:
            return False

    def success_panel_visible(self):
        try:
            _ = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(self.loc("success_text")))
            return True
        except Exception:
            return False
