from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebElement

def href_has_mailto(mark):
	'''
	An Expectation for checking an element's href has a 'mailto:' text.

	element is either a locator (text) or a WebElement
	'''

	def _predicate(driver: webdriver.Chrome):
		# find element if locator is given
		el = mark if isinstance(mark, WebElement) else driver.find_element(*mark)

		return el if 'mailto' in el.get_attribute('href') else False

	return _predicate
