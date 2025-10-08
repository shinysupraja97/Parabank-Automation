import time
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def click(driver, locator, timeout=10):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator)).click()

def type_text(driver, locator, text, timeout=10, clear=True):
    el = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
    if clear:
        el.clear()
    el.send_keys(text)

def get_text(driver, locator, timeout=10):
    el = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
    return (el.text or "").strip()

def exists(driver, locator, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        return True
    except:
        return False

def navigate(driver, url: str):
    driver.get(url)

def screenshot(driver, name: str, folder="artifacts/screenshots"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    path = Path(folder) / f"{int(time.time())}_{name}.png"
    driver.save_screenshot(str(path))
    return path

def wait_for_any(driver, locators, timeout=10):
    end = WebDriverWait(driver, timeout)
    while True:
        for i, loc in enumerate(locators):
            try:
                el = end.until(EC.presence_of_element_located(loc))
                return i, el
            except:
                pass
        # if none present yet, loop continues until timeout triggers from last wait

def wait_until_text_in_body(driver, text_substring: str, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: text_substring.lower() in d.find_element("tag name", "body").text.lower()
    )