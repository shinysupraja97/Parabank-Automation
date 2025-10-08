import os
from selenium import webdriver

# Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Edge (Chromium)
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


def _as_bool(val, default=True) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def build_driver(cfg: dict):    
    browser = os.getenv("BROWSER", cfg.get("browser", "chrome")).strip().lower()
    headless = _as_bool(os.getenv("HEADLESS", cfg.get("headless", "true")), default=True)
    implicit_wait = int(os.getenv("IMPLICIT_WAIT", cfg.get("implicit_wait", "5")))
    page_load_strategy = os.getenv(
        "PAGE_LOAD_STRATEGY", cfg.get("page_load_strategy", "normal")
    ).strip().lower()

    if browser == "chrome":
        options = ChromeOptions()
        options.page_load_strategy = page_load_strategy
        if headless:
            options.add_argument("--headless=new")
        else:
            options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # just in case — some environments ignore --start-maximized
        if not headless:
            try:
                driver.maximize_window()
            except Exception:
                pass

    elif browser == "edge":
        options = EdgeOptions()
        options.page_load_strategy = page_load_strategy
        if headless:
            options.add_argument("--headless=new")
        else:
            options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        if not headless:
            try:
                driver.maximize_window()
            except Exception:
                pass

    elif browser == "firefox":
        options = FirefoxOptions()
        options.page_load_strategy = page_load_strategy
        if headless:
            options.add_argument("-headless")

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        if not headless:
            try:
                driver.maximize_window()
            except Exception:
                pass

    else:
        raise ValueError(f"Unsupported browser '{browser}'. Use chrome|edge|firefox.")

    driver.implicitly_wait(implicit_wait)
    return driver
