from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

SERVICE = Service(executable_path=ChromeDriverManager().install())
OPTIONS = Options()
OPTIONS.add_argument('--headless')
OPTIONS.add_experimental_option("excludeSwitches", ["enable-logging"])
