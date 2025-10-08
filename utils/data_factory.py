from datetime import datetime
import random, string
import re


_used_suffixes = set()

def username_from_firstname(first_name: str) -> str:
    base = re.sub(r"\W+", "", (first_name or "user")).lower()

    # Try up to 50 attempts to find an unused two-letter suffix
    for _ in range(50):
        suffix = "".join(random.choice(string.ascii_lowercase) for _ in range(2))
        if suffix not in _used_suffixes:
            _used_suffixes.add(suffix)
            return f"{base}{suffix}"

    # Fallback (extremely unlikely)
    return f"{base}{''.join(random.choice(string.ascii_lowercase) for _ in range(2))}"

def default_user(username=None, password="Passw0rd!"):
    if not username:
        username = username_from_firstname()
    return {
        "firstName": "Incu",
        "lastName": "Byte",
        "address": "123 Test St",
        "city": "Testville",
        "state": "TS",
        "zip": "12345",
        "phone": "1234567890",
        "ssn": "999-99-9999",
        "username": username,
        "password": password,
        "confirm": password,
    }
