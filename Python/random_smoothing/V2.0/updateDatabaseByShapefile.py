# -*- coding: utf-8 -*-

# import modules
import sys
try:
	import numpy as np
	import pandas as pd
	import RSUtilities as utls
	import RSAlgorithms as rsas
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

def main():

	rasterfilename = 'C:/Users/xuetaolu/gom/data/Raster/resolutions/croppedResolution550.tif'
	# Change file each time
	shapefilename = 'C:/Users/xuetaolu/gom/data/Shapefiles/allForML.shp'

	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"
	schema = "raster"
	tablename = "r550"
	datatable = schema+'.'+tablename
	colname = "shaperange1" # Change the colname each time
	coltype = "boolean"

	utls.addColumnToDatabase(schema,tablename,colname,coltype,strConn)
	IDs = rsas.findIDs(shapefilename,rasterfilename)
	new_values = utls.packWithTrueForUpdateDatabase(IDs)
	utls.updateDatabase(datatable,colname,new_values,strConn)

if __name__ == '__main__': main()