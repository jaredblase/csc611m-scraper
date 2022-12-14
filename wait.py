from selenium import webdriver
from threading import Lock
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.common.exceptions import NoSuchElementException

def href_has_mailto(mark):
	'''
	An Expectation for checking an element's href has a 'mailto:' text.

	mark is either a locator (text) or a WebElement
	'''

	def _predicate(driver: webdriver.Chrome):
		# find element if locator is given
		try:
			el = mark if isinstance(mark, WebElement) else driver.find_element(*mark)
			href = el.get_attribute('href')

			if 'mailto' in href:
				return el
			if 'cdn-cgi' in href: # still loading
				return False
			else:
				return True
		except NoSuchElementException:
			return True

	return _predicate


def thread_safe_element_to_be_clickable(mark, lock: Lock):
	'''
	A thread-safe expectation for checking  if an element is clickable

	mark is either a locator (text) or a WebElement
	event is a threading.Lock object
	'''
	pred = element_to_be_clickable(mark)

	def _predicate(driver: webdriver.Chrome):
		lock.acquire()
		result = pred(driver)
		if lock.locked():
			lock.release()
		return result

	return _predicate
