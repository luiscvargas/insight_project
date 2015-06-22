#!/usr/bin/env 
# -*- coding: utf-8 -*-

import matplotlib as mpl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import api_import 
import simplejson as json
from sklearn import linear_model
from sklearn import ensemble
from sklearn.metrics import explained_variance_score

def create_feature_matrix(dataframe,feature_list,feature_cuisine,single_feature=False):

    np.set_printoptions(precision=8)
    
    #get size of matrix
    ncols = len(feature_list)
    nrows = len(dataframe)
        
    if single_feature == True:
        X_ = np.array(dataframe[feature_list].astype('float'))
        X_ = X_[:,np.newaxis]
    else:
        X = []
        for feature in feature_list:
            A = np.array(dataframe[feature].astype('float'))
            X.append(A)    
        X_ = np.vstack(X).T
    
    Y = np.array(dataframe[feature_cuisine].astype('float'))
    Y = Y[:,np.newaxis]
    X_ = np.nan_to_num(X_)
    
    return np.matrix(X_), np.matrix(Y)

#return first element of a group (for pandas groupby operations)
def first_element(x):
    return x.iloc[0]

#set to True to produce diagnostic plots and disable writing outputs
diagnose = False
plt.style.use('ggplot')

#Load yelp api dataframe
yelp = pd.read_json("../data/yelp/yelp_api_data.json")
with open("../data/yelp/yelp_api_data.json") as fp:
    json1_str = fp.read() 
    yelp = json.loads(json1_str)

cuisine_types = yelp.keys()

if diagnose == True:
    print(cuisine_types)

print(cuisine_types)

raise ValueError

#Load master dataframe
dftract = pd.read_json("../data/census_zillow_subway_yelp_data.json")
dftract.set_index(['COUNTY_ID', 'TRACT_ID'],inplace=True,drop=True)

if diagnose == True:
    print(dftract.columns)

#Add restaurant numbers to DF
#First, add features based on types of restaurants to be queried.
dftract['number_restaurants'] = 0.0
for category_cuisine in cuisine_types:
    dftract['number_restaurants_'+category_cuisine] = 0.0
    dftract['average_rating_restaurants_'+category_cuisine] = np.nan
    dftract['unweighed_average_rating_restaurants_'+category_cuisine] = np.nan
    dftract['closed_number_restaurants_'+category_cuisine] = 0.0
if diagnose == True: print(dftract.head(5))

for category_cuisine in cuisine_types:
    print category_cuisine
    for (key,value) in yelp[category_cuisine].items():
        scores = []
        weights = []
        closed_biz = 0.0
        open_biz = 0.0
        if len(value) > 0:
            for j in range(len(value)):
                if value[j]['is_closed'] == False:
                    #print "open!"
                    scores.append(float(value[j]['rating']))
                    weights.append(float(value[j]['review_count']))
                    open_biz += 1
                elif value[j]['is_closed'] == True:
                    #print "closed!"
                    closed_biz += 1
            scores = np.array(scores)
            weights = np.array(weights)
            #weighed_score = np.average(scores, weights = weights)
            unweighed_score = np.average(scores)
            #print key, open_biz, type(key), type(open_biz), type(df.ix[:,"GEOID"])
            dftract.loc[dftract["GEOID"].astype(str) == key,"number_restaurants_"+category_cuisine] = open_biz
            dftract.loc[dftract["GEOID"].astype(str) == key,"closed_number_restaurants_"+category_cuisine] = closed_biz
            #dftract.loc[dftract["GEOID"].astype(str) == key,"average_rating_restaurants_"+category_cuisine] = weighed_score
            dftract.loc[dftract["GEOID"].astype(str) == key,"unweighed_average_rating_restaurants_"+category_cuisine] = unweighed_score
            #print float(value[0]['rating']),float(value[0]['review_count'])



#Make dataframe at the zipcode level
dfzip = dftract.groupby('ZIPCODE').apply(sum)
dfzip2 = dftract.groupby('ZIPCODE').apply(np.mean)
dfzip3 = dftract.groupby('ZIPCODE').apply(first_element)
dfzip['FRAC_LAND'] = dfzip['ALAND'] / (dfzip['ALAND'] + dfzip['AWATER'])
dfzip['INTPTLAT'] = dfzip2['INTPTLAT']
dfzip['INTPTLONG'] = dfzip2['INTPTLONG']
dfzip['fraction_latino'] = dfzip['pop_latino']/dfzip['pop_total']
dfzip['fraction_asian'] = dfzip['pop_asian']/dfzip['pop_total']
dfzip['fraction_white'] = dfzip['pop_white']/dfzip['pop_total']
dfzip['fraction_black'] = dfzip['pop_black']/dfzip['pop_total']
dfzip['pop_density'] = dfzip['transient_residential_pop'] / dfzip['ALAND']
dfzip['hhmean'] = dfzip2['hhmean']
dfzip['hhmedian'] = dfzip2['hhmedian']
dfzip['house_median'] = dfzip2['house_median']
dfzip['house_index'] = dfzip2['house_index']
dfzip['median_owned'] = dfzip2['median_owned']
dfzip['median_rent'] = dfzip2['median_rent']
dfzip['BOROUGH'] = dfzip3['BOROUGH']
dfzip = dfzip.drop(0,axis=0)

dfzip.drop("ZIPCODE",axis=1,inplace=True)
df = dfzip
#Choose to do analysis at zipcode or tract level, default: zipcode
#df = dfzip.set_index("ZIPCODE")

if diagnose == True:
    print("Number of columns in database: ",len(df.columns))
    print("Number of rows in database: ",len(df))
    print(df.head(5))

#Add additional features
df['fraction_asian'] = (df['pop_asian'] / df['pop_total'])
df['fraction_latino'] = (df['pop_latino'] / df['pop_total'])
df['fraction_white'] = (df['pop_white'] / df['pop_total'])
df['fraction_black'] = (df['pop_black'] / df['pop_total'])
df['fraction_black'] = (df['pop_black'] / df['pop_total'])
df['pop_density'] = df['transient_residential_pop'] / df['ALAND']

for cuisine_type in cuisine_types:
    df['number_restaurants'] = df['number_restaurants'] + df['number_restaurants_'+cuisine_type]

df['number_restaurants_capita'] = 10000.0 * (df['number_restaurants'] / df['transient_residential_pop']).replace([np.inf,-np.inf,np.nan],0.0)


for cuisine_type in cuisine_types:
    df['number_restaurants_capita_'+cuisine_type] = 10000.0 *\
    (df['number_restaurants_'+cuisine_type] / df['transient_residential_pop']).replace([np.inf,-np.inf,np.nan],0.0) 

if diagnose == True:
    print("Added additional features ...")
    print("Number of columns in database: ",len(df.columns))
    print("Number of rows in database: ",len(df))
    print(df.head(5))

    mpl.rcParams['figure.figsize'] = (7,4)
    n, bins, patches = plt.hist(np.array(df['number_restaurants']),bins=100,alpha=0.5);
    plt.hist(np.array(df['number_restaurants_mexican']),bins=bins,alpha=0.5);
    plt.xlim([0,60])
    plt.show()

#Restrict analysis to subset of data, where:
#Census tracts / zipcodes where number of restaurants is != 0
#Census tracts / zipcodes where fraction of land mass > 0.8
#Rationale: Areas with NO restaurants at all may be zoned completely residential. 
#While lacking access to zoning data, this is best heuristic.


dfsub = df.loc[(df['FRAC_LAND'] > 0.5) & (df['number_restaurants'] > 0.0),:]
if diagnose == True:
    print(len(dfsub)," rows after clearing census tracts without any restaurants")
    dfsub.head(5)

#cuisine_types = ["chinese","mexican"]

#Define set of features 
pred_features = ['pop_density','STATION_DISTANCE','hhmedian','median_owned','median_rent',
    'pop_asian','pop_black','pop_indpak','pop_latino','pop_total','pop_white','transient_pop',
    'transient_residential_pop','fraction_asian','fraction_latino']

print len(cuisine_types)

raw_input("enter to continue?")

cuisine_types.append("all")

for cuisine_type in cuisine_types:

    print(cuisine_type)

    if cuisine_type == "all":
        feature_cuisine = "number_restaurants"
        feature_cuisine_capita = "number_restaurants_capita"
    else:
        feature_cuisine = "number_restaurants_"+cuisine_type
        feature_cuisine_capita = "number_restaurants_capita_"+cuisine_type

    if diagnose == True:

        mpl.rcParams['figure.figsize'] = (7,4)
        dfsub[feature_cuisine_capita].hist(bins=100)
        plt.show()

        mpl.rcParams["figure.figsize"] = (6,6)
        plt.scatter(dfsub["INTPTLONG"],dfsub["INTPTLAT"],s=20,color="blue",alpha=0.5)
        plt.xlabel("LONG"); plt.ylabel("LAT")
        plt.show()

    #Linear Model - Feature Selection

    nfeatures = len(pred_features)

    mpl.rcParams["font.size"] = 9
    mpl.rcParams["figure.figsize"] = (14,8)
    gs = gridspec.GridSpec(5, 4)
    if diagnose == True: fig = plt.figure()
    for i,feature in enumerate(pred_features):

        X_, y_ = create_feature_matrix(dfsub,feature,feature_cuisine,single_feature=True)

        clf = linear_model.LinearRegression()
        clf.fit(X_,y_)
        R2 = clf.score(X_,y_)
    
        if diagnose == True:
            ax = fig.add_subplot(gs[i])
            ax.scatter(dfsub[feature],dfsub[feature_cuisine],s=5,alpha=0.8,color="blue")
            ax.set_xlabel(feature)
            ax.set_ylim([0,50])
            ax.ticklabel_format(axis="x",style = 'sci', scilimits=(-1,1)) 

            #plot best-fit line 
            xline = np.linspace(X_.min(),X_.max(),100)
            yline = clf.predict(xline[:,np.newaxis])
    
            ax.plot(xline,yline,color='red',ls='-',lw=2)
    
            ax.text(X_.min(),45,"{0:<7.4f}".format(R2))
    
        print("{0:20s}: {1:<6.4f}".format(feature, R2))

    if diagnose == True:
        plt.show()

    gs = gridspec.GridSpec(5, 4)
    if diagnose == True: fig = plt.figure()

    for i,feature in enumerate(pred_features):
        
        X_, y_ = create_feature_matrix(dfsub,feature,feature_cuisine_capita,single_feature=True)

        clf = linear_model.LinearRegression()
        clf.fit(X_,y_)
        R2 = clf.score(X_,y_)

        if diagnose ==  True:
            ax = fig.add_subplot(gs[i])
            feature_cuisine = "number_restaurants_capita_"+cuisine_type
            ax.scatter(dfsub[feature],dfsub[feature_cuisine],s=5,alpha=0.8,color="blue")
            ax.set_xlabel(feature)
            ax.set_ylim([0,0.5])
            ax.ticklabel_format(axis="x",style = 'sci', scilimits=(-1,1))
                                    #plot best-fit line 
            xline = np.linspace(X_.min(),X_.max(),100)
            yline = clf.predict(xline[:,np.newaxis])
                    
            ax.plot(xline,yline,color='red',ls='-',lw=2)
            ax.text(0,0.45,"{0:<7.4f}".format(R2))
                
        print("{0:20s}: {1:<6.4f}".format(feature, R2))

    if diagnose == True:
        plt.show()

    #Add function here to only use the top scoring features? Maybe different features for each 
    #type of cuisine?

    X_, y_ = create_feature_matrix(dfsub,pred_features,feature_cuisine,single_feature=False)

    #Linear Regression, All Features

    clf_linear = linear_model.LinearRegression()
    clf_linear.fit(X_,y_)
    R2_linear = clf_linear.score(X_,y_)
    print("Linear Regression R^2 = ",R2_linear)
    yfit_linear = clf_linear.predict(X_)
    #print "MSE = ",metrics.mean_squared_error(y_,clf.predict(X_))

    #Lasso Regression, All Features
    #
    for alpha in np.logspace(-6,0.5,5):
        clf_lasso = linear_model.Lasso(alpha=alpha)
        clf_lasso.fit(X_,y_)
        R2_lasso = clf_lasso.score(X_,y_)
        print "Lasso Regression R^2 = ",R2_lasso," ,alpha = ",alpha

    #Ridge Regression, All Features
    for alpha in np.logspace(-6,0.5,5):
        clf_ridge = linear_model.Ridge(alpha=alpha)
        clf_ridge.fit(X_,y_)
        R2_ridge = clf_ridge.score(X_,y_)
        print("Ridge Regression R^2 = ",R2_ridge," ,alpha = ",alpha)

    #Lasso Lars Regression: Best if alpha->0 ie regular Linear Regression
    #note: highest R2 when alpha->0

    clf_lassolars = linear_model.LassoLars(alpha=0.1,verbose=True)
    clf_lassolars.fit(X_,y_)
    R2_lassolars = clf_lassolars.score(X_,y_)
    print("Lasso Lars Regression R^2 = ",R2_lassolars)  

    # Deviation between Prediction and Data

    yfit_linear = np.ravel(clf_linear.predict(X_))
    yfit_lasso = np.ravel(clf_lasso.predict(X_))
    yfit_ridge = np.ravel(clf_ridge.predict(X_))
    yfit_lassolars = clf_lassolars.predict(X_)

    dx_linear = np.ravel(y_)-yfit_linear
    dx_lasso = np.ravel(y_)-yfit_lasso
    dx_ridge = np.ravel(y_)-yfit_ridge
    dx_lassolars = np.ravel(y_)-yfit_lassolars

    stddev_linear = np.std(dx_linear)   
    stddev_lasso = np.std(dx_lasso)
    stddev_ridge = np.std(dx_ridge)
    stddev_lassolars = np.std(dx_lassolars)

    dx_linear = dx_linear / stddev_linear
    dx_lasso = dx_lasso / stddev_lasso
    dx_ridge = dx_ridge / stddev_ridge
    dx_lassolars = dx_lassolars / stddev_lassolars

    print(stddev_linear)
    print(stddev_lasso)
    print(stddev_ridge)
    print(stddev_lassolars)

    if diagnose == True:
        mpl.rcParams['figure.figsize'] = (13,4)
        fig = plt.figure()
        ax1 = fig.add_subplot(121)
        n, bins, patches = ax1.hist(np.ravel(y_)-yfit_lassolars,bins=30,alpha=0.2);
        ax1.hist(np.ravel(y_)-yfit_ridge,bins=bins,alpha=0.2);
        ax2 = fig.add_subplot(122)
        ax2.hist(np.ravel(y_)-yfit_lasso,bins=bins,alpha=0.2);
        ax2.hist(np.ravel(y_)-yfit_linear,bins=bins,alpha=0.2);
        plt.show()

    if len(yfit_linear) != len(dfsub): raise ValueError

    #Random Forest and Ensemble Classifiers

    clf_rf = ensemble.RandomForestRegressor(n_estimators=10,max_depth=7,verbose=0)
    clf_rf.fit(X_,np.ravel(np.array(y_)))
    yfit_rf = clf_rf.predict(X_)
    R2_rf = clf_rf.score(X_,np.ravel(np.array(y_)))
    print("R2 Random Forest = ",R2_rf)

    #How does R2 change with max depth?
    #How does R2 change with number estimators

    if diagnose == True:
        max_depth_list = np.arange(15) + 1
        R2_rf_list = []
        for depth in max_depth_list:
            clf_rf_tmp = ensemble.RandomForestRegressor(n_estimators=10,max_depth=depth,verbose=1)
            clf_rf_tmp.fit(X_,np.ravel(np.array(y_)))
            yfit_rf_tmp = clf_rf_tmp.predict(X_)
            R2_rf_list.append(clf_rf_tmp.score(X_,np.ravel(np.array(y_))))

        mpl.rcParams["figure.figsize"] = (10,4)
        plt.plot(max_depth_list,R2_rf_list,lw=2)
        plt.xlabel("max_depth")
        plt.ylabel("R^2")
        plt.show()


        number_estimators_list = np.arange(1,30)
        R2_rf_list_2 = []
        for n in number_estimators_list:
            clf_rf_tmp = ensemble.RandomForestRegressor(n_estimators=n,max_depth=depth,verbose=1)
            clf_rf_tmp.fit(X_,np.ravel(np.array(y_)))
            yfit_rf_tmp = clf_rf_tmp.predict(X_)
            R2_rf_list_2.append(clf_rf_tmp.score(X_,np.ravel(np.array(y_))))

        mpl.rcParams["figure.figsize"] = (10,4)
        plt.plot(number_estimators_list,R2_rf_list_2,lw=2)
        plt.xlabel("N Estimators")
        plt.ylabel("R^2")
        plt.show()

    #In conclusion want roughly ~ 5+ estimators (10 is ok), and max_depth >= 7.

    dx_rf = np.ravel(y_) - yfit_rf
    stddev_rf = np.std(dx_rf)
    dx_rf = dx_rf / stddev_rf

    print("Feature Importances from Random Forest")
    print(zip(clf_rf.feature_importances_,pred_features))

    plt.hist(dx_rf,bins=30);
    if diagnose == True: plt.show()

    #Plot true vs predicted for the four models
    mpl.rcParams["figure.figsize"] = (10,6)
    plt.scatter(y_,yfit_linear,s=10,color="blue")
    plt.scatter(y_,yfit_lasso,s=10,color="green")
    plt.scatter(y_,yfit_rf,s=10,color="red")
    if diagnose == True: plt.show()

    plt.scatter(dx_linear,dx_rf,s=10,color="black")
    plt.plot([-4,4],[-4,4],lw=2,ls="--",color="blue")
    plt.axis([-2,2,-2,2])
    plt.xlabel("Deviation Linear Model (Scaled by Std Dev)")
    plt.ylabel("Deviation RF Model (Scaled by Std Dev")
    if diagnose == True: plt.show()

    #Restaurants per Capita
    plt.hist(np.array(dfsub[feature_cuisine_capita]),bins=np.arange(0,10,0.1))
    if diagnose == True: plt.show()

    dfsub.loc[:,"dx_linear_raw_"+cuisine_type] = dx_linear * stddev_linear
    dfsub.loc[:,"dx_rf_raw_"+cuisine_type] = dx_rf * stddev_rf
    dfsub.loc[:,"dx_linear_"+cuisine_type] = dx_linear
    dfsub.loc[:,"dx_rf_"+cuisine_type] = dx_rf
    dfsub.loc[:,"r2_rf_"+cuisine_type] = R2_rf
    dfsub.loc[:,"r2_linear_"+cuisine_type] = R2_linear
    dfsub.loc[:,"stddev_rf_"+cuisine_type] = stddev_rf
    dfsub.loc[:,"stddev_linear_"+cuisine_type] = stddev_linear

    print dfsub.head(3)

dfsub.to_json("../data/underserved_data.json")

    #sort zipcodes by those with few restaurants
    #dfsort = dfsub.sort(columns=feature_cuisine_capita, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
    #sorted_indices = dfsort.index.values

    #print(dfsort.head(10)[['transient_residential_pop','pop_total',feature_cuisine_capita,'number_restaurants']])




