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

	# SVR model
	# Set the parameters by cross-validation
	tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0.5],'C': [3000,4000]}]
	clf = GridSearchCV(SVR(), tuned_parameters, verbose=100, cv=10,n_jobs=58,pre_dispatch=116)
	clf.fit(X_train, y_train)
 	
	means = clf.cv_results_['mean_test_score']
	stds = clf.cv_results_['std_test_score']
	strps=""
	for mean, std, params in zip(means, stds, clf.cv_results_['params']):
		#print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
		strps = strps+str(mean)+"(+/-"+str(std * 2)+")"+" for " + str(params)+"\n"
	strText = "Best parameters set found on development set: \n"+str(clf.best_params_)+"\n"+"Grid scores on development set:\n"+strps
	with open("GridSearchCV_SVR.txt", "w") as text_file:
		text_file.write(strText)

	pred_test_svr_rbf = clf.predict(X_test)
	strsvr = "svr rbf model mean squared error of test data: " + str(mean_squared_error(y_test, pred_test_svr_rbf))+"\n"+"svr rbf model variance score of test data: "  + str(r2_score(y_test, pred_test_svr_rbf))
	with open("SVR_prediction_res.txt", "w") as text_file:
		text_file.write(strsvr)

	# save the results 
	#y_test_original = scalery.inverse_transform(y_test)
	results = scalery.inverse_transform(pred_test_svr_rbf)
	#results = y_test_pred_svr_original
	#results = np.concatenate((X_test,y_test,y_test_original,pred_test_mlp,y_test_pred_mlp_original),axis=1)
	strFileName = 'SVR_Prediction_res.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,results, delimiter=",")


if __name__ == '__main__': main()
