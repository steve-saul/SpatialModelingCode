# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
import pickle

from functools import partial
import multiprocessing
from sklearn.model_selection import KFold

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor

from scipy.stats import uniform as sp_rand
from sklearn.model_selection import RandomizedSearchCV

from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, r2_score

# function for cutting the uncertenty using gmc and gv
def cutWithUncertainty(data,tvGmc,tvGv):
	# data: pandas dataframe
	screenGmc = data.loc[lambda df: df.gmc > tvGmc, :]
	screenGv = screenGmc.loc[lambda df: df.gv < tvGv, :]
	screenNull = data.loc[lambda df: df.gmc.isnull(), :]
	frames = [screenGv,screenNull]
	screen = pd.concat(frames)
	return screen

def doML(X,Y,Ids):
	# Data preparing
	train_index = Ids[0]
	test_index = Ids[1]
	X_train, X_test = X[train_index], X[test_index]
	y_train, y_test = Y[train_index], Y[test_index]
	# Linear model
	lmd = LinearRegression()
	lmd.fit(X_train,y_train)
	Y_pred_lin = lmd.predict(X_test)
	shapelen = len(Y_pred_lin.shape)
	if shapelen==1:
		Y_pred_lin = Y_pred_lin.reshape(-1,1)
	# MLP model
	mlp = MLPRegressor(activation="relu", alpha=1e-06, hidden_layer_sizes=650)
	mlp.fit(X_train,y_train)
	Y_pred_mlp = mlp.predict(X_test)
	shapelen = len(Y_pred_mlp.shape)
	if shapelen==1:
		Y_pred_mlp = Y_pred_mlp.reshape(-1,1)
	# SVR model
	svr = SVR(C=500,gamma=0.5)
	svr.fit(X_train,y_train)
	Y_pred_svr = svr.predict(X_test)
	shapelen = len(Y_pred_svr.shape)
	if shapelen==1:
		Y_pred_svr = Y_pred_svr.reshape(-1,1)

	y_test = y_test.reshape(-1,1)
	Data = np.concatenate((y_test,Y_pred_lin,Y_pred_mlp,Y_pred_svr),axis=1)
	return Data


def main():
	# load data
	all = pd.read_csv("allLabelledDataallPlusPrior.csv")
	# calculate the cutting values for gmc and gv
	gmc = all.loc[:,'gmc']
	gmc = gmc[gmc.isnull() == False]
	gv = all.loc[:,'gv']
	gv = gv[gv.isnull() == False]
	tvGmc = np.median(gmc)
	tvGv = np.median(gv)
	Gmc40 = np.percentile(gmc,40)
	Gv50 = np.percentile(gv,50)
	# cut the uncertenty
	#cutdata = cutWithUncertainty(all,tvGmc,tvGv)
	cutdata = cutWithUncertainty(all,Gmc40,Gv50)
	# scale the trainning set and testing set
	y = cutdata.iloc[:,[6]]
	x = cutdata.iloc[:,[4,5,9,10,13,14,15,16,17,18,19]]

	scalery = preprocessing.StandardScaler().fit(y)
	scalerX = preprocessing.StandardScaler().fit(x)

	Y = scalery.transform(y)
	Y = np.ravel(Y)
	X = scalerX.transform(x)
	#============================================================================================
	kf = KFold(n_splits=10,shuffle = True,random_state=12345)

	listIds = []
	for train_index, test_index in kf.split(X):
		listIds.append((train_index,test_index))

	pool = multiprocessing.Pool(10)
	func = partial(doML, X, Y)
	result_list=pool.map(func, listIds)
	pool.close()
	pool.join()
	#print result_list
	res = np.vstack(result_list)

	# Save the New dataset
	strFileName = 'SLData.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,res, delimiter=",")

	#============================================================================================
	# Construct the new dataset for Super Learner
	#============================================================================================
	# Linear Model
	'''
	lmd = LinearRegression()
	predicted_lmd = cross_val_predict(lmd, X_train, y_train, cv=10, n_jobs=30, pre_dispatch='2*n_jobs')
	lmdshapelen = len(predicted_lmd.shape)
	if lmdshapelen==1:
		predicted_lmd = predicted_lmd.reshape(-1,1)
	# SVR Model
	clf_svr = SVR(C=500,gamma=0.5)
	predicted_svr = cross_val_predict(clf_svr, X_train, y_train, cv=10, n_jobs=30, pre_dispatch='2*n_jobs')
	svrshapelen = len(predicted_svr.shape)
	if svrshapelen==1:
		predicted_svr = predicted_svr.reshape(-1,1)
	# MLP Model
	clf_mlp = MLPRegressor(activation="relu", alpha=1e-06, hidden_layer_sizes=650)
	predicted_mlp = cross_val_predict(clf_mlp, X_train, y_train, cv=10, n_jobs=30, pre_dispatch='2*n_jobs')
	mlpshapelen = len(predicted_mlp.shape)
	if mlpshapelen==1:
		predicted_mlp = predicted_mlp.reshape(-1,1)
	# New dataset
	SLData = np.concatenate((predicted_lmd,predicted_svr,predicted_mlp),axis=1)
	# Save the New dataset
	strFileName = 'SLData.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,SLData, delimiter=",")

	strFileName = 'SLDataY.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,y_train, delimiter=",")
	'''

	#=============================================================================================
	# Construct Super Learner (Ridge Regression)
	#=============================================================================================
	# Randomized Search for Algorithm Tuning
	# prepare a uniform distribution to sample for the alpha parameter
	param_grid = {'alpha': sp_rand()}
	# create and fit a ridge regression model, testing random alpha values
	Super_Model = Ridge()
	rsearch = RandomizedSearchCV(estimator=Super_Model, param_distributions=param_grid, n_iter=100, cv=10, n_jobs=40, pre_dispatch='2*n_jobs')
	rsearch.fit(res[:,(1,2,3)], res[:,0])
	#Super_Learner = rsearch.best_estimator_
	filename_super_learner = 'Super_learner.pkl'
	pickle.dump(rsearch, open(filename_super_learner, 'wb'))

	#super_test = Super_Learner_Train.predict(p_test)
	#test_all = np.concatenate((p_test,super_test.T,y_test),axis=1)

if __name__ == '__main__': main()
