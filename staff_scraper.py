from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import threading
from queue import Queue, Empty
from wait import href_has_mailto
from professor import Professor

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
OPTIONS = Options()
OPTIONS.add_argument('--headless')
OPTIONS.add_experimental_option("excludeSwitches", ["enable-logging"])
OPTIONS.add_argument('--disable-dev-shm-usage')
OPTIONS.add_argument('--no-sandbox')

class StaffScraper(threading.Thread):
	STOP_EVENT = threading.Event()

	def __init__(self, driver: webdriver.Chrome, id_buffer: Queue, personnel_list: Queue):
		threading.Thread.__init__(self)
		self.driver = driver
		self.id_buffer = id_buffer
		self.personnel_list = personnel_list

	def run(self):
		while not StaffScraper.STOP_EVENT.is_set():
			id = None
			try:
				id = self.id_buffer.get(timeout=5)
			except Empty:
				self.id_buffer.put(id)

			self.driver.get(f'https://www.dlsu.edu.ph/staff-directory/?personnel={id}')

			try:
				email = WebDriverWait(self.driver, 10).until(
					href_has_mailto((By.CSS_SELECTOR, 'ul.list-unstyled.text-capitalize.text-center ul a'))
				)
			except (NoSuchElementException, TimeoutException):
				continue

			# extract data
			list_items = self.driver.find_elements(By.CSS_SELECTOR, 'ul.list-unstyled.text-capitalize.text-center li span')

			name = self.driver.find_element(By.TAG_NAME, 'h3').get_attribute('innerText')
			email = email.get_attribute('href').split(':')[-1]
			position = list_items[0].get_attribute('innerText')
			department = list_items[1].get_attribute('innerText')

			print(Professor(name, email, department, position))
			# add to queue
			self.personnel_list.put(Professor(name, email, department, position))