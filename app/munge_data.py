#!/usr/bin/env python
# -*- coding: utf-8 -*-
from yelp_api import *
import argparse
import json
import pprint
import sys
import urllib
import urllib2
import oauth2
import numpy as np
import pandas as pd
import pprint
from api_import import *

#get list of populations by zip code - limit to New York County for now. 

zip_tract_dict = zip_to_tract()

tract_zip_dict = tract_to_zip()

ziplist = zip_tract_dict.keys() #if y[0] == '61']

ziplist = ziplist[0:3]

#query zillow data and get list of zipcodes and housing values for each zipcode

zillow_data = query_zillow(ziplist)

#specify features in census database

census_vars = [["DP03_0051E", {"description": "Total households"}],
["DP03_0052E" , {"description": "Total households < 10,000"}],
["DP03_0053E" , {"description": "Total households 10,000 to 14,999"}],
["DP03_0054E" , {"description": "Total households 15,000 to 24,999"}],
["DP03_0055E" , {"description": "Total households 25,000 to 34,999"}],
["DP03_0056E" , {"description": "Total households 35,000 to 49,999"}],
["DP03_0057E" , {"description": "Total households 50,000 to 74,999"}],
["DP03_0058E" , {"description": "Total households 75,000 to 99,999"}],
["DP03_0059E" , {"description": "Total households 100,000 to 149,999"}],
["DP05_0001E" , {"description": "Total population"}],
["DP05_0008E" , {"description": "Total population 20 to 24 years old"}],
["DP05_0009E" , {"description": "Total population 25 to 34 years old"}],
["DP05_0010E" , {"description": "Total population 35 to 44 years old"}],
["DP05_0011E" , {"description": "Total population 45 to 54 years old"}],
["DP05_0012E" , {"description": "Total population 55 to 59 years old"}],
["DP05_0013E" , {"description": "Total population 60 to 64 years old"}],
["DP05_0014E" , {"description": "Total population 65 to 74 years old"}],
["DP05_0015E" , {"description": "Total population 75 to 84 years old"}],
["DP05_0016E" , {"description": "Total population 85+"}],
["DP05_0039E" , {"description": "Race: Asian"}],
["DP05_0033E" , {"description": "Race: African American"}],
["DP05_0032E" , {"description": "Race: White"}],
["DP05_0034E" , {"description": "Race: American"}],
["DP05_0047E" , {"description": "Race: Native Hawaiian and Other Pacific Islander"}],
["DP05_0065E" , {"description": "Hispanic and Latino of any race"}]]

census_vars_keys = [x[0] for x in census_vars]

#get census information for all zip codes, one call per county/borough

county_list = {"05": "Bronx", "81": "Queens", "61": "Manhattan", 
			   "47": "Brooklyn", "85": "Staten Island"}

bronx_df = query_census(census_vars_keys, "05")
manhattan_df = query_census(census_vars_keys, "61")
queens_df = query_census(census_vars_keys, "81")
brooklyn_df = query_census(census_vars_keys, "47")
staten_df = query_census(census_vars_keys, "85")

#concatenate DataFrames for all boroughs

dfs = [manhattan_df,bronx_df,queens_df,brooklyn_df,staten_df]
census_df = pd.concat(dfs)

#add zipcode information to census_df
census_df.loc[:,'zipcode'] = 0
for index, row in census_df.iterrows():
    mytuple = (str(row["county"]),str(row["tract"]))
    if mytuple in tract_zip_dict.keys():
        census_df.loc[index,'zipcode'] = tract_zip_dict[mytuple]

#Build set of features

feature_array = []

for zipcode in ziplist:
    number_households, avg_income, population, latino_population = get_census_features(census_df,zipcode)
    value_index, value_median = zillow_data[zipcode]
    feature_array.append([zipcode, avg_income, population, value_index, value_median])

for row in feature_array:
	print row

#restaurants = []

#get list of restaurants per zip code for a representative list of zipcodes

	# to do later: incorporate tags for category_filter, and to eliminate 
	#businesses that already closed (both are in yelp api)


#for zipcode in zipcodes:
#	try:
#		restaurants.append(query_api("mexican",str(zipcode)))
#	except urllib2.HTTPError as error:
#		restaurants.append([])
		#sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))


#pprint.pprint(restaurants[0])

#df['number_restaurants'] = number_restaurants

#with open("../data/basic_table_mexican.json","w") as f:
#	f.write(df.to_json())

#df = pd.read_json("../data/basic_table_delete.json")

#print df.head(10)


#print zip(ziplist,number_restaurants)