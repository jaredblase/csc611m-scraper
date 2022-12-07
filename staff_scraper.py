from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import threading
import atexit
from queue import Queue, Empty
from wait import href_has_mailto
from personnel import Personnel
from utils import create_driver

class StaffScraper(threading.Thread):
	STOP_EVENT = threading.Event()
	__COUNTER_LOCK = threading.Lock()
	COUNTER = 0

	def __init__(self, id_buffer: Queue, personnel_list: Queue, driver=None):
		threading.Thread.__init__(self)
		self.driver = create_driver() if driver is None else driver
		self.id_buffer = id_buffer
		self.personnel_list = personnel_list
		atexit.register(self.__close)

	def run(self):
		while not StaffScraper.STOP_EVENT.is_set():
			id = None
			try:
				id = self.id_buffer.get(timeout=5)
			except Empty:
				continue

			self.driver.get(f'https://www.dlsu.edu.ph/staff-directory/?personnel={id}')
			
			StaffScraper.__COUNTER_LOCK.acquire()
			StaffScraper.COUNTER += 1
			StaffScraper.__COUNTER_LOCK.release()

			try:
				email = WebDriverWait(self.driver, 10).until(
					href_has_mailto((By.CSS_SELECTOR, '.btn.btn-sm.btn-block.text-capitalize'))
				)

				if email == True: # email element not present
					continue
			except TimeoutException:
				# print(f'Pass! {id}')
				self.id_buffer.put(id)
				continue

			# extract data
			list_items = self.driver.find_elements(By.CSS_SELECTOR, 'ul.list-unstyled.text-capitalize.text-center li span')

			name = self.driver.find_element(By.TAG_NAME, 'h3').get_attribute('innerText')
			email = email.get_attribute('href').split(':')[-1]
			position = list_items[0].get_attribute('innerText')
			department = list_items[1].get_attribute('innerText')

			# print(Professor(name, email, department, position))
			# add to queue
			self.personnel_list.put(Personnel(name, email, department, position))

	def __close(self):
		self.driver.quit()
