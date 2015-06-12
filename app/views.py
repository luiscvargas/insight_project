from flask import render_template, request
from app import app
import pymysql as mdb
import numpy as np

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

@app.route('/output')
def restaurants_output():
	#pull ID from input field and store it.
	cuisine = request.args.get("ID")

	if cuisine.lower() == "mexican":
		cuisine_code = "MEX"
	elif cuisine.lower() == "japanese":
		cuisine_code = "JPN"
	elif cuisine.lower() == "american":
		cuisine_code = "AME"
	else:
		return render_template("output.html",areas=[],cuisine=cuisine)

	query_results = np.genfromtxt("/Users/deneb/insight/insight_project/data/zip_codes_"+cuisine_code+".csv",delimiter=",",
		names="zipcode,score",usecols=(0,1))

	query_results = query_results[0:5]  #only top five

	areas = []
	for result in query_results:
		areas.append(dict(zipcode="{0:<5d}".format(int(result[0])),score="{0:<5.2f}".format(result[1])))

	#call a function from a_Model package, note we are only pulling one result in the query

	#pop_input = cities[0]['population']
	#the_result = ModelIt(city,pop_input)

	return render_template("output.html",areas=areas,cuisine=cuisine)  #, the_result=the_result)
