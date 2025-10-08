from behave import step, use_step_matcher, given, when , then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from selenium.webdriver.common.by import By

from pages.home_page import HomePage
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.accounts_page import AccountsPage

from utils.data_factory import username_from_firstname
from utils.or_loader import resolve_locator
from utils.ui_actions import wait_for_any, wait_until_text_in_body

from utils.test_state import remember
from utils.test_state import recall

import allure
from allure_commons.types import AttachmentType

use_step_matcher("re")

# ---------- Common / navigation ----------

@step("I open the site")
def open_site(ctx):
    ctx.home = HomePage(ctx.driver, ctx.or_map, ctx.cfg)
    ctx.home.open()
    ctx.home.await_loaded(timeout=10)

@step("I log out if logged in")
def logout_if_logged_in(ctx):
    if not hasattr(ctx, "home"):
        ctx.home = HomePage(ctx.driver, ctx.or_map, ctx.cfg)
    ctx.home.logout_if_present()

@step("I navigate to the registration page")
def go_to_register(ctx):
    if not hasattr(ctx, "home"):
        ctx.home = HomePage(ctx.driver, ctx.or_map, ctx.cfg)
    ctx.home.go_to_register()
    ctx.register = RegisterPage(ctx.driver, ctx.or_map, ctx.cfg)
    # wait for firstName field to be visible
    fn_loc = resolve_locator(ctx.or_map, "register_page", "firstName")
    WebDriverWait(ctx.driver, 10).until(EC.visibility_of_element_located(fn_loc))

# ---------- Registration ----------

@step("I register a new user with:?")
def register_new_user(ctx):
    assert ctx.table and len(ctx.table.rows) == 1, "Provide exactly one data row."
    row = ctx.table.rows[0].as_dict()

    # Username policy: <firstName><digit>
    requested = (row.get("username") or "").strip()
    first = row.get("firstName", "user")
    if requested.upper() == "UNIQUE":
        username = username_from_firstname(first)
    else:
        username = requested or username_from_firstname(first)

    password = ctx.cfg.get("default_password", "Passw0rd!")
    ctx.remembered_username = username
    ctx.remembered_password = password
    remember(username, password)
    payload = {
        "firstName": first,
        "lastName":  row.get("lastName", ""),
        "address":   row.get("address", ""),
        "city":      row.get("city", ""),
        "state":     row.get("state", ""),
        "zip":       row.get("zip", ""),
        "phone":     row.get("phone", ""),
        "ssn":       row.get("ssn", ""),
        "username":  username,
        "password":  password,
        "confirm":   password,
    }
    ctx.register.register(payload)

    # Wait until either success text OR the login username field is present
    success_loc = resolve_locator(ctx.or_map, "register_page", "success_text")
    login_user_loc = resolve_locator(ctx.or_map, "login_page", "username")
    wait_for_any(ctx.driver, [success_loc, login_user_loc], timeout=12)

@step("I remember the password from config")
def remember_password_from_config(ctx):
    ctx.remembered_password = ctx.cfg.get("default_password", "Passw0rd!")

@step("registration should succeed")
def registration_should_succeed(ctx):
    success_loc = resolve_locator(ctx.or_map, "register_page", "success_text")
    login_user_loc = resolve_locator(ctx.or_map, "login_page", "username")
    # give the page a chance to flip
    idx, _ = wait_for_any(ctx.driver, [success_loc, login_user_loc], timeout=8)
    ok = (idx == 0) or (idx == 1)  # either is fine
    assert ok, "Expected success panel or login page after registration."

# ---------- Login & Balance ----------

@step("I log in with the remembered username and password")
def login_with_remembered(ctx):
    # Prefer context
    u = (getattr(ctx, "remembered_username", None) or "").strip()
    p = (getattr(ctx, "remembered_password", None) or "").strip()

    # Fallback to global stash if context empty
    if not u or not p:
        from utils.test_state import recall
        fu, fp = recall()
        u = (fu or "").strip()
        p = (fp or "").strip()
        # IMPORTANT: write back into context so downstream steps/prints are correct
        ctx.remembered_username, ctx.remembered_password = u, p

    assert u and p, "No remembered credentials; run the registration step first."

    ctx.login = LoginPage(ctx.driver, ctx.or_map, ctx.cfg)
    ctx.login.login(u, p)  # robust method below

    print(f"[DEBUG] logging in with -> user={u!r}")

    # Wait until Accounts Overview link is present (success signal)
    overview_loc = resolve_locator(ctx.or_map, "accounts_page", "overview_link")
    WebDriverWait(ctx.driver, 30).until(EC.presence_of_element_located(overview_loc))

# @step("I should see Accounts Overview and print the balance")
# def see_overview_and_print_balance(ctx):
#     ctx.accounts = AccountsPage(ctx.driver, ctx.or_map, ctx.cfg)

