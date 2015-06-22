
# coding: utf-8

import yelp_api_bounds
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import api_import 
#import json
import simplejson as json


# ##Searching By Category
# The yelp categories are found here: 
# https://www.yelp.com/developers/documentation/v2/all_category_list

def yelp_restaurant_categories(country="All"):
    with open("../data/yelp/categories.dat","r") as f:
        content = [x.strip('\n') for x in f.readlines()]
    
    category_dict = {}

    for item in content:
        words = item.split(",")
        cuisine_type = words[0]  #no need for strip() for name
        cuisine_category = words[1].strip()
        cuisine_language_support = words[2:]
        cuisine_language_support = [x.strip() for x in cuisine_language_support]
        if (country in cuisine_language_support) | ("All" in cuisine_language_support):
            category_dict[cuisine_category] = [cuisine_type, cuisine_language_support]
        
    return category_dict

#Load master dataframe
df = pd.read_json("../data/census_data.json")
df.set_index(['COUNTY_ID', 'TRACT_ID'],inplace=True,drop=True)

print(df.head(5))


# ##Keys associated with each business from API call
# u'is_claimed': <br>
# u'rating'<br>
# u'mobile_url'<br>
# u'rating_img_url'<br>
# u'review_count'<br>
# u'name'<br>
# u'rating_img_url_small'<br>
# u'url'<br>
# u'is_closed'<br>
# u'snippet_text'<br>
# u'categories'<br>
# u'rating_img_url_large'<br>
# u'id'<br>
# u'snippet_image_url'<br>
# u'location'

#Get dict with all restaurant categories and subset accessible from US. 

yelp_categories = yelp_restaurant_categories(country="US")

yelp_categories_usa = [{x: y[0]} for x,y in yelp_categories.items()]

for category in yelp_categories_usa:
    print category.keys()[0]," : ",category.values()[0]

#based on the list above

#category_cuisine_list = ["mexican","chinese"]  DONE

#category_cuisine_list = ["japanese", "latin", "greek"] DONE

#category_cuisine_list = ["puertorican","cuban","indpak","italian"] DONE

#category_cuisine_list = ["newamerican","tradamerican","vegetarian"] DONE

#category_cuisine_list = ["arabian", "brazilian", "cafes", "diners", "ethiopian", 
#"korean", "mideastern", "peruvian"] DONE

category_cuisine_list = ["colombian", "pizza", "seafood", "soup", "spanish", "french", 
"turkish", "vegan"]

#category_cuisine_list = ["japanese"]

print("You will get restaurants of the following categories:")
for category in category_cuisine_list:
    print category
raw_input("Press any key to continue   ")

#Query YELP API and get restaurant data

#yelp_dict = {}

with open("../data/yelp/yelp_api_data.json", 'r') as fp:
    yelp_dict = json.load(fp)

count_api_calls = 0

for category_cuisine in category_cuisine_list:
    yelp_dict[category_cuisine] = {}
    count = 0.0
    for irow, row in df.iterrows():
        lat_min = row['LATMIN']
        lat_max = row['LATMAX']
        long_min = row['LONGMIN']
        long_max = row['LONGMAX']
        bounds_str = "{0:<11.6f},{1:<11.6f}|{2:<11.6f},{3:<11.6f}".format(lat_min,long_max,lat_max,long_min) 
        bounds_str = bounds_str.replace(" ","")
        yelp_dict[category_cuisine][row.GEOID] = yelp_api_bounds.query_api("restaurant", category_cuisine, bounds_str)
        count_api_calls += 1
        count += 1
        if np.mod(count,5.) == 0:
            print category_cuisine, ", ", count,'...'


#save data to dictionary 
with open("../data/yelp/yelp_api_data.json", "w") as fp:
    json.dump(yelp_dict, fp, sort_keys=True)

print("You made {0} API calls".format(count_api_calls))



