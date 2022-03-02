# -*- coding: utf-8 -*-

# import modules
import sys
try:
	import numpy as np
	import psycopg2
	import psycopg2.extras as p2e
	import os, gdal
	from gdalconst import *
	import pyproj
	import shapefile
	import shutil
	import struct # New
	from PIL import Image
	from shapely.geometry import Point, shape
	#from gdalconst import * 
except ImportError, err:
    print "couldn't load module. %s" % (err)
    sys.exit(2)
#==============================================================
# Other utility functions
#==============================================================

def projConvert(longi, lati, fm = 'epsg:3857', to = 'epsg:4326'):
	f = pyproj.Proj(init=fm)
	t = pyproj.Proj(init=to)
	newlongi, newlati = pyproj.transform(f, t, longi, lati)
	return newlongi, newlati

def fetchFromDatabase(strSql,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):
	flag = 0
	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		cur.execute(strSql)
		rows = cur.fetchall()
		flag = 1

	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:
		if con:
			con.close()
	if flag:
		return rows
	else:
		return None

# New
# prepare for updateDatabase
# return a tuple
def packWithTrueForUpdateDatabase(IDs):
	new_values = []
	for i in xrange(len(IDs)):
		new_values.append((IDs[i],True))
	return tuple(new_values)

# prepare for updateDatabase
# return a tuple
# values can be a list or array which must correspond to IDs
def packWithValuesForUpdateDatabase(IDs,values):
	new_values = []
	for i in xrange(len(IDs)):
		new_values.append((IDs[i],values[i]))
	return tuple(new_values)

# New
# Update multiple rows with multiple columns in a table with values from a tuple of tuples
def updateDatabase(datatable,updateColname,new_values,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):
	# update_query: see examples.
	# new_values: tuples, corresponding to the update_query.

	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		#update_query = "UPDATE "+datatable+" as t SET "+updateColname+" = c.v1 FROM (VALUES %s) AS c(id, v1) WHERE c.id = t.id"
		#p2e.execute_values (cur, update_query, new_values, template=None, page_size=100)
		for i in xrange(len(new_values)):
			update_query = "UPDATE "+datatable+" SET "+updateColname+"= "+str(new_values[i][1])+" WHERE id="+str(int(new_values[i][0]))+";"
			#print update_query
			cur.execute(update_query)
		con.commit()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:
		if con:
			con.close()

	# examples
	'''
	example 1:
	>>> cur.execute(
	... "create table test (id int primary key, v1 int, v2 int)")

	>>> execute_values(cur,
	... "INSERT INTO test (id, v1, v2) VALUES %s",
	... [(1, 2, 3), (4, 5, 6), (7, 8, 9)])

	>>> execute_values(cur,
	... """UPDATE test SET v1 = data.v1 FROM (VALUES %s) AS data (id, v1)
	... WHERE test.id = data.id""",
	... [(1, 20), (4, 50)])

	>>> cur.execute("select * from test order by id")
	>>> cur.fetchall()
	[(1, 20, 3), (4, 50, 6), (7, 8, 9)])

	example 2:
	You can add as many columns as you like:

	update test as t set
	    column_a = c.column_a,
	    column_c = c.column_c
	from (values
	    ('123', 1, '---'),
	    ('345', 2, '+++')  
	) as c(column_b, column_a, column_c) 
	where c.column_b = t.column_b;
	'''
# New
def addColumnToDatabase(schema,tablename,colname,coltype,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):

	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		strCn = "SELECT column_name FROM information_schema.columns WHERE  table_name='" + tablename +"' and column_name='"+colname+"'"
		cur.execute(strCn)
		rows = cur.fetchall()
		if len(rows)>0:
			print "The column already exist."
		else:
			strAddCol = 'ALTER TABLE '+schema+'.'+tablename+' ADD COLUMN '+colname+' '+coltype
			cur.execute(strAddCol)
			con.commit()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:
		if con:
			con.close()

#==============================================================
# Utility functions for raster data
#==============================================================

# transfer ID to xth and yth cell position (integer) in the whole raster map.
def IDtoXY(ID,ncols):
	x = ID%ncols
	y = ID/ncols
	return int(x), int(y)

# transfer xth and yth cell position (integer) in the whole raster map to ID.
def XYtoID(x,y,ncols):
	return int(y*ncols+x)
# find xth and yth cell center position (float).
def XYtoCellCenter(x,y,rasterInfo):
	xOrigin, yOrigin, l, h = rasterInfo[2:6]
	cx = xOrigin+(x+0.5)*l
	cy = yOrigin+(y+0.5)*h
	return cx,cy

# decode the raster file
def decodeRaster(filename):

	# start timing
	# startTime = time.time()
	# set directory
	# os.chdir(r'/home/lxt/GOM_Project/Qgis/Raster')
	# register all of the drivers
	gdal.AllRegister()
	# open the image
	ds = gdal.Open(filename, GA_ReadOnly)

	if ds is None:
		print 'Could not open raster file'
		sys.exit(1)

	# get image size
	areaHms = ds.RasterYSize # rows
	areaLns = ds.RasterXSize # cols
	#bands = ds.RasterCount

	# get georeference info
	transform = ds.GetGeoTransform()
	# (longi_left,lati_bottom) <=> (0,0)
	xOrigin = transform[0] # left x
	yOrigin = transform[3] # top y

	l = transform[1] # w-e pixel resolution, l
	h = transform[5] #n-s pixel resolution, h

	return areaLns,areaHms,xOrigin,yOrigin,l,h

# New
# read the Raster band data (single band) and return the data as a array whose index corresponds to the ID
def readRasterBandData(rasterfilename):
	gdal.AllRegister()
	dataset = gdal.Open(rasterfilename, gdal.GA_ReadOnly)
	areaHms = dataset.RasterYSize # rows
	areaLns = dataset.RasterXSize # cols
	rbd = np.zeros((areaHms,areaLns))
	band = dataset.GetRasterBand(1)
	for i in xrange(areaHms):
		scanline = band.ReadRaster(xoff=0, yoff=i,xsize=band.XSize, ysize=1,buf_xsize=band.XSize, buf_ysize=1,buf_type=gdal.GDT_Float32)
		rbd[i,:] = struct.unpack('f' * band.XSize, scanline)
	return rbd

def decodeShapefile(filename):
	# Reading Shapefiles
	sf = shapefile.Reader(filename)
	# Reading Geometry
	shapes = sf.shapes()
	return shapes

# Find the cells of raster data falling in the polygon
def clipRasterWithPolygon(shpfn,rastfn):
	IDs = []
	areaLns,areaHms,xOrigin,yOrigin,l,h = decodeRaster(rastfn)
	shapes = decodeShapefile(shpfn)
	boxPoly= shapes[0].bbox
	leftlongi, toplati = projConvert(boxPoly[0], boxPoly[3], 'epsg:4326', 'epsg:3857')
	westlongi, bottomlati = projConvert(boxPoly[2], boxPoly[1], 'epsg:4326', 'epsg:3857')
	xl = int((leftlongi-xOrigin)/l)
	yt = int((toplati-yOrigin)/h)
	xr = int((westlongi-xOrigin)/l)
	yb = int((bottomlati-yOrigin)/h)
	#w = shapefile.Writer(shapefile.POINTM)
	for i in xrange(xl,xr):
		for j in xrange(yt,yb):
			longi, lati = projConvert((xOrigin + i*l + 0.5*l), (yOrigin + j*h + 0.5*h), 'epsg:3857', 'epsg:4326')
			pt = (longi, lati)
			if Point(pt).within(shape(shapes[0])):
				IDs.append(XYtoID(i,j,areaLns))
				#w.point(longi,lati)                
	#w.save('/home/lxt/ipython_Scripts/shapefiles/point')
	return IDs

# Create tiff with clipped rectangle.
def cropWithShapefile(shpfn,rastfn,savePath):
	areaLns,areaHms,xOrigin,yOrigin,l,h = decodeRaster(rastfn)
	shapes = decodeShapefile(shpfn)
	boxPoly= shapes[0].bbox
	leftlongi, toplati = projConvert(boxPoly[0], boxPoly[3], 'epsg:4326', 'epsg:3857')
	westlongi, bottomlati = projConvert(boxPoly[2], boxPoly[1], 'epsg:4326', 'epsg:3857')
	xl = int((leftlongi-xOrigin)/l)
	yt = int((toplati-yOrigin)/h)
	xr = int((westlongi-xOrigin)/l)
	yb = int((bottomlati-yOrigin)/h)
	img = Image.open(rastfn)
	img2 = img.crop((xl, yt, xr, yb))
	img2.save(savePath)

	gdal.AllRegister()
	# open the image
	ds = gdal.Open(savePath, GA_Update)

	if ds is None:
		print 'Could not open raster file'
		sys.exit(1)
	ds.SetGeoTransform([leftlongi, l, 0, toplati, 0, h])
	ds=None
	# Return left top cell ID to xy
	return (xl,yt)

