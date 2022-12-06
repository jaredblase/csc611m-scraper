from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import threading
from queue import Queue, Empty
from typing import List
import csv

import config
from staff_scraper import StaffScraper
from id_scraper import IDScraper

# constants
N_PRODUCER = 1
N_CONSUMER = 5
N_TIME = 30 # seconds

URL = 'https://www.dlsu.edu.ph/staff-directory'
PERSONNEL_LIST = Queue()
PERSONNEL_COUNT = 0
ID_BUFFER = Queue()
STOPPED = False

HEADER = ['name', 'email', 'department', 'position']

producer_threads: List[threading.Thread] = []
consumer_threads: List[threading.Thread] = []

def stop_execution():
	global STOPPED
	STOPPED = True
	StaffScraper.STOP_EVENT.set()
	IDScraper.STOP_EVENT.set()
	print('stopping...')

timer = None
try:
	DRIVER = webdriver.Chrome(service=config.SERVICE, options=config.OPTIONS)
	DRIVER.get(URL)
	
	# initialize readers
	for _ in range(N_PRODUCER):
		producer_threads.append(IDScraper(DRIVER, ID_BUFFER))
		producer_threads[-1].start()

	# initialize requesters
	for _ in range(N_CONSUMER):
		consumer_threads.append(StaffScraper(DRIVER, ID_BUFFER, PERSONNEL_LIST))
		consumer_threads[-1].start()

	# set timer
	timer = threading.Timer(N_TIME, stop_execution)
	timer.start()

	while not STOPPED:
		# press the "Load More" button once it is visible and clickable
		DRIVER.execute_script(
			'arguments[0].click();',
			WebDriverWait(DRIVER, 30).until(
				EC.element_to_be_clickable((By.CSS_SELECTOR, '#dlsu-personnel-button button'))
			)
		)
		IDScraper.ID_EVENT.set() # notify ID scraper that new items are loaded

finally:
	timer.join()

	for thread in producer_threads:
		thread.join()

	for thread in consumer_threads:
		thread.join()
	
	# write personnel
	with open('personnel.csv', 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(HEADER)
		while True:
			try:
				prof = PERSONNEL_LIST.get(timeout=1)
				print(prof)
				PERSONNEL_COUNT += 1
				writer.writerow([prof.name, prof.email, prof.department, prof.position])
			except Empty:
				break

	# write statistics
	with open('statistics.txt', 'w') as f:
		f.write(f'''URL: {URL}
								Statistics
								Number of pages scraped: {IDScraper.COUNTER}
								Number of emails found: {PERSONNEL_COUNT}
						 ''')

	DRIVER.quit()