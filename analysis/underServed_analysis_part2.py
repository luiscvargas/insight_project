import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import simplejson as json
import matplotlib as mpl
import matplotlib.gridspec as gridspec

"""
add restaurant = f(time) data information as well as composite score
"""

diagnose = False

#read-in results json file from underserved_analysis.py
dfcensus = pd.read_json("../data/underserved_data.json")
zips_nyc_int = [int(x) for x in dfcensus.index]

#read in census business data
df98 = pd.read_csv("../data/census_business/zbp98detail.txt").set_index("zip").loc[:,['naics','est']]
df01 = pd.read_csv("../data/census_business/zbp01detail.txt").set_index("zip").loc[:,['naics','est']]
df02 = pd.read_csv("../data/census_business/zbp02detail.txt").set_index("ZIP").loc[:,['NAICS','EST']]
df04 = pd.read_csv("../data/census_business/zbp04detail.txt").set_index("zip").loc[:,['naics','est']]
df07 = pd.read_csv("../data/census_business/zbp07detail.txt").set_index("zip").loc[:,['naics','est']]
df10 = pd.read_csv("../data/census_business/zbp10detail.txt").set_index("zip").loc[:,['naics','est']]
df12 = pd.read_csv("../data/census_business/zbp12detail.txt").set_index("zip").loc[:,['naics','est']]
df02.rename(index={'ZIP': 'zip'},columns={'NAICS': 'naics', 'EST': 'est'}, inplace=True)

dfin = [df98,df01,df02,df04,df07,df10,df12]
year = ['1998','2001','2002','2004','2007','2010','2012']
dfout = []
for idf, df_ in enumerate(dfin):
    dftmp = df_.loc[df_['naics'] == '72----',['est']]
    est_str = year[idf]
    dfout.append(dftmp.rename(columns={"est":est_str}))

#Join dataframes on zipcode
for idf,df_ in enumerate(dfout):
    if idf == 0:
        dfall = df_
    else:
        dfall = dfall.join(df_)

#add variables for change in number restaurants with time
dfall["dNdt"] = dfall["2012"] / dfall["2001"]
dfall["dNdt_short"] = dfall["2012"] / dfall["2007"]

#reduce number of zipcodes to those in NYC area only.
dfall = dfall.loc[zips_nyc_int,:]

if diagnose == True:
	mpl.rcParams['figure.figsize'] = (12,6)
	fig = plt.figure()
	ax = fig.add_subplot(121)
	int_years = [int(x) for x in year]
	for irow,row in dfall.iterrows():
		ax.plot(int_years,row[year],marker="o",ls="--",lw=0.5)

	ax.set_xlabel("Year")
	ax.set_ylabel("Number of Restaurants")
	ax.set_xlim([2000,2014])
	ax.set_ylim([0,60])

	ax = fig.add_subplot(122)
	int_years = [int(x) for x in year]
	for irow,row in dfall.iterrows():
		ax.plot(int_years,row[year],marker="o",ls="--",lw=0.5)
	ax.set_xlabel("Year")
	ax.set_ylabel("Number of Restaurants")
	ax.set_xlim([2000,2014])
	ax.set_ylim([0,15])


#join dfcensus and dfall on zipcode (which is the index on both DFs)

df_master = dfcensus.join(dfall)

#add additional scores, first get cuisine_types

yelp = pd.read_json("../data/yelp/yelp_api_data.json")
with open("../data/yelp/yelp_api_data.json") as fp:
	json1_str = fp.read() 
	yelp = json.loads(json1_str)
cuisine_types = yelp.keys()

df_master["dNdt_scaled"] = df_master["dNdt"] / df_master["dNdt"].median()
df_master["dNdt_short_scaled"] = df_master["dNdt_short"] / df_master["dNdt_short"].median()

for cuisine in cuisine_types:
	df_master['composite_score_'+cuisine] = df_master['dNdt_scaled'] * df_master['dx_linear_'+cuisine]

#save augmented dataframe 

df_master.to_json("../data/underserved_time_data.json")

