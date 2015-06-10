#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""temp version of comments: funcs in this module
query the various apis used in my project, and 
return the variables of interest for the project.

Idea is to combine data by zipcode, so each returned
dict/data frame should have a dict column. 

can then save data in mysql/sqlite3 database

note zipcode must be entered as a five letter string, 
not as number"""

#import modules to handle requests to APIs
import requests
from lxml import html
import numpy as np 

def query_zillow(zipcode):

	"""
		Inputs: 
			zipcode (string)
		Outputs:
			Zillow Home Value Index, Median Sale Price for given zipcode
	"""
	
	zillow_string = "http://www.zillow.com/webservice/GetDemographics.htm?zws-id="
	
	with open("../oauth_keys/zillow.keys") as f:
		zillow_key = f.read().strip("\n")
		zillow_url = zillow_string + zillow_key + "&zip=" + zipcode
		r = requests.get(zillow_url)
		#create tree from html content
		parser = etree.XMLParser()
		root = etree.fromstring(r.content)
		
	if len(parser.error_log) != 0:
		return -1
	
	#get Zillow Home Value Index from the XML tree	
	find = etree.XPath(".//response/pages/page/tables/table/data/attribute/name[text()='Zillow Home Value Index']")
	element = find(root)[0]  # [0] single element, in general, find(root) returns list.  
	try: 
		value_index = float(element.getparent().find("values/zip/value").text)
	except: 
		value_index = np.nan
	
	#get median sale price from the XML tree	
	find = etree.XPath(".//response/pages/page/tables/table/data/attribute/name[text()='Median Sale Price']")
	element = find(root)[0]  # [0] single element, in general, find(root) returns list.  
	try: 
		value_median = float(element.getparent().find("values/zip/value").text)
	except: 
		value_median = np.nan
	
	return value_index, value_median

def query_census(zipcode):
	#use tract-zipcode mapping here to filter for
	#data in requested zipcode.
	return census_data

def query_yelp(zipcode,business_type):
	#get number of restaurants, average rating, ...
	return yelp_data