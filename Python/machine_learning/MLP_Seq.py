# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
import pickle
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
from sklearn.model_selection import KFold

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

	Y = scalery.transform(y)
	Y = np.ravel(Y)
	X = scalerX.transform(x)

	# specify parameters
	param_dist =   {"activation": ['relu'],
					"alpha": [1e-06],
					'hidden_layer_sizes': [(20,),(30,),(650,),(700,),(800,)]}

	kf = KFold(n_splits=5,shuffle = True,random_state=12345)
	listIds = []
	for train_index, test_index in kf.split(X):
		listIds.append((train_index,test_index))

	clf = GridSearchCV(MLPRegressor(), param_dist, cv=listIds, n_jobs=10, pre_dispatch='2*n_jobs')
	clf.fit(X, Y)
	file_MLP= 'MLP_Seq4.pkl'
	pickle.dump(clf, open(file_MLP, 'wb'))

if __name__ == '__main__': main()
