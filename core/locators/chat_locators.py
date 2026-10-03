from selenium.webdriver.common.by import By


class ChatLocators:
    MAIN_SCREEN = (By.CSS_SELECTOR, "[data-testid='main-screen']")
    CURRENT_USER_NAME = (By.CSS_SELECTOR, "[data-testid='current-user-name']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "[data-testid='logout-button']")

    # Channels
    CHANNEL_LIST = (By.CSS_SELECTOR, "[data-testid='channel-list']")
    CHANNEL_GENERAL = (By.CSS_SELECTOR, "[data-testid='channel-general']")
    CHANNEL_QA_TESTING = (By.CSS_SELECTOR, "[data-testid='channel-qa-testing']")
    CHANNEL_MEDIA_TTS = (By.CSS_SELECTOR, "[data-testid='channel-media-tts']")
    ACTIVE_CHANNEL_NAME = (By.CSS_SELECTOR, "[data-testid='active-channel-name']")
    MESSAGE_COUNT_BADGE = (By.CSS_SELECTOR, "[data-testid='message-count-badge']")

    # Messaging
    MESSAGES_CONTAINER = (By.CSS_SELECTOR, "[data-testid='messages-container']")
    MESSAGES_LIST = (By.CSS_SELECTOR, "[data-testid='messages-list']")
    ALL_MESSAGES = (By.CSS_SELECTOR, ".message-item")
    MESSAGE_INPUT = (By.CSS_SELECTOR, "[data-testid='message-input']")
    SEND_BUTTON = (By.CSS_SELECTOR, "[data-testid='send-button']")

    # Audio & TTS
    TTS_OPEN_BUTTON = (By.CSS_SELECTOR, "[data-testid='tts-open-btn']")
    TTS_MODAL = (By.CSS_SELECTOR, "[data-testid='tts-modal']")
    TTS_TEXT_INPUT = (By.CSS_SELECTOR, "[data-testid='tts-text-input']")
    TTS_LANG_SELECT = (By.CSS_SELECTOR, "[data-testid='tts-lang-select']")
    TTS_GENERATE_BUTTON = (By.CSS_SELECTOR, "[data-testid='tts-generate-btn']")
    TTS_CLOSE_BUTTON = (By.CSS_SELECTOR, "[data-testid='tts-close-btn']")
    ALL_AUDIO_PLAYERS = (By.CSS_SELECTOR, ".audio-player-box audio")

    # Diagnostics & Telemetry
    STRESS_TOGGLE_BUTTON = (By.CSS_SELECTOR, "[data-testid='stress-toggle-btn']")
    STRESS_DRAWER = (By.CSS_SELECTOR, "[data-testid='stress-drawer']")
    STRESS_CPU_BUTTON = (By.CSS_SELECTOR, "[data-testid='stress-cpu-btn']")
    STRESS_MEM_BUTTON = (By.CSS_SELECTOR, "[data-testid='stress-mem-btn']")
    STRESS_RESET_BUTTON = (By.CSS_SELECTOR, "[data-testid='stress-reset-btn']")
    METRIC_CPU = (By.CSS_SELECTOR, "[data-testid='metric-cpu']")
    METRIC_RAM = (By.CSS_SELECTOR, "[data-testid='metric-ram']")