# New # Has problems
# crop the raster with range of depth
# return: all the cell IDs in the range
def cropWithRasterDepth(rastfn,depthLow=None,depthUp=None):
	dps = readRasterBandData(rastfn)
	ncols = dps.shape[1]
	IDs = []
	indexes = []
	if (depthLow != None) & (depthUp != None):
		indexes = (dps>=depthLow) & (dps<=depthUp)
	elif (depthLow != None) & (depthUp == None):
		indexes = (dps>=depthLow)
	elif (depthLow == None) & (depthUp != None):
		indexes = (dps<=depthUp)
	# find the location of every index == true, it's a list of tuples.
	xyIDs = zip(*np.where(indexes == True))
	for i in xrange(len(xyIDs)):
		IDs.append(XYtoID(xyIDs[i][0],xyIDs[i][1],ncols))
	return IDs

# gsdgmc: gsd is 0, gmc is 1, gv is 2.
def updateRaster(rasterfilename,df_RS,gsdgmcgv,rasterInfo,pos_clip):

    ncols = rasterInfo[0]

    gdal.AllRegister()
    # open the image
    ds = gdal.Open(rasterfilename, GA_Update)

    if ds is None:
        print 'Could not open raster file'
        sys.exit(1)
    areaHms = ds.RasterYSize # rows
    areaLns = ds.RasterXSize # cols
    if gsdgmcgv==0:
        gsdk = max(df_RS[:,1])-min(df_RS[:,1])
        if gsdk==0:
            k = 1
        else:
            k = 255/gsdk
    elif gsdgmcgv==1:
        gmck = max(df_RS[:,2])-min(df_RS[:,2])
        if gmck==0:
            k = 1
        else:
            k = 255/gmck
    else:
        gvk = max(df_RS[:,3])-min(df_RS[:,3])
        if gvk==0:
            k = 1
        else:
            k = 255/gvk

    gdata = np.zeros((areaHms,areaLns))
    data = np.zeros((areaHms,areaLns))

    for t in xrange(len(df_RS)):
        ID = int(df_RS[t,0])
        x,y = IDtoXY(ID,ncols)
        j = int(y-pos_clip[1])
        i = int(x-pos_clip[0])
        gdata[j,i]=int(df_RS[t,(gsdgmcgv+1)]*k)

    ds.GetRasterBand(1).WriteArray(data)
    ds.GetRasterBand(2).WriteArray(data)
    ds.GetRasterBand(3).WriteArray(data)
    ds.GetRasterBand(1).WriteArray(gdata)

    ds=None


# Copy the old raster file to 2 files and update the two files with new data.
# newDdata: the data using for updating the copies of original raster file.
# filename: original raster file using for updating.
def dataToRaster(df_RS,filename,rasterInfo,pos_clip,strelse=""):

    # Make two copies of original raster file.
    source = filename

    fpath,fname = os.path.split(filename)
    fn,fe = os.path.splitext(fname)

    if strelse=="":
        fnamegsd = fn+'gsd'+strelse+fe
        fnamegmc = fn+'gmc'+strelse+fe
        fnamegv = fn+'gv'+strelse+fe

        targetgsd = os.path.join(fpath,fnamegsd)
        targetgmc = os.path.join(fpath,fnamegmc)
        targetgv = os.path.join(fpath,fnamegv)

        try:
            shutil.copyfile(source, targetgsd)
            shutil.copyfile(source, targetgmc)
            shutil.copyfile(source, targetgv)
            updateRaster(targetgsd,df_RS,0,rasterInfo,pos_clip)
            updateRaster(targetgmc,df_RS,1,rasterInfo,pos_clip)
            updateRaster(targetgv,df_RS,2,rasterInfo,pos_clip)
        except IOError as e:
            print("Unable to copy file. %s" % e)
            exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)
        # Update the two copies with df_RS.

    else:
        fnamegsd = fn+'gsd'+strelse+fe
        targetgsd = os.path.join(fpath,fnamegsd)
        try:
            shutil.copyfile(source, targetgsd)
            updateRaster(targetgsd,df_RS,0,rasterInfo,pos_clip)
        except IOError as e:
            print("Unable to copy file. %s" % e)
            exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)

# New
# Create raster from the database
def createRasterFromDatabase(data,rasterFn,rasterInfo):
	# data: two columns, one is for ids, another is for the values of predictors.
	# Make two copies of original raster file.
	source = rasterFn
	areaLns,areaHms = rasterInfo[0:2]

	fpath,fname = os.path.split(rasterFn)
	fn,fe = os.path.splitext(fname)

	fnamegsd = fn+'DateFromDatabase'+fe
	
	target = os.path.join(fpath,fnamegsd)

	try:
		shutil.copyfile(source, target)
	except IOError as e:
		print("Unable to copy file. %s" % e)
		exit(1)
	except:
		print("Unexpected error:", sys.exc_info())
		exit(1)

	gdal.AllRegister()
	# open the image
	ds = gdal.Open(target, GA_Update)

	targetdata = np.zeros((areaHms,areaLns))
	zdata = np.zeros((areaHms,areaLns))

	ds.GetRasterBand(1).WriteArray(zdata)
	ds.GetRasterBand(2).WriteArray(zdata)
	ds.GetRasterBand(3).WriteArray(zdata)

	for t in xrange(len(data)):
		ID = int(data[t,0])
		x,y = IDtoXY(ID,areaLns)
		targetdata[y,x]=int(data[t,1])

	ds.GetRasterBand(1).WriteArray(targetdata)
	ds=None

# array: gmc or gvi array to calculate percentile
# df_RS: 
# cutflag: 1 for gmc, 2 for gv
# topercent: keep top percent.
def cutWithTopercent(df_RS,cutflag=1,percentile_gmc=50,percentile_gv=50):

	if cutflag==1:
		cpgmc = np.percentile(df_RS[:,2], percentile_gmc)
		gmcid =  df_RS[:,2]>cpgmc
		cpgv = np.percentile(df_RS[:,3], percentile_gv)
		gvid = df_RS[:,3]<cpgv
		fid = gmcid & gvid
	elif cutflag==2:
		cpgmc = np.percentile(df_RS[:,cutflag], percentile_gmc)
		fid =  df_RS[:,cutflag]>cpgmc
	elif cutflag==3:
		cpgv = np.percentile(df_RS[:,cutflag], percentile_gv)
		fid = df_RS[:,cutflag]<cpgv

	return fid

#============================================================================
# Utility functions for load and save raster data from/to postgresql database
#============================================================================

# Initial the database table using the raster spatial information
def initialRasterDatabase(filename,tablename,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):
	# decode raster file to get: 1.IDs, center positions (longi,lati).
	# areaLns: cols
	# areaHms: rows
	# l: w-e pixel resolution
	# h: n-s pixel resolution
	# xOrigin: left x
	# yOrigin: top y
	areaLns,areaHms,xOrigin,yOrigin,l,h = decodeRaster(filename)

	# insert all the information into database
	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		#print cur
		for i in xrange(areaLns*areaHms):
			ID = i
			nC,mR = IDtoXY(ID,areaLns)
			longi = xOrigin+ nC*l + 0.5*l
			lati = yOrigin + mR*h + 0.5*h
			cur.execute("""INSERT INTO """+ tablename +""" (id, col_number, row_number, sta_lat, sta_lon) VALUES (%s, %s, %s, %s, %s)""",(ID, nC, mR, lati, longi))
		con.commit()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:   
		if con:
			con.close()

#New
def initialDepthRugosity(tablename,filenameDepth,filenameRugosity,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):
	arrDepth = readRasterBandData(filenameDepth)
	arrRugosity = readRasterBandData(filenameRugosity)
	areaLns = arrDepth.shape[1]
	areaHms = arrDepth.shape[0]

	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		#print cur
		for i in xrange(areaLns*areaHms):
			ID = i
			nC,mR = IDtoXY(ID,areaLns)
			strUpdate = "UPDATE "+ tablename +" SET depth = " + str(arrDepth[mR,nC]) +","+ "rugosity = "+str(arrRugosity[mR,nC])+ " WHERE id = "+str(ID)
			cur.execute(strUpdate)
		con.commit()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:   
		if con:
			con.close()

#New
def updateRowByRow(tablename,colname,IDs,strConn="dbname='gisdb' user='lxt' host='localhost' password='12345'"):

	try:
		con = psycopg2.connect(strConn)
		cur = con.cursor()
		#print cur
		for i in xrange(len(IDs)):
			strUpdate = "UPDATE "+ tablename +" SET "+colname+" = true WHERE id = "+str(IDs[i])
			cur.execute(strUpdate)
		con.commit()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)

	finally:   
		if con:
			con.close()

# update to band information of the raster data into database
def rasterBandInfoToDatabase():
	pass


#============================================================================
# Other utility functions
#============================================================================
# createFolder
def createFolder(directory):
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
	except OSError:
		print ('Error: Creating directory. ' +  directory)
