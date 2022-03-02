# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
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

	y_train = scalery.transform(y)
	y_train = np.ravel(y_train)
	X_train = scalerX.transform(x)

	# Set the best parameters from cross-validation
	clf = SVR(C=2000,gamma=0.5)
	clf.fit(X_train, y_train)
 	# save the model to disk
	filename_svr = 'SVR_C2000_05.pkl'
	pickle.dump(clf, open(filename_svr, 'wb'))

	# Set the best parameters from cross-validation
	clf = SVR(C=1000,gamma=0.5)
	clf.fit(X_train, y_train)
 	# save the model to disk
	filename_svr = 'SVR_C1000_05.pkl'
	pickle.dump(clf, open(filename_svr, 'wb'))

	# Set the best parameters from cross-validation
	clf = SVR(C=2000,gamma=0.2)
	clf.fit(X_train, y_train)
 	# save the model to disk
	filename_svr = 'SVR_C2000_02.pkl'
	pickle.dump(clf, open(filename_svr, 'wb'))

	# Set the best parameters from cross-validation
	clf = SVR(C=1000,gamma=0.2)
	clf.fit(X_train, y_train)
 	# save the model to disk
	filename_svr = 'SVR_C1000_02.pkl'
	pickle.dump(clf, open(filename_svr, 'wb'))

if __name__ == '__main__': main()
