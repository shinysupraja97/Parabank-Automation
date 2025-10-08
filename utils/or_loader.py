import json
from pathlib import Path
from selenium.webdriver.common.by import By

_BY = {
    "id": By.ID,
    "name": By.NAME,
    "xpath": By.XPATH,
    "css": By.CSS_SELECTOR,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "tag": By.TAG_NAME,
    "class": By.CLASS_NAME
}

def load_or(filepath: str) -> dict:
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Object repository missing: {filepath}")
    return json.loads(p.read_text(encoding="utf-8"))

def resolve_locator(or_map: dict, page_key: str, element_key: str):
    node = or_map.get(page_key, {}).get(element_key)
    if not node:
        raise KeyError(f"Locator not found: {page_key}.{element_key}")
    by = _BY[node["by"].lower()]
    return (by, node["value"])
