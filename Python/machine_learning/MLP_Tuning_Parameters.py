# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from scipy import stats
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
	X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.3,random_state=12345)
	scalerX = preprocessing.StandardScaler().fit(X_train)
	scalery = preprocessing.StandardScaler().fit(y_train)
	X_train = scalerX.transform(X_train)
	y_train = scalery.transform(y_train)
	y_train = np.ravel(y_train)
	X_test = scalerX.transform(X_test)
	y_test = scalery.transform(y_test)
	y_test = np.ravel(y_test)

	# MLP model

	# specify parameters
	param_dist =   {"activation": ['relu'],
					"alpha": [1e-06],
					'hidden_layer_sizes': [(550,),(600,),(650,),(700,)]}
	# run GridSearchCV search
	clf = GridSearchCV(MLPRegressor(), param_dist, cv=10, n_jobs=20, pre_dispatch='2*n_jobs')
	clf.fit(X_train, y_train)
 	
	means = clf.cv_results_['mean_test_score']
	stds = clf.cv_results_['std_test_score']
	strps=""
	for mean, std, params in zip(means, stds, clf.cv_results_['params']):
		#print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
		strps = strps+str(mean)+"(+/-"+str(std * 2)+")"+" for " + str(params)+"\n"
	strText = "Best parameters set found on development set: \n"+str(clf.best_params_)+"\n"+"Grid scores on development set:\n"+strps
	with open("GridSearchCV_MLP.txt", "w") as text_file:
		text_file.write(strText)

	pred_test_mlp = clf.predict(X_test)
	strmlp = "mlp model mean squared error of test data: " + str(mean_squared_error(y_test, pred_test_mlp))+"\n"+"mlp model variance score of test data: "  + str(r2_score(y_test, pred_test_mlp))
	#strall = strsvr
	with open("MLP_prediction_res.txt", "w") as text_file:
		text_file.write(strmlp)

	# save the results 
	y_test_original = scalery.inverse_transform(y_test)
	y_test_pred_mlp_original = scalery.inverse_transform(pred_test_mlp)
	results = y_test_pred_mlp_original
	#results = np.concatenate((X_test,y_test,y_test_original,pred_test_mlp,y_test_pred_mlp_original),axis=1)
	strFileName = 'MLP_Prediction_res.csv'
	with open(strFileName, 'wb') as csvfile:
		np.savetxt(csvfile,results, delimiter=",")

if __name__ == '__main__': main()