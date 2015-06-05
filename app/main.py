from yelp_api import *
import argparse
import json
import pprint
import sys
import urllib
import urllib2
import oauth2

#get list of restaurants per zip code for a representative list of zipcodes

	# to do later: incorporate tags for category_filter, and to eliminate 
	#businesses that already closed (both are in yelp api)

ziplist = [10020,10021,10022,10023,10024]
number_restaurants = []

for zipcode in ziplist:
	try:
		number_restaurants.append(query_api("japanese",str(zipcode)))
	except urllib2.HTTPError as error:
		number_restaurants.append(0)
		#sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

print zip(ziplist,number_restaurants)