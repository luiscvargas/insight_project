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
	zipcode = request.args.getlist("zipval")

	df = pd.read_json("app/static/dat/underserved_time_data.json")
 
	df = df.loc[float(zipcode[0]),:]  #float str () to remove unicode and match floating type

	borough = df.BOROUGH

	return render_template("zipcode.html",zip=str(zipcode[0]),borough=borough)

@app.route('/')
@app.route('/index')
@app.route('/input')
def restaurants_input():
	return render_template("input.html")

@app.route('/output',methods=["GET","POST"])
def restaurants_output():

	#SET DEFAUILT NUMBER OF ZIPCODES TO PRINT OUT
	NUMBER_ZIPCODES = 8

	#pull ID from input field and store it.

	#with open("app/static/dat/cuisine_types_enabled.json","r") as fp:
	#	cuisine_dict = json.load(fp)

	#with open("app/static/dat/cuisine_types_enabled.dat") as fp:
	#	cuisine_types = fp.read().strip("\n")

	with open("app/static/dat/yelp_api_data.json") as fp:
 		json1_str = fp.read() 
 		yelp = json.loads(json1_str)
		cuisine_types = yelp.keys()

	cuisine_usr = request.args.get("cuisine")
	boroughs = request.args.getlist("area")
	cuisine_usr = cuisine_usr.lower().strip()

	#convert alternate spellings

	if cuisine_usr in cuisine_types:
		cuisine_type = cuisine_usr
	else:
		return render_template("output.html",areas=[],cuisine=cuisine_types)
	
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