#     # Click and wait for overview to actually render
#     ctx.accounts.go_to_overview()
#     ctx.accounts.await_overview_loaded(timeout=15)

#     balance = ctx.accounts.first_balance()
#     print(f"[Parabank] Balance for {getattr(ctx, 'remembered_username', '<unknown>')}: {balance}")
#     assert balance != "N/A", "No balance found on Accounts Overview or Account Details."

@step("I should see Accounts Overview and print the balance")
def see_overview_and_print_balance(ctx):
    def _safe(page, key):
        try:
            return resolve_locator(ctx.or_map, page, key)
        except Exception:
            return None

    # 1) Give the landing view a moment to render
    time.sleep(3)

    # 2) Try to locate the Accounts Overview table
    table_loc = _safe("accounts_page", "overview_table")
    if table_loc is None:
        # Fallback: try heading; still keep going with body parsing if needed
        heading_loc = _safe("accounts_page", "overview_heading")
        if heading_loc:
            try:
                WebDriverWait(ctx.driver, 5).until(EC.presence_of_element_located(heading_loc))
            except Exception:
                pass

    account_number = "<unknown>"
    total_value  = "N/A"

    # 3) Read account number from the first account link in the overview table
    try:
        first_acct_loc = _safe("accounts_page", "first_account_link")
        if first_acct_loc:
            el = WebDriverWait(ctx.driver, 5).until(EC.presence_of_element_located(first_acct_loc))
            txt = (el.text or "").strip()
            if txt:
                account_number = txt
    except Exception:
        # soft fail; we'll still try to read Total
        pass

    # 4) Read the Total value shown on the Overview page
    try:
        table = None
        if table_loc:
            table = WebDriverWait(ctx.driver, 5).until(EC.presence_of_element_located(table_loc))

        if table:
            # Look for a bold "Total" label inside this table and take the following cell as the value
            total_lbl = table.find_element(By.XPATH, ".//b[normalize-space()='Total']")
            total_cell = total_lbl.find_element(By.XPATH, "./ancestor::td/following-sibling::td[1]")
            total_value = (total_cell.text or "").strip()
        else:
            # Fallback: search anywhere on the page for a "Total" label pattern
            total_lbl = ctx.driver.find_element(By.XPATH, "(.//b[normalize-space()='Total'])[1]")
            total_cell = total_lbl.find_element(By.XPATH, "./ancestor::td/following-sibling::td[1]")
            total_value = (total_cell.text or "").strip()
    except Exception:
        # Last-resort: regex scan for currency if page structure changed
        try:
            body = (ctx.driver.find_element(By.TAG_NAME, "body").text or "").strip()
        except Exception:
            body = ""
        if body:
            import re
            m = re.search(r"Total[^$]*\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})", body, flags=re.I)
            if m:
                # pull just the $ amount if present
                m2 = re.search(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})", m.group(0))
                if m2:
                    total_value = m2.group(0)

    # Console log (kept)
    print(f"[Parabank] Account: {account_number} | Total: {total_value}")

    # --- Allure logging & screenshot ---
    try:
        with allure.step("Account summary"):
            allure.attach(
                f"Username: {getattr(ctx, 'remembered_username', '<unknown>')}\n"
                f"Account Number: {account_number}\n"
                f"Total Value: {total_value}",
                name="Account Summary",
                attachment_type=AttachmentType.TEXT
            )
            # Screenshot for evidence
            png = ctx.driver.get_screenshot_as_png()
            allure.attach(png, name="Accounts Overview Screenshot", attachment_type=AttachmentType.PNG)
    except Exception:
        # Don't fail the test if Allure attachment has an issue
        pass

    assert total_value != "N/A", "Could not read the Total on Accounts Overview after login."


# ---- Config for error surfaces (kept in one place) ----
FIELD_ERROR_KEYS = [
    "first_name_error", "last_name_error", "address_error", "city_error",
    "zip_error", "password_error", "confirm_error",
    # add "state_error", "ssn_error", "username_error" if you wire them in locators.json
]
GENERAL_ERROR_KEYS = ["general_error", "error", "error_panel", "error_msg", "validation_block"]


# ---- small helpers ----
def _tok(val: str, *, for_username=False, first_name_seed="user") -> str:
    if val is None:
        return ""
    v = str(val)
    if v.upper() == "EMPTY":
        return ""
    if v.upper() == "UNIQUE" and for_username:
        return username_from_firstname(first_name_seed or "user")
    return v  # keep spaces as-is

def _wait_presence(context, page_key: str, key: str, timeout=6):
    loc = resolve_locator(context.or_map, page_key, key)
    return WebDriverWait(context.driver, timeout).until(EC.presence_of_element_located(loc))

def _wait_any_text(context, page_key: str, keys: list[str], timeout=6) -> str:
    out = []
    for k in keys:
        try:
            el = _wait_presence(context, page_key, k, timeout=timeout)
            t = (el.text or "").strip()
            if t:
                out.append(t)
        except Exception:
            continue
    if out:
        return " ".join(out)
    try:
        return (context.driver.find_element("tag name", "body").text or "").strip()
    except Exception:
        return ""

def _resubmit_if_mismatch(context, password: str, confirm: str):
    if confirm and confirm != password:
        try:
            c = resolve_locator(context.or_map, "register_page", "confirm")
            b = resolve_locator(context.or_map, "register_page", "btn_register")
            el = WebDriverWait(context.driver, 5).until(EC.presence_of_element_located(c))
            el.clear(); el.send_keys(confirm)
            context.driver.find_element(*b).click()
        except Exception:
            pass


# ---------- WHEN: I attempt registration with (table) ----------
@when(u'I attempt registration with')
def attempt_registration_table(context):
    assert context.table and context.table.rows, "Provide a single data row."
    row = context.table.rows[0].as_dict()

    first = _tok(row.get("firstName", ""), first_name_seed=row.get("firstName", "user"))
    payload = {
        "firstName": first,
        "lastName":  _tok(row.get("lastName", "")),
        "address":   _tok(row.get("address", "")),
        "city":      _tok(row.get("city", "")),
        "state":     _tok(row.get("state", "")),
        "zip":       _tok(row.get("zip", "")),
        "phone":     _tok(row.get("phone", "")),
        "ssn":       _tok(row.get("ssn", "")),
        "username":  _tok(row.get("username", ""), for_username=True, first_name_seed=first),
        "password":  _tok(row.get("password", "")),
        "confirm":   _tok(row.get("confirm", "")),
    }

    if not hasattr(context, "register"):
        context.register = RegisterPage(context.driver, context.or_map, context.cfg)

    context.register.register(payload)
    _resubmit_if_mismatch(context, payload["password"], payload["confirm"])

    # Allow either error surfaces or success/login to appear for next assertions
    try:
        wait_targets = [
            resolve_locator(context.or_map, "register_page", "general_error"),
            resolve_locator(context.or_map, "register_page", "success_text"),
            resolve_locator(context.or_map, "login_page", "username"),
        ]
        for loc in wait_targets:
            try:
                WebDriverWait(context.driver, 6).until(EC.presence_of_element_located(loc))
                break
            except Exception:
                continue
    except Exception:
        pass


# ---------- THEN: generic validator (covers all message variants) ----------
@then(r'I should see a registration validation containing "(?P<phrase>.+)"')
def assert_registration_validation_contains(context, phrase):
    text = _wait_any_text(context, "register_page", FIELD_ERROR_KEYS, timeout=6) \
        or _wait_any_text(context, "register_page", GENERAL_ERROR_KEYS, timeout=6)
    got = (text or "").lower()
    exp = (phrase or "").lower()
    assert exp in got, f'Expected validation containing "{phrase}", but saw: {text[:400]}'


# ---------- THEN: all-required special (count field errors, exclude phone) ----------
@then(u'I should see required errors for all fields except phone')
def assert_required_all_except_phone(context):
    expected = [
        "first_name_error", "last_name_error", "address_error",
        "city_error", "zip_error", "password_error", "confirm_error",
        # add more here if you add locators (state_error, ssn_error, username_error)
    ]

    seen = []
    for k in expected:
        try:
            _ = _wait_presence(context, "register_page", k, timeout=8)
            seen.append(k)
        except Exception:
            pass

    missing = [k for k in expected if k not in seen]
    assert not missing, f"Missing required-field errors for: {missing}. Seen: {seen}"

    # Ensure phone_error is absent
    phone_present = False
    try:
        _ = _wait_presence(context, "register_page", "phone_error", timeout=3)
        phone_present = True
    except Exception:
        pass
    assert not phone_present, "Did not expect a phone error when all fields are empty."


# --- WHEN (regex matcher expects capturing groups and quotes) ---
@when(r'I attempt login with "(?P<username>.*)" and "(?P<password>.*)"')
def step_attempt_login(context, username, password):
    u = "" if username.strip().upper() == "EMPTY" else username.strip()
    p = "" if password.strip().upper() == "EMPTY" else password.strip()
    context.login = LoginPage(context.driver, context.or_map, context.cfg)
    context.login.login(u, p)

# --- THEN (regex; captures full expected string) ---
@then(r'I should see a login error containing "(?P<expect>.+)"')
def step_login_error_contains(context, expect):
    ok, msg = context.login.has_error()  # uses your locators.json -> login_page.error
    assert ok, "Expected a login error message, but none was found."
    # Normalize whitespace & prefix like "Error!" (keeps this flexible)
    norm = " ".join((msg or "").split())
    assert expect in norm, f"Expected '{expect}' in error message, but saw '{msg}'"
