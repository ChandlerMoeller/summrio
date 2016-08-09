# -*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError
from bs4 import BeautifulSoup

#
#functions
#
def print_error(error, text):
	"""print errors in consistent format then exits

	Args:
		error: The error that occured
		text: More descript and/or a possible solution
	"""
	error = str(error)
	print (error + ": " + text)
	exit()

def print_debug_title(txt):
	print "\n##############################"
	print "\t" + txt
	print "##############################"

def print_sorted_table_by_value(table):
	"""Print a sorted table
	"""
	d_view = [ (v,k) for k,v in table.iteritems() ]
	d_view.sort(reverse=True) # natively sort tuples by first element
	for v,k in d_view:
		print "%d: %s" % (v,k)

def get_soup(url):
	"""get the soup from a url

	Args:
		url: a valid url string

	Returns:
		soup
	"""
	response = urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, "html.parser")
	response.close()
	return soup

def get_soup_alternate(url):
	"""get the soup from a url using an alternate method for websites that do not work for webscraping
	
	Args:
		url: a valid url string

	Returns:
		soup
	"""
	headers = {"User-Agent":"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
	req = Request(url, headers=headers)
	response = urlopen(req)
	html = response.read()
	soup = BeautifulSoup(html, "html.parser")
	response.close()
	return soup
