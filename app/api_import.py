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

def query_zillow(zipcode):
	#get housing information in zipcode
	zillow_string = "http://www.zillow.com/webservice/GetDemographics.htm?zws-id="
	with open("../oauth_keys/zillow.keys") as f:
		zillow_key = f.read().strip("\n")
	zillow_url = zillow_string + zillow_key + "&zip=" + zipcode
	r = requests.get(zillow_url)
	if r.status_code != 200:
		return -1
	return r
	#print r.text
	#return zillow_data

def query_census(zipcode):
	#use tract-zipcode mapping here to filter for
	#data in requested zipcode.
	return census_data

def query_yelp(zipcode,business_type):
	#get number of restaurants, average rating, ...
	return yelp_data