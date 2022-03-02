# -*- coding: utf-8 -*-

# import modules
import numpy as np
import pandas as pd
import os
import sys
import csv
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

def main():
	# open a file, where you stored the pickled data
	file = open("RF_Seq.pkl", "rb")

	# dump information to that file
	RF_Seq = pickle.load(file)

	# close the file
	file.close()

	with open('RF_Seq.txt', 'w') as f:
		print >> f, RF_Seq.cv_results_  # Python 2.x

if __name__ == '__main__': main()
