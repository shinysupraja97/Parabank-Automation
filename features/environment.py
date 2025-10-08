from pathlib import Path
from utils.config_loader import load_properties
from utils.or_loader import load_or
from drivers.webdriver_factory import build_driver
from utils.test_state import clear

def before_all(context):
    clear()
    context.cfg = load_properties(str(Path("config") / "config.properties"))
    context.or_map = load_or(str(Path("object_repository") / "locators.json"))

def before_scenario(context, scenario):
    context.driver = build_driver(context.cfg)

def after_scenario(context, scenario):
    clear()
    try:
        Path("artifacts/screenshots").mkdir(parents=True, exist_ok=True)
        shot = Path("artifacts/screenshots") / f"{scenario.name.replace(' ','_')}.png"
        context.driver.save_screenshot(str(shot))
        print(f"[PROOF] Screenshot -> {shot}")
    finally:
        context.driver.quit()
