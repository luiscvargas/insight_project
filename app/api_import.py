#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""temp version of comments: funcs in this module
query the various apis used in my project, and 
return the variables of interest for the project.

Idea is to combine data by zipcode, so each returned
dict/data frame should have a dict column. 

can then save data in mysql/sqlite3 database """

def query_zillow(zipcode):
	#get housing information in zipcode
	return zillow_data

def query_census(zipcode):
	#use tract-zipcode mapping here to filter for
	#data in requested zipcode.
	return census_data

def query_yelp(zipcode,business_type):
	#get number of restaurants, average rating, ...
	return yelp_data