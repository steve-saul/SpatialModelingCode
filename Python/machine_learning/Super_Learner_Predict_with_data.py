# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import csv
import pickle

from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import Ridge
from scipy.stats import uniform as sp_rand
from sklearn.model_selection import RandomizedSearchCV


def main():
	# load data
	SLData = pd.read_csv("SLData.csv")
	y_train = pd.read_csv("SLDataY.csv")
	#=============================================================================================
	# Construct Super Learner (Ridge Regression)
	#=============================================================================================
	# Randomized Search for Algorithm Tuning
	# prepare a uniform distribution to sample for the alpha parameter
	param_grid = {'alpha': sp_rand()}
	# create and fit a ridge regression model, testing random alpha values
	Super_Model = Ridge()
	rsearch = RandomizedSearchCV(estimator=Super_Model, param_distributions=param_grid, n_iter=100, cv=10, n_jobs=40, pre_dispatch='2*n_jobs')
	rsearch.fit(SLData, y_train)
	#Super_Learner = rsearch.best_estimator_
	filename_super_learner = 'Super_learner.pkl'
	pickle.dump(rsearch, open(filename_super_learner, 'wb'))

	#super_test = Super_Learner_Train.predict(p_test)
	#test_all = np.concatenate((p_test,super_test.T,y_test),axis=1)

if __name__ == '__main__': main()
