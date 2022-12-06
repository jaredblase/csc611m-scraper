from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

OPTIONS = Options()
OPTIONS.add_argument('--headless')
OPTIONS.add_experimental_option("excludeSwitches", ["enable-logging"])

def create_driver():
	return webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=OPTIONS)
