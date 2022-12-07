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

	def __init__(self, driver: webdriver.Chrome, driver_lock: threading.Lock, id_buffer: Queue):
		threading.Thread.__init__(self)
		self.driver = driver
		self.driver_lock = driver_lock
		self.id_buffer = id_buffer

	def get_children_count(self):
		while not self.driver_lock.acquire(timeout=5) and not IDScraper.STOP_EVENT.is_set():
			pass

		if IDScraper.STOP_EVENT.is_set():
			return 0
		
		count = int(
			self.driver.find_element(By.ID, 'dlsu-personnel-list').get_attribute('childElementCount')
		)
		self.driver_lock.release()
		return count

	def run(self):
		while not IDScraper.STOP_EVENT.is_set():
			while not IDScraper.__COUNTER_LOCK.acquire(timeout=5) and not IDScraper.STOP_EVENT.is_set():
				pass

			# if there are lacking children, wait until main thread loads more items
			if self.get_children_count() < IDScraper.__COUNTER and not IDScraper.STOP_EVENT.is_set():
				IDScraper.ID_EVENT.clear()
			
			while not IDScraper.ID_EVENT.is_set() and not IDScraper.STOP_EVENT.is_set():
				pass

			element = None
			try:
				while not self.driver_lock.acquire(timeout=5) and not IDScraper.STOP_EVENT.is_set():
					pass
				element = self.driver.find_element(By.CSS_SELECTOR, f'#dlsu-personnel-list :nth-child({IDScraper.__COUNTER}) button[name=personnel]')
				# print(element.get_attribute('value'))
				self.id_buffer.put(element.get_attribute('value'))
			except NoSuchElementException:
				pass
			finally:
				self.driver_lock.release()
				IDScraper.__COUNTER += 1
				IDScraper.__COUNTER_LOCK.release()
