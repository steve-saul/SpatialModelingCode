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

	res_csv_folder = 'C:/Users/xuetaolu/gom/data/Raster/RandomSmoothing/data_csv/'
	filename = 'allLabelledData.csv'
	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"
	schema = "raster"
	tablename = "r550"
	datatable = schema+'.'+tablename

	strSql = "SELECT * FROM raster.r550 WHERE gsd is not null"
	rawdata = utls.fetchFromDatabase(strSql,strConn)
	df = pd.DataFrame(rawdata,columns=['id','ncol','nrow','c_lat','c_long','gsd','gmc','gv','depth','rugosity','depthrange','shaperange'])
	df.to_csv(res_csv_folder+filename, sep=',')

if __name__ == '__main__': main()