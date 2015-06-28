#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request
from app import app
import numpy as np
import simplejson as json
import string
import pandas as pd
#import pymysql as mdb

@app.route('/zipcode',methods=["GET"])
def zipcode_box():
	values = str(request.args.getlist("zipval")[0]).split("_")

	zipcode = values[0]
	cuisine = values[1]

	df = pd.read_json("app/static/dat/underserved_time_data.json")
 
	df = df.loc[float(zipcode),:]  #float str () to remove unicode and match floating type

	cuisine_dict = {"Mexican": "mexican", 
	"Chinese": "chinese", "Japanese": "japanese", "Latin": "latin", 
	"Greek": "greek","Puerto Rican": "puertorican","Cuban": "cuban",
	"Indian": "indpak","Italian":"italian","Modern American": "newamerican",
    "Traditional American": "tradamerican","Vegetarian": "vegetarian",
    "Arabian": "arabian", "Brazilian": "brazilian", 
    "Cafes": "cafes", "Diners": "diners", "Ethiopian": "ethiopian", 
    "Korean": "korean", "Middle Eastern": "mideastern", 
	"Peruvian": "peruvian", "Colombian": "colombian", "Pizza": "pizza", 
	"Seafood": "seafood", "Soup": "soup","Spanish": "spanish", 
	"French": "french", "Turkish": "turkish", "Vegan": "vegan"} 

	cuisine_title = [x for (x,y) in cuisine_dict.items() if y == cuisine][0]

	borough = df.BOROUGH

	#create url for yelp query:
 
	if zipcode == "":
		yelp_url = "#"
	else:
		yelp_url = "http://www.yelp.com/search?find_desc=Restaurants"+"&find_loc="+zipcode+"&ns=1&cflt="+cuisine

	growth_rate = ["{0:<5.1f}".format(df.dNdt_scaled),"{0:<5.1f}".format(df.dNdt)]

	if df['dx_linear_'+cuisine] < 0.0:
		dx_str = "0"
	else:
		dx_str = "1"

	if df['dx_linear_'+cuisine] < -3.0:
		recommendation = "strong"
	elif (df['dx_linear_'+cuisine] >= -3.0) & (df['dx_linear_'+cuisine] < -2.0):
		recommendation = "moderate"
	elif (df['dx_linear_'+cuisine] >= -2.0) & (df['dx_linear_'+cuisine] < 0.0):
		recommendation = "weak"	
	else:
		recommendation = ""


	dx = ["{0:<5.1f}".format(np.abs(df['dx_linear_'+cuisine])),"{0:<5.1f}".format(df['composite_score_'+cuisine]),
		dx_str,recommendation]

	#http://www.yelp.com/search?find_desc=Restaurants&find_loc=10023&ns=1#find_desc=restaurants+indpak

	#yelp_url = "http://www.yelp.com/search?find_desc=restaurants+indpak&find_loc=11377&ns=1"

	return render_template("zipcode.html",zip=str(zipcode),borough=borough,cuisine_title=cuisine_title,yelp_url=yelp_url,
		growth_rate=growth_rate,dx=dx)

@app.route('/')
@app.route('/index')
@app.route('/input')
def restaurants_input():
	return render_template("input.html")

@app.route('/output',methods=["GET","POST"])
def restaurants_output():

	#SET DEFAUILT NUMBER OF ZIPCODES TO PRINT OUT
	NUMBER_ZIPCODES = 7

	#pull ID from input field and store it.

	#with open("app/static/dat/cuisine_types_enabled.json","r") as fp:
	#	cuisine_dict = json.load(fp)

	#with open("app/static/dat/cuisine_types_enabled.dat") as fp:
	#	cuisine_types = fp.read().strip("\n")

	with open("app/static/dat/yelp_api_data.json") as fp:
 		json1_str = fp.read() 
 		yelp = json.loads(json1_str)
		cuisine_types = yelp.keys()

	cuisine_dict = {"Mexican": "mexican", 
	"Chinese": "chinese", "Japanese": "japanese", "Latin": "latin", 
	"Greek": "greek","Puerto Rican": "puertorican","Cuban": "cuban",
	"Indian": "indpak","Italian":"italian","Modern American": "newamerican",
    "Traditional American": "tradamerican","Vegetarian": "vegetarian",
    "Arabian": "arabian", "Brazilian": "brazilian", 
    "Cafes": "cafes", "Diners": "diners", "Ethiopian": "ethiopian", 
    "Korean": "korean", "Middle Eastern": "mideastern", 
	"Peruvian": "peruvian", "Colombian": "colombian", "Pizza": "pizza", 
	"Seafood": "seafood", "Soup": "soup","Spanish": "spanish", 
	"French": "french", "Turkish": "turkish", "Vegan": "vegan"} 


	cuisine_usr = request.args.get("cuisine").strip().title()
	boroughs = request.args.getlist("area")

	try:
		cuisine_type = cuisine_dict[cuisine_usr]
	except:
		#return list of cuisines if no match
		return render_template("output.html",areas=[],cuisine=cuisine_dict.keys())
	
	#try: 
	#	cuisine_type = cuisine_dict[cuisine_usr.lower()]
	#except: 
	#	with open("app/static/dat/cuisine_types_enabled.dat") as fp:
	#		cuisine_types = fp.read().split("\n")
	#		cuisine_types = [x for x in cuisine_types if len(x) != 0]
	#	return render_template("output.html",areas=[],cuisine=cuisine_types)


	df = pd.read_json("app/static/dat/underserved_time_data.json")

	dx_linear = "dx_linear_"+cuisine_type
	dx_rf = "dx_rf_"+cuisine_type
	feature_cuisine = "number_restaurants_"+cuisine_type
	feature_cuisine_capita = "number_restaurants_capita_"+cuisine_type
	dx_composite = "composite_score_" + cuisine_type

	#restrict to areas within boroughs specified
	if boroughs != []:
		if "nyc" not in boroughs:
			df_arr = []
			for borough in boroughs:	
				df_arr.append(df[df['BOROUGH'].str.lower() == borough])
			df = pd.concat(df_arr)

	dfsub = df.sort(columns=dx_linear, axis=0, 
        ascending=True, inplace=False, kind='quicksort', 
        na_position='last').head(NUMBER_ZIPCODES)[["BOROUGH","pop_total",
		feature_cuisine,feature_cuisine_capita,dx_linear,dx_rf,dx_composite,"dNdt","dNdt_scaled"]]

	boroughs = dfsub.BOROUGH.tolist()
	#deviation = dfsub["dx_linear_"+cuisine_type]
	score_linear = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub[dx_linear].tolist()]
	score_rf = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub[dx_rf].tolist()]
	score_composite = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub[dx_composite].tolist()]
	dNdt = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub["dNdt"].tolist()]
	dNdt_scaled = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub["dNdt_scaled"].tolist()]

	zipcodes = [str(int(x)) for x in dfsub.index.values.tolist()]

	areas = zip(zipcodes,boroughs,score_linear,score_rf,score_composite,dNdt,dNdt_scaled)

	#call a function from a_Model package, note we are only pulling one result in the query

	#pop_input = cities[0]['population']
	#the_result = ModelIt(city,pop_input)

	return render_template("output.html",areas=areas,cuisine=cuisine_type)  #, the_result=the_result)
