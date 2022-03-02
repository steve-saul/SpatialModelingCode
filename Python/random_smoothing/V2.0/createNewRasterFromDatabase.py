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

	rasterfilename = 'C:/Users/xuetaolu/gom/data/Raster/resolutions/croppedResolution550.tif'

	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"
	schema = "raster"
	tablename = "r550"
	datatable = schema+'.'+tablename


	strSql = "SELECT id FROM raster.r550 WHERE depthrange1=true AND shaperange1=true"
	rawdata = utls.fetchFromDatabase(strSql,strConn)

	dt = np.zeros((len(rawdata),2))
	for i in xrange(len(rawdata)):
		dt[i,0] = rawdata[i][0]
		dt[i,1] = 100
	rasterInfo = utls.decodeRaster(rasterfilename)
	utls.createRasterFromDatabase(dt,rasterfilename,rasterInfo)

if __name__ == '__main__': main()