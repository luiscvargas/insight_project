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
from lxml import etree
import lxml
import numpy as np 
import pandas as pd

def query_zillow(ziplist):

	"""
	Inputs: 
		- ziplist (list of string zipcodes)
	Outputs:
		- dict of zipcode: Zillow Home Value Index, Median Sale Price]
	"""
	
	output_dict = {}

	zillow_string = "http://www.zillow.com/webservice/GetDemographics.htm?zws-id="
	
	for zipcode in ziplist:

		if zipcode == "0":
			output_dict["0"] = [np.nan,np.nan]

		else:

			print "zipcode = ",zipcode

			with open("../oauth_keys/zillow.keys") as f:
				zillow_key = f.read().strip("\n")
				zillow_url = zillow_string + zillow_key + "&zip=" + zipcode
				r = requests.get(zillow_url)
				#create tree from html content
				parser = etree.XMLParser()
				root = etree.fromstring(r.content)
		
			if len(parser.error_log) != 0:
				output_dict[zipcode] = [np.nan, np.nan]

			else:
	
				#get Zillow Home Value Index from the XML tree	
				find = etree.XPath(".//response/pages/page/tables/table/data/attribute/name[text()='Zillow Home Value Index']")
				if find(root) == []:
					value_index = np.nan
				else:
					element = find(root)[0]  # [0] single element, in general, find(root) returns list.  
					try: 
						value_index = float(element.getparent().find("values/zip/value").text)
					except: 
						value_index = np.nan
	
				#get median sale price from the XML tree	
				find = etree.XPath(".//response/pages/page/tables/table/data/attribute/name[text()='Median Sale Price']")
				if find(root) == []:
					value_index = np.nan
				else:
					element = find(root)[0]  # [0] single element, in general, find(root) returns list.  
					try: 
						value_median = float(element.getparent().find("values/zip/value").text)
					except: 
						value_median = np.nan
	
				output_dict[zipcode] = [value_index, value_median]

	return output_dict

def format_census_request(list_keys,county,state="36"):

	"""
	Inputs: 
		- list_keys (list of strings) - Variables to be imported via API call
		- county (str) - One of counties in NY State, must be single value 
			so list of tracts is unique
		- state (str) - Currently only enabled for NY  
	Outputs:
		- url (str) - address for API call to US Census 5 Year ACS Profile Data
	"""

	if state != "36":
		raise ValueError("state must be '36'")

	tract = "*"  #get all tracts within county and state

	with open("../oauth_keys/census.keys") as f:
		census_key = f.read().strip("\n")

	url_root = "http://api.census.gov/data/2013/acs5/profile?get="
	url_vars = ",".join(list_keys)
	url_reg  = "&for=tract:" + tract + "&in=state:" + state + "+county:" + county + "&key=" + census_key
	url = url_root + url_vars + url_reg

	print url
	
	return url

def query_census(census_vars_keys, county_code):
	#use tract-zipcode mapping here to filter for
	#data in requested zipcode.
	
	#Request data for a given county

	import itertools

	if len(census_vars_keys) > 40:

		keys1 = [census_vars_keys[0:2],census_vars_keys[2:30]]
		keys2 = [census_vars_keys[0:2],census_vars_keys[30:]]

		keys1 = list(itertools.chain.from_iterable(keys1))
		keys2 = list(itertools.chain.from_iterable(keys2))

		#print keys1

		#raise ValueError

		r1 = requests.get(format_census_request(keys1,county_code))
		r2 = requests.get(format_census_request(keys2,county_code))

		census_data_1 = r1.json()
		df1 = pd.DataFrame(census_data_1)
		df1.columns = df1.iloc[0]
		df1 = df1[1:].reset_index(drop=True)

		#df1 = df1.set_index(["tr","cty"])

		census_data_2 = r2.json()
		df2 = pd.DataFrame(census_data_2)
		df2.columns = df2.iloc[0]
		df2 = df2[1:].reset_index(drop=True)

		df2 = df2.set_index(["tr","cty"])

		df2.drop(['state','county','tract'], axis=1, inplace=True)

		census_df = df1.join(df2,on=["tr","cty"])

		census_df = census_df.reset_index(drop=True)

	else:	

		r = requests.get(format_census_request(census_vars_keys,county_code))
	
		census_data = r.json()
		census_df = pd.DataFrame(census_data)
		census_df.columns = census_df.iloc[0]
		census_df = census_df[1:].reset_index(drop=True)

	return census_df

def get_census_features(df,zipcode):
	dfsub = df[df['zipcode'] == zipcode]
	
	number_households = dfsub['DP03_0051E'].astype('float').sum()
	
	n_households = np.array([dfsub['DP03_0052E'].astype('float').sum(),  # < 10k
			dfsub['DP03_0053E'].astype('float').sum(),  # 10,000 to 14,999
			dfsub['DP03_0054E'].astype('float').sum(),  # 15,000 to 24,999
			dfsub['DP03_0055E'].astype('float').sum(),  # 25,000 to 34,999
			dfsub['DP03_0056E'].astype('float').sum(),  # 35,000 to 49,999
			dfsub['DP03_0057E'].astype('float').sum(),  # 50,000 to 74,999
			dfsub['DP03_0058E'].astype('float').sum(),  # 75,000 to 99,999
			dfsub['DP03_0059E'].astype('float').sum()]) # 100,000 to 149,999


	#raise Exception
	
	income = np.array([10.,12.5,20.,30.,42.5,62.5,87.5,125.0]) * 1000.
	average_income = np.sum(n_households * income) / np.sum(n_households)                  
	total_population = dfsub['DP05_0001E'].astype('float').sum()

	#something is wrong with this variable - get same values as for total pop
	latino_population = dfsub['DP05_0065E'].astype('float').sum()
	
	return number_households, average_income, total_population, latino_population

def tract_to_zip():

	"""
	Inputs:
		- None
	Outputs: 
		- (county, tract) - > (zipcode) dictionary
	Note:
		- Currently only for NY State, remove state = 36 flag for others
	"""

	df = pd.read_csv('../data/zcta_tract_rel_10.txt',dtype=str)

	#df = df[(data['STATE'] == '36') & (data['COUNTY'] == '061')].reset_index()
	df = df[(df['STATE'] == '36')].reset_index()

	tract_zip_dict = {}

	for index, row in df.iterrows():
		tract_zip_dict[(row['COUNTY'],row['TRACT'])] = row['ZCTA5']
	
	return tract_zip_dict

def zip_to_tract():
	df = pd.read_csv('../data/zcta_tract_rel_10.txt',dtype=str)

	int_county = df['COUNTY'].astype('int')

	df = df[(df['STATE'] == '36') & 
		((int_county == 5) | (int_county == 61) | (int_county == 81) |
			(int_county == 47) | (int_county == 85))].reset_index()

	#df = df[(df['STATE'] == '36') & (int_county == 61)].reset_index()

	ziplist = df["ZCTA5"].unique()

	zip_tract_dict = {}

	for zipval in ziplist:
	
		dfsub = df[df["ZCTA5"] == zipval]
		sublist = []
	
		for index, row in dfsub.iterrows():
			sublist.append([row['COUNTY'],row['TRACT']])
			zip_tract_dict[zipval] = sublist

	return zip_tract_dict

#def query_yelp(ziplist,cuisines):
	#get number of restaurants, average rating, ...

#	yelp_dict = {}
#	for zipcode in ziplist:
#		yelp_dict[zipcode] = {}
#		for cuisine in cuisines:
#			number_restaurants, average_rating = query_api(cuisine,zipcode)
#			yelp_dict[zipcode][cuisine] = [number_restaurants, average_rating]

#	return yelp_dict