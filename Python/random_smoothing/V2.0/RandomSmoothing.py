# -*- coding: utf-8 -*-
#
# Random Smoothin Main
# Xuetao Lu
# 
# Released under the GNU General Public License

VERSION = "0.2"
import sys
try:
	import os
	import numpy as np
	import RSAlgorithms as rsas
	import RSUtilities as utls
	import progressbar
	import csv
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

# Main function    
def main():

	# file locations
	rasterfilename = 'C:/Users/xuetaolu/gom/data/Raster/resolutions/croppedResolution550.tif'
	shapefilename = 'C:/Users/xuetaolu/gom/data/Shapefiles/area18.shp'
	# Result rasters save folder
	res_raster_folder = 'C:/Users/xuetaolu/gom/data/Raster/RandomSmoothing/raster'
	# Result csv data save folder
	res_csv_folder = 'C:/Users/xuetaolu/gom/data/Raster/RandomSmoothing/data_csv'
	# Database connection
	strConn="dbname='gom' user='lxt' host='localhost' password='12345'"

	# name of species
	spcn = "epinephelus morio"

	# gmc top 40% left. gv top 80% removed
	topPercent_gmc = 50
	topPercent_gv = 60
	cutflag = 1

	# n_sms: number of random smoothing windows.
	n_sms = 5000
	R_n_cells = 10

	# save path of the cropped raster file (tif).
	fpath,fname = os.path.split(shapefilename)
	fn,fe = os.path.splitext(fname)
	# create the new folder for raster files
	# new folder path
	croppedRasterPath = res_raster_folder + '/' + fn
	utls.createFolder(croppedRasterPath)
	# create whole file path
	croprasterfile = fn+'.tif'
	targetcropraster = os.path.join(croppedRasterPath,croprasterfile)

	# Get raster information and find ids in the shape area
	rasterInfo = rsas.setRasterInfo(rasterfilename)
	IDs = rsas.findIDs(shapefilename,rasterfilename)

	smw_area_grids = rsas.initializeSmw_area_grids(IDs,rasterInfo)

	vs_data, n_v_surveys = rsas.getVSdata(shapefilename,rasterfilename,IDs,spcn,strConn)

	# smw_data: [0] for wmld <= Catch Ratio, [1] Credibiliy.
	smw_data = np.zeros((n_sms,2))
	# Calculate optimal R
	R = R_n_cells*max(rasterInfo[4],rasterInfo[5])

	with progressbar.ProgressBar(max_value=n_sms+n_sms*0.1) as bar:

		for i in xrange(n_sms):
		    ID, pos_c = rsas.drawRandomPos(IDs,rasterInfo)
		    rsas.drawSmoothingWindow(pos_c,R,ID,IDs,i,smw_data,vs_data,n_v_surveys,smw_area_grids,rasterInfo)
		    bar.update(i)

		df_RS = rsas.initializeDf_RS(IDs)

		rsas.claGsdGmcGv(smw_data,smw_area_grids,df_RS,rasterInfo,n_v_surveys)

		# Save the resulte into csv files
		strFileName = fn + '.csv'
		targetcsv = os.path.join(res_csv_folder,strFileName)
		with open(targetcsv, 'wb') as csvfile:
			np.savetxt(csvfile,df_RS, delimiter=",")

		pos_cl = utls.cropWithShapefile(shapefilename,rasterfilename,targetcropraster)
		utls.dataToRaster(df_RS,targetcropraster,rasterInfo,pos_cl)

		# cutflag = 1, cut by gmc and gv.
		fid = utls.cutWithTopercent(df_RS,cutflag,topPercent_gmc,topPercent_gv)
		df_RS_cut = df_RS[fid,:]
		utls.dataToRaster(df_RS_cut,targetcropraster,rasterInfo,pos_cl,"cut")

if __name__ == '__main__': main()