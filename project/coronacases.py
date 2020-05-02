import requests 
from bs4 import BeautifulSoup 
import numpy as np 
import matplotlib.pyplot as plt 
extract_contents = lambda row: [x.text.replace('\n', '') for x in row] 
URL = 'https://www.mohfw.gov.in/'
  
SHORT_HEADERS = ['SNo', 'State','Indian-Confirmed', 
                 'Foreign-Confirmed','Cured','Death'] 
  
response = requests.get(URL).content 
soup = BeautifulSoup(response, 'html.parser') 
header = extract_contents(soup.tr.find_all('th'))   
stats = [] 
all_rows = soup.find_all('tr') 
  
for row in all_rows:
	stat = extract_contents(row.find_all('td'))
	if stat:
		if len(stat)==5:
			stats.append(['',*stat])
objects=[]
Total_cases=[]
Total_cured=[]
Total_deaths=[]
for r in stats:
	objects.append(r[2])
	Total_cases.append(r[3])
	Total_cured.append(r[4])
	Total_deaths.append(r[5])
