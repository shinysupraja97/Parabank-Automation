from pages.home_page import HomePage
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from utils.data_factory import default_user

def ensure_user_exists(driver, or_map, cfg, username, password):
    home = HomePage(driver, or_map, cfg)
    home.open()
    home.logout_if_present()
    home.go_to_register()

    reg = RegisterPage(driver, or_map, cfg)
    payload = default_user(username=username, password=password)
    reg.register(payload)

    # If taken -> fine; else success also fine
    if reg.has_username_taken_error() or reg.success_panel_visible():
        return
