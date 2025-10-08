from utils import ui_actions as UI

class BasePage:
    def __init__(self, driver, or_map=None, cfg=None):
        self.driver = driver
        self.or_map = or_map or {}
        self.cfg = cfg or {}

    def goto(self, url): UI.navigate(self.driver, url)
    def click(self, loc): UI.click(self.driver, loc)
    def type(self, loc, text): UI.type_text(self.driver, loc, text)
    def text(self, loc): return UI.get_text(self.driver, loc)
    def exists(self, loc, timeout=3): return UI.exists(self.driver, loc, timeout)
    def snap(self, name): return UI.screenshot(self.driver, name)
