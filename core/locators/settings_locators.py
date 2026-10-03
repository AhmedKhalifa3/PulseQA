from selenium.webdriver.common.by import By


class SettingsLocators:
    TELEMETRY_WIDGET = (By.CSS_SELECTOR, "[data-testid='telemetry-widget']")
    CHANNEL_SEARCH_INPUT = (By.CSS_SELECTOR, "[data-testid='channel-search-input']")
    STRESS_DRAWER = (By.CSS_SELECTOR, "[data-testid='stress-drawer']")
