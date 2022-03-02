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

	# file locations
	filename = 'C:/Users/xuetaolu/gom/data/Raster/resolutions/croppedResolution550.tif'
	filenameDepth = 'C:/Users/xuetaolu/gom/data/Raster/predictors/GOM_DEM_3Seconds_res550.tif'
	filenameRugosity = 'C:/Users/xuetaolu/gom/data/Raster/predictors/rugosity_res550.tif'
	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"
	schema = "raster"
	tablename = "r550"
	datatable = schema+'.'+tablename

	### Initial the original database from zero
	#utls.initialRasterDatabase(filename,datatable,strConn)

	colname_depth = "depth"
	colname_rugosity = "rugosity"
	coltype_double = "double precision"

	### Create the columns
	#utls.addColumnToDatabase(schema,tablename,colname_depth,coltype_double,strConn)
	#utls.addColumnToDatabase(schema,tablename,colname_rugosity,coltype_double,strConn)
	### Initial the data base with raster data
	#utls.initialDepthRugosity(datatable,filenameDepth,filenameRugosity,strConn)

if __name__ == '__main__': main()