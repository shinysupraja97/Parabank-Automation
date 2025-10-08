import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.or_loader import resolve_locator
from .base_page import BasePage

CURRENCY_REGEX = re.compile(r"(?:[$₹]|Rs\.?)?\s?\d[\d,]*\.\d{2}")

class AccountsPage(BasePage):
    def _loc(self, group, key):
        return resolve_locator(self.or_map, group, key)

    def await_overview_loaded(self, timeout=15):
        try:
            heading = self._loc("accounts_page", "overview_heading")
            table   = self._loc("accounts_page", "overview_table")
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(heading))
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(table))
        except Exception:
            # Best effort: some themes don't have <h1>, so at least wait for any table
            pass

    def go_to_overview(self):
        self.click(self._loc("accounts_page", "overview_link"))

    def _text_of(self, by_locator, timeout=5):
        el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(by_locator))
        return (el.text or "").strip()

    def _try_overview_table_balance(self) -> str:
        try:
            cell_loc = self._loc("accounts_page", "any_balance_cell")
            text = self._text_of(cell_loc, timeout=3)
            m = CURRENCY_REGEX.search(text)
            if m:
                return m.group(0)
        except Exception:
            pass

        # fallback: scan the table text by regex
        try:
            table_loc = self._loc("accounts_page", "overview_table")
            table_text = self._text_of(table_loc, timeout=3)
            m = CURRENCY_REGEX.search(table_text)
            if m:
                return m.group(0)
        except Exception:
            pass
        return "N/A"

    def _open_first_account_and_read_balance(self) -> str:
        try:
            first_link = self._loc("accounts_page", "first_account_link")
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(first_link)).click()
        except Exception:
            return "N/A"

        # Now on Account Details page, read the balance cell
        try:
            avail_loc = self._loc("account_details", "available_balance_cell")
            text = self._text_of(avail_loc, timeout=5)
            m = CURRENCY_REGEX.search(text)
            if m:
                return m.group(0)
            # fallback: scan entire body
            body_text = self.driver.find_element("tag name", "body").text
            m = CURRENCY_REGEX.search(body_text)
            return m.group(0) if m else "N/A"
        except Exception:
            return "N/A"

    def first_balance(self) -> str:
        # 1) make sure Overview is there
        self.await_overview_loaded(timeout=15)

        # 2) overview table
        bal = self._try_overview_table_balance()
        if bal != "N/A":
            return bal

        # 3) open first account and read
        bal = self._open_first_account_and_read_balance()
        if bal != "N/A":
            return bal

        # 4) last resort: body regex
        body_text = self.driver.find_element("tag name", "body").text
        m = CURRENCY_REGEX.search(body_text)
        return m.group(0) if m else "N/A"
