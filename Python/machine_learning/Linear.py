# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
#from multiprocessing.dummy import Pool
#import os,time,random
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
	return screenGv

def main():
	# load data
	all = pd.read_csv("allLabelledData.csv")
	# calculate the cutting values for gmc and gv
	gmc = all.loc[:,'gmc']
	gv = all.loc[:,'gv']
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
	X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.3,random_state=12345)
	scalerX = preprocessing.StandardScaler().fit(X_train)
	scalery = preprocessing.StandardScaler().fit(y_train)
	X_train = scalerX.transform(X_train)
	y_train = scalery.transform(y_train)
	X_test = scalerX.transform(X_test)
	y_test = scalery.transform(y_test)

	# linear model
	# Create linear regression object
	lmd = LinearRegression()
	lmd.fit(X_train, y_train)
	pred_test_lmd = lmd.predict(X_test)
	strlin = "linear model mean squared error of test data: " +str(mean_squared_error(y_test, pred_test_lmd))+"\n" + "linear model variance score of test data: " + str(r2_score(y_test, pred_test_lmd))+"\n"
	with open("Linear_prediction_res.txt", "w") as text_file:
		text_file.write(strlin)

	# save the results 
	results = scalery.inverse_transform(pred_test_lmd)
	#results = np.concatenate((X_test,y_test,y_test_original,pred_test_mlp,y_test_pred_mlp_original),axis=1)
	strFileName = 'Linear_Prediction_res.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,results, delimiter=",")
		
if __name__ == '__main__': main()
