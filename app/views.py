from flask import render_template, request
from app import app
import pymysql as mdb
import numpy as np
import simplejson as json
import string
import pandas as pd

#db = mdb.connect(user="root",host="localhost",db="world_innodb",
#	charset='utf8',unix_socket="/opt/local/var/run/mysql56/mysqld.sock")

#@app.route('/')
#@app.route('/index')
#def index():
#	user = { 'nickname': 'Luis' }
#	return render_template("index.html",
#		title = "Home",
#		user = user)

#@app.route('/db_fancy')
#def cities_page_fancy():
#	with db:
#		cur = db.cursor()
#		cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")
#		query_results = cur.fetchall()
#	cities = []
#	for result in query_results:
#		cities.append(dict(name=result[0], country=result[1], population=result[2]))
#	return render_template('cities.html', cities=cities)

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

	with open("app/static/dat/cuisine_types_enabled.json","r") as fp:
		cuisine_dict = json.load(fp)

	with open("app/static/dat/cuisine_types_enabled.dat") as fp:
		cuisine_types = fp.read().strip("\n")


	cuisine_usr = request.args.get("cuisine")
	boroughs = request.args.getlist("area")
	print cuisine_usr.lower(), boroughs

	#convert alternate spellings
	try: 
		cuisine_type = cuisine_dict[cuisine_usr.lower()]
	except: 
		with open("app/static/dat/cuisine_types_enabled.dat") as fp:
			cuisine_types = fp.read().split("\n")
			cuisine_types = [x for x in cuisine_types if len(x) != 0]
		return render_template("output.html",areas=[],cuisine=cuisine_types)

	df = pd.read_json("app/static/dat/underserved_data.json")

	dx_linear = "dx_linear_"+cuisine_type
	dx_rf = "dx_rf_"+cuisine_type
	feature_cuisine = "number_restaurants_"+cuisine_type
	feature_cuisine_capita = "number_restaurants_capita_"+cuisine_type

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
		feature_cuisine,feature_cuisine_capita,"dx_linear_"+cuisine_type]]

	boroughs = dfsub.BOROUGH.tolist()
	deviation = dfsub["dx_linear_"+cuisine_type]
	deviations = ["{0:<5.1f}".format(-1.*x).strip() for x in dfsub["dx_linear_"+cuisine_type].tolist()]
	zipcodes = [str(int(x)) for x in dfsub.index.values.tolist()]

	areas = zip(zipcodes,boroughs,deviations)

	#query_results = np.genfromtxt("/Users/deneb/insight/insight_project/data/zip_codes_"+cuisine_code+".csv",delimiter=",",
	#	names="zipcode,score",usecols=(0,1))

	#query_results = query_results[0:5]  #only top five

	#areas = []
	#for result in query_results:
	#	areas.append(dict(zipcode="{0:<5d}".format(int(result[0])),score="{0:<5.2f}".format(result[1])))

	#call a function from a_Model package, note we are only pulling one result in the query

	#pop_input = cities[0]['population']
	#the_result = ModelIt(city,pop_input)

	return render_template("output.html",areas=areas,cuisine=cuisine_type)  #, the_result=the_result)
