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

#get list of populations by zip code - limit to New York County for now. 
df = pd.read_csv('../data/zcta_tract_rel_10.txt',dtype=str)
df.drop_duplicates(subset= 'ZCTA5', inplace = True)
df = df[(df['STATE'] == '36') & (df['COUNTY'] == '061')].head(40)

#ziplist = df.ZCTA5

#get list of restaurants per zip code for a representative list of zipcodes

	# to do later: incorporate tags for category_filter, and to eliminate 
	#businesses that already closed (both are in yelp api)

number_restaurants = []

for zipcode in df.ZCTA5:
	try:
		number_restaurants.append(query_api("japanese",str(zipcode)))
	except urllib2.HTTPError as error:
		number_restaurants.append(0)
		#sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

df['number_restaurants'] = number_restaurants

with open("../data/basic_table.json","w") as f:
	f.write(df.to_json())

df = pd.read_json("../data/basic_table.json")

print df.head(10)


#print zip(ziplist,number_restaurants)