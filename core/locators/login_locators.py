from selenium.webdriver.common.by import By


class LoginLocators:
    AUTH_SCREEN = (By.CSS_SELECTOR, "[data-testid='auth-screen']")
    LOGIN_CARD = (By.ID, "login-card")
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-testid='username-input']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-testid='password-input']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-testid='login-button']")
    LOGIN_ERROR = (By.CSS_SELECTOR, "[data-testid='login-error']")
