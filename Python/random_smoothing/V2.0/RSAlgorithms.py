# -*- coding: utf-8 -*-

# import modules
import sys
try:
	import numpy as np
	import math
	import random
	import RSUtilities as utls
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)

#===================================================================
# Initial functions
#===================================================================
def setRasterInfo(rasterfilename):
	return utls.decodeRaster(rasterfilename)

def findIDs(shapefilename,rasterfilename):
	return utls.clipRasterWithPolygon(shapefilename,rasterfilename)

# initialize df_RS
def initializeDf_RS(IDs):

	# create nparray df_RS with columns: IDs, gsd, gmc, gv
	df_RS = np.zeros((len(IDs),4))
	df_RS[:,0]=IDs

	return df_RS

# Draw the center of random smoothing window
# IDs: the IDs in the shapefile area
# Return: ID, the center ID; pos, the exact center position.
def drawRandomPos(IDs,rasterInfo):
	ncols = rasterInfo[0]
	xOrigin, yOrigin, l, h = rasterInfo[2:6]
	ID = random.sample(IDs,1)[0]
	x,y = utls.IDtoXY(ID,ncols)
	pos = np.array((random.uniform(xOrigin+x*l,xOrigin+(x+1)*l),random.uniform(yOrigin+(y+1)*h,yOrigin+y*h)))
	return ID, pos

# initialize smw_area_grids.
def initializeSmw_area_grids(IDs,rasterInfo):

	ncols = rasterInfo[0]
	XYs = []
	# create nparray smw_area_grids with IDs: IDtoXY()
	for ID in IDs:
		x,y = utls.IDtoXY(ID,ncols)
		XYs.append((x,y))

	smw_area_grids = {(x,y):[] for (x,y) in XYs}

	# using x, y to initialize dictionary

	return smw_area_grids


# initialize vs_data.
def getVSdata(shapefilename,rasterfilename,IDs,species,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):
	# filename: shapefile includes the polygon
	areaLns,areaHms,xOrigin,yOrigin,l,h = utls.decodeRaster(rasterfilename)
	shapes = utls.decodeShapefile(shapefilename)

	# [0] for total number of survey, [1] for number of red grouper
	vs_data = {(id):[0,0] for id in IDs}

	boxPoly= shapes[0].bbox
	leftlongi, toplati = boxPoly[0], boxPoly[3]
	westlongi, bottomlati = boxPoly[2], boxPoly[1]

	strSql = "SELECT sta_lat,sta_lon,sta_dpth,sta_time,maxn,scientificname FROM video.all WHERE "+str(toplati)+ ">sta_lat AND sta_lat>"+str(bottomlati)+" AND "+str(leftlongi)+"<sta_lon AND sta_lon<"+str(westlongi)
	rawdata = utls.fetchFromDatabase(strSql,strConn)
	n_surveys = len(rawdata)

	for i in xrange(n_surveys):
		# rawdata: [i][0] sta_lat, [i][1] sta_lon, [i][2] sta_dpth, [i][3] sta_time, [i][4] maxn, [i][5] scientificname
		longi, lati = utls.projConvert(rawdata[i][1], rawdata[i][0], 'epsg:4326', 'epsg:3857')
		x = int((longi-xOrigin)/l)
		y = int((lati-yOrigin)/h)
		id = utls.XYtoID(x,y,areaLns)
		if (id in IDs):
			vs_data[id][0] = vs_data[id][0] + 1
			if rawdata[i][5] == species:
				vs_data[id][1] = vs_data[id][1] + rawdata[i][4]

	return vs_data, n_surveys

#===================================================================
# Core functions
#===================================================================
# mapping catch ratio to smoothing window maximum likelihood density
# need experimential data
# cr: catch ratio
# return smoothing window maximum likelihood density
def crToWmld(cr):
	y = 20.0/6.0
	x = 0.05
	k = y/x
	wmld = k*cr
	return wmld

# mapping credibility to weight
# creds: credibility
# return weight
def credibiltiesToWeights(creds):
	return(np.square(creds)/sum(np.square(creds)))

# Function of calculating catched and total in smoothing window
# ID: the center cell location of the smoothing window
# IDs: all the cells in the shapefile area
# pos_c: center of the random window, pos_c = (x_c,y_c).
# R: radium of smoothing window, unit degree
# vs_data: Video Survey data
# return number of catched and total in the smoothing window and the IDs in the smoothing window
def countCatchedTotalInSmw(ID,IDs,pos_c,R,vs_data,rasterInfo):
	ncols, mrows = rasterInfo[0:2]
	l, h = rasterInfo[4:6]
	i,j = utls.IDtoXY(ID,ncols)
	ki = int(math.floor(float(R)/l))
	kj = int(math.floor(float(R)/(-h)))
	i_start = i-ki
	i_end = i+ki
	j_start = j-kj
	j_end = j+kj

	total,catched = 0,0
	s_w_IDS = []

	for r in xrange(i_start,(i_end+1)):
		for s in xrange(j_start,(j_end+1)):
			cx,cy = utls.XYtoCellCenter(r,s,rasterInfo)
			isIn = (np.square(cx-pos_c[0])+np.square(cy-pos_c[1]))<=np.square(R)
			# print cx,cy,pos_c
			#print isIn
			if isIn:
				id = utls.XYtoID(r,s,ncols)
				if (id in IDs):
					# labeling each grid in the smoothing window with the number of this smoothing window
					total = total + vs_data[id][0]
					catched = catched + vs_data[id][1]
					s_w_IDS.append(id)

	'''
	ind = (np.square(vs_data[:,0]-pos_c[0])+np.square(vs_data[:,1]-pos_c[1]))<=np.square(R)
	total = sum(ind)
	catched = sum(vs_data[ind,2])
	'''
	return catched,total,s_w_IDS

# Function of labeling each grid in the smoothing window with the number of this smoothing window
# ID: the center cell location of the smoothing window
# R: radium of smoothing window, unit degree
# smw_area_grids: every grid vs smoothing windows
# ith_smw: the ith smoothing window
def gridLableSmw(s_w_IDS,smw_area_grids,ith_smw,rasterInfo):
	# Calculate center of random smoothing window in which grid (i,j).
	ncols = rasterInfo[0]
	for ID in s_w_IDS:
		i,j = utls.IDtoXY(ID,ncols)
		smw_area_grids[i,j].append(ith_smw)

# Function of drawing each random window
# pos_c: center of the random window, pos_c = (x_c,y_c).
# R: radium of smoothing window, unit degree
# ID: the center cell location of the smoothing window
# IDs: all the cells in the shapefile area
# ith_smw: the ith smoothing window
# smw_data: Smoothing Windows data structure
# n_surveys: number of Video Surveys in the shapefile area, for calculating gmc
# smw_area_grids: every grid vs smoothing windows
def drawSmoothingWindow(pos_c,R,ID,IDs,ith_smw,smw_data,vs_data,n_surveys,smw_area_grids,rasterInfo):

	# calculate the wmld and Credibilty for ith smoothing window
	catch,total,s_w_IDS = countCatchedTotalInSmw(ID,IDs,pos_c,R,vs_data,rasterInfo)
	# if total is greater than 0, else set it equal to 1.
	if total==0:
		total = 1
	# calculate wmld
	cr = float(catch)/total
	smw_data[ith_smw,0] = crToWmld(cr)
	# calculate credibility
	smw_data[ith_smw,1] = float(total)/n_surveys

	# labels each grid in the smoothing window with the number of this smoothing window
	gridLableSmw(s_w_IDS,smw_area_grids,ith_smw,rasterInfo)

# Calculate gsd and gmc for each grid
# smw_data: Smoothing Windows data structure
# smw_area_grids: every grid vs smoothing windows
# and list as each element of the frame. The 0 layer of list is for gsd,the 1 layer is for gmc.
def claGsdGmcGv(smw_data,smw_area_grids,df_RS,rasterInfo,g_weight):
	ncols = rasterInfo[0]
	# Store gmc for each grid
	for i in xrange(len(df_RS)):
		x,y = utls.IDtoXY(int(df_RS[i,0]),ncols)
		# list of smoothing windows(index) covers grid (i,j)
		smws = smw_area_grids[x,y]
		if len(smws)>0:
			# calculate gsd for grid (i,j)
			# smw_data[smws,0] slicing smoothing windows data which belongs to grid (i,j). layer [0] is for wmld.
			# credibiltiesToWeights(smw_data[smws,1]): calculate the weights
			# np.multiply(): inner multiplication, w*wmld
			df_RS[i,1] = sum(np.multiply(credibiltiesToWeights(smw_data[smws,1]),smw_data[smws,0]))

			# calculate gmc for grid (i,j)
			# smw_data[smws,1] slicing smoothing windows data which belongs to grid (i,j). layer [1] is for credibility.
			df_RS[i,2] = (sum(smw_data[smws,1])/len(smws))*g_weight

			# calculate gv (grid variance)
			var = np.var(smw_data[smws,0])
			df_RS[i,3] = var
