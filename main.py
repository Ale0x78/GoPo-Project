#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
URL = "https://www.opensecrets.org/outsidespending/nonprof_cands.php"
open_secret_urls = ["https://www.opensecrets.org/outsidespending/nonprof_cands.php?cycle=2014","https://www.opensecrets.org/outsidespending/nonprof_cands.php","https://www.opensecrets.org/outsidespending/nonprof_cands.php?cycle=2012"]
CoC_url = "https://www.uschamber.com/how-they-voted/2016"
# Url is https://www.opensecrets.org/outsidespending/nonprof_cands.php
DEBUG = True

def clean_up(line):
	l = str(line).strip()
	l = l.replace(' ','_')
	l = l.replace(',','')
	l = l.replace('(D)','')
	l = l.replace('(R)','')
	l = l.replace('(I)','')
	return l

def numericify(data):
	d = str(clean_up(data))
	d = d.replace('_','')
	d = d.replace('$','')
	# print(d)
	return d

def unpack(stri):
	s = stri.replace('_',' ')
	s = s.strip()
	return s

def lookup(name,rows):
	first = name.split(" ")[1]
	last = name.split(" ")[0]
	if first == "Steven":
		first = "Steve" #The only special case that doesn't work with the web scraper. 

	index = -1
	if DEBUG:
		print ("Looking up the CoC Index for " + first + " " + last + ".")
	for row in rows:
		if "Senate" not in str(row.contents[1].text):
			continue
		match = str(row.contents[1].text).split('Senate')[0].strip()
		
		if (first in match and last in match):
			index_str = str(row.contents[5].text).strip()
			index_str = index_str[:len(index_str)-1]
			index = int(index_str)

	return index
		



def openSecrets(url):

	CoC_r = requests.get(CoC_url)
	CoC_text_html = CoC_r.text
	#print(text_html)
	CoC_soup = BeautifulSoup(CoC_text_html,'html.parser')
	CoC_rows = CoC_soup.find_all('tr', class_="views-row")

	r = requests.get(url)
	text_html = r.text
	#print(text_html)
	soup = BeautifulSoup(text_html,'html.parser')
	rows = soup.find_all('tr')
	counter = 0
	names = []
	contributions = []

	votes = []
	for row in rows:
		if counter == 0:
			counter += 1
			continue
		region = str(row.contents[2].text).strip()
		name = clean_up(str(row.contents[0].text))
		cont = numericify(row.contents[4].text)
		if region[2] == 'S' and row.contents[14].text == "Winner":
			vote = lookup(unpack(name),CoC_rows)
			if not (vote == -1): #THE API IS NOT PERFECT DUE TO TIME LIMITATIONS 
				if DEBUG:	
					print("[+] " + unpack(name) + " has recived $" + cont + " dark money contributions and has a CoC index of " + str(vote));
				contributions.append(cont)
				votes.append(vote)
				names.append(name)
			else:
				print("[-] " + unpack(name) + " Was not FOUND!")
		
		counter += 1
	print("Checking to make sure the amount of data collected is equal....")
	print(len(names) == len(contributions))
	print(len(votes) == len(names))
	return (names,contributions,votes)

def write(names,contributions,votes):
	with open('data.csv', 'w') as myfile:
	    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	    wr.writerow(["Name","Cont","Votes"])
	    i = 0;
	    for name in names:
	    	wr.writerow([unpack(name),contributions[i],votes[i]])
	    	i += 1

def main():
	total_names = []
	total_cont = []
	total_votes = []
	for url in open_secret_urls:
		names, cont,votes = openSecrets(url)
		total_names += names
		total_cont += cont
		total_votes += votes
		sleep(1)
	write(total_names,total_cont,total_votes)
	print(len(total_names))

main()