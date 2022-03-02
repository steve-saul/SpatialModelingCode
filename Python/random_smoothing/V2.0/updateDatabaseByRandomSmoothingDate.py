# -*- coding: utf-8 -*-

# import modules
import sys
try:
	import numpy as np
	import pandas as pd
	import RSUtilities as utls
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

def main():

	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"
	datatable = "raster.r550"

	#utls.initialRasterDatabase(filename,tablename,strConn)

	#utls.addColumnToDatabase(schema,tablename,colname1,coltype1,strConn)
	#utls.addColumnToDatabase(schema,tablename,colname2,coltype1,strConn)
	#utls.addColumnToDatabase(schema,tablename,colname3,coltype3,strConn)
	#IDs = utls.cropWithRasterDepth(filenameDepth,depthLow=-200,depthUp=-2)
	#new_values = utls.packWithTrueForUpdateDatabase(IDs)

	#utls.updateDatabase(datatable,updateColname1,new_values,strConn)


	#utls.initialDepthRugosity(datatable,filenameDepth,filenameRugosity,strConn)

	#utls.updateDatabase(datatable,updateColname1,new_values,strConn)

	#utls.initialDepthRugosity(tablename,filenameDepth,filenameRugosity,strConn)

	# update gsd gmc and gv
	for i in xrange(18):
		csvfn = 'C:/Users/xuetaolu/gom/data/Raster/RandomSmoothing/data_csv/area'+ str(i+1) +'.csv'
		re = pd.read_csv(csvfn,header=None)
		dgsd = np.asarray(re.loc[:,[0,1]])
		dgmc = np.asarray(re.loc[:,[0,2]])
		dgv = np.asarray(re.loc[:,[0,3]])
		utls.updateDatabase(datatable,"gsd",dgsd,strConn)
		utls.updateDatabase(datatable,"gmc",dgmc,strConn)
		utls.updateDatabase(datatable,"gv",dgv,strConn)


if __name__ == '__main__': main()