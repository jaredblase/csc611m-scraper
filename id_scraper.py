from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import threading
from queue import Queue

class IDScraper(threading.Thread):
	__COUNTER_LOCK = threading.Lock()
	__COUNTER = 2
	ID_EVENT = threading.Event()
	STOP_EVENT = threading.Event()

	def __init__(self, driver: webdriver.Chrome, id_buffer: Queue):
		threading.Thread.__init__(self)
		self.driver = driver
		self.id_buffer = id_buffer

	def get_children_count(self):
		return int(
			self.driver.find_element(By.ID, 'dlsu-personnel-list').get_attribute('childElementCount')
		)

	def run(self):
		while not IDScraper.STOP_EVENT.is_set():
			IDScraper.__COUNTER_LOCK.acquire()

			# if there are lacking children, wait until main thread loads more items
			if self.get_children_count() < IDScraper.__COUNTER and not IDScraper.STOP_EVENT.is_set():
				IDScraper.ID_EVENT.clear()
			
			while not IDScraper.ID_EVENT.is_set() and not IDScraper.STOP_EVENT.is_set():
				pass

			element = None
			try:
				element = self.driver.find_element(By.CSS_SELECTOR, f'#dlsu-personnel-list :nth-child({IDScraper.__COUNTER}) button[name=personnel]')
			except NoSuchElementException:
				pass
			finally:
				IDScraper.__COUNTER += 1
				IDScraper.__COUNTER_LOCK.release()

			if element:
				self.id_buffer.put(element.get_attribute('value'))