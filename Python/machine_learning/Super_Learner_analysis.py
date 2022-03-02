# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
import pickle
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor

from sklearn.model_selection import cross_val_predict

from scipy.stats import uniform as sp_rand
from sklearn.model_selection import RandomizedSearchCV

from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, r2_score

# function for cutting the uncertenty using gmc and gv
def cutWithUncertainty(data,tvGmc,tvGv):
	# data: pandas dataframe
	screenGmc = data.loc[lambda df: df.gmc > tvGmc, :]
	screenGv = screenGmc.loc[lambda df: df.gv < tvGv, :]
	return screenGv

def main():
	#============================================================================================
	# load data
	all = pd.read_csv("allLabelledData.csv")
	# calculate the cutting values for gmc and gv
	gmc = all.loc[:,'gmc']
	gv = all.loc[:,'gv']
	tvGmc = np.median(gmc)
	tvGv = np.median(gv)
	Gmc40 = np.percentile(gmc,40)
	Gv50 = np.percentile(gv,50)
	# cut off the uncertenty
	cutdata = cutWithUncertainty(all,Gmc40,Gv50)
	# scale the trainning set and testing set
	y = cutdata.iloc[:,[6]]
	x = cutdata.iloc[:,[4,5,9,10,13,14,15,16,17,18,19]]
	X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.3,random_state=12345)
	scalerX = preprocessing.StandardScaler().fit(X_train)
	scalery = preprocessing.StandardScaler().fit(y_train)
	X_train = scalerX.transform(X_train)
	y_train = scalery.transform(y_train)
	X_test = scalerX.transform(X_test)
	y_test = scalery.transform(y_test)
	#============================================================================================

	#============================================================================================
	# Construct the new dataset for Super Learner
	#============================================================================================
	# Linear Model
	lmd = LinearRegression()
	predicted_lmd = cross_val_predict(lmd, X_train, y_train, cv=10, n_jobs=32, pre_dispatch='2*n_jobs')
	# SVR Model
	clf_svr = SVR(C=4000,gamma=0.5)
	predicted_svr = cross_val_predict(clf_svr, X_train, y_train, cv=10, n_jobs=48, pre_dispatch='2*n_jobs')
	# MLP Model
	clf_mlp = MLPRegressor(activation="relu", alpha=1e-06, hidden_layer_sizes=550)
	predicted_mlp = cross_val_predict(clf_mlp, X_train, y_train, cv=10, n_jobs=48, pre_dispatch='2*n_jobs')
	# New dataset
	SLData = np.concatenate((predicted_lmd,predicted_svr,predicted_mlp,y_train.T),axis=1)
	# Save the New dataset
	strFileName = 'SLData.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,SLData, delimiter=",")

	#=============================================================================================
	# Construct Super Learner with Train set (Ridge Regression)
	#=============================================================================================
	# Randomized Search for Algorithm Tuning
	# prepare a uniform distribution to sample for the alpha parameter
	param_grid = {'alpha': sp_rand()}
	# create and fit a ridge regression model, testing random alpha values
	Super_Model = Ridge()
	rsearch = RandomizedSearchCV(estimator=Super_Model, param_distributions=param_grid, n_iter=100, cv=10, n_jobs=32, pre_dispatch='2*n_jobs')
	rsearch.fit(SLData[:,(0,1,2)], SLData[:,3])
	Super_Learner_Train = rsearch.best_estimator_
	filename_super_learner_train = 'Super_learner_train.pkl'
	pickle.dump(Super_Learner_Train, open(filename_super_learner_train, 'wb'))

	#==============================================================================================
	# Fit the models with all Train data
	#==============================================================================================
	# linear
	lmd_train = LinearRegression()
	lmd_train.fit(X_train, y_train)
	# save the model to disk
	filename_Linear = 'Linear_train.pkl'
	pickle.dump(lmd_train, open(filename_Linear, 'wb'))
	# SVR
	clf_svr_train = SVR(C=4000,gamma=0.5)
	clf_svr_train.fit(X_train, y_train)
 	# save the model to disk
	filename_svr_train = 'SVR_train.pkl'
	pickle.dump(clf_svr_train, open(filename_svr_train, 'wb'))
	# MLP
	clf_mlp_train = MLPRegressor(activation="relu", alpha=1e-06, hidden_layer_sizes=550)
	clf_mlp_train.fit(X_train, y_train)
	# save the model to disk
	filename_MLP_train = 'MLP_train.pkl'
	pickle.dump(clf_mlp_train, open(filename_MLP_train, 'wb'))

	#==============================================================================================
	# Store the new super data of test
	#==============================================================================================
	lp = lmd_train.predict(X_test)
	sp = clf_svr_train.predict(X_test)
	mp = clf_mlp_train.predict(X_test)
	p_test_3 = np.concatenate((lp.T,sp.T,mp.T),axis=1)
	super_test = Super_Learner_Train.predict(p_test)
	test_all = np.concatenate((p_test,super_test.T,y_test),axis=1)
	# Save the New dataset
	strFileName = 'test_all.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,test_all, delimiter=",")


if __name__ == '__main__': main()
