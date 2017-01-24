# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 13:31:13 2017

@author: Rdebbout
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
from datetime import datetime as dt
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


def findIntersects(geoDF):
    one = geoDF.copy()
    two = geoDF.copy()
    on = sjoin(one,two)[['COMID_left','COMID_right']].reset_index()
    on = on.ix[on.COMID_left != on.COMID_right]
    cons = []
    for i in on.index:
        r = on.ix[i]
        t = [r.COMID_left, r.COMID_right]
        f = [r.COMID_right, r.COMID_left]
        if not t in cons and not f in cons:
            cons.append(t)
    return cons

def addInteriors(ser, arr):
    poly = []
    for pol in ser.geometry.interiors:
        poly.append(pol)
    arr = np.empty([0,2])
    for bnds in range(len(poly)):
        arr = np.concatenate([arr,np.array(poly[bnds].coords)[:,:2]])
    return arr    
    
def makeArray(ser):
    if type(ser.geometry) == type(Polygon()):
        arr = np.array(ser.geometry.exterior.coords)[:,:2]
        if len(ser.geometry.interiors) > 0:
            arr = np.concatenate([arr,addInteriors(ser,arr)])
    else:
        poly = []
        for pol in ser.geometry:
            poly.append(pol)
        arr = np.empty([0,2])
        for bnds in range(len(poly)):
            arr = np.concatenate([arr,np.array(poly[bnds].exterior.coords)[:,:2]])
    return np.around(arr,decimals=10)
    
def compareGeoms(geoDF):
    one = geoDF.index[0]
    two = geoDF.index[1]
    a = makeArray(geoDF.ix[one])
    b = makeArray(geoDF.ix[two])
    nrows, ncols = a.shape
    dtype={'names':['f{}'.format(i) for i in range(ncols)],
                    'formats':ncols * [a.dtype]}
    c = np.intersect1d(a.view(dtype), b.view(dtype))
    c = c.view(a.dtype).reshape(-1, ncols)
    if len(c) == 1:
        pt = gpd.GeoSeries(Point(map(tuple,c)))
        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=pt)
    if len(c) > 1:
        line = gpd.GeoSeries(LineString(list(map(tuple,c))))
        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=line)
lt = [] 
for x in c:
  lt.append(zip(*np.where(a == x))[0][0])
lt.sort()
a[lt[0]:lt[-1]+1]




def compareGeoms(geoDF):
    one = geoDF.index[0]
    two = geoDF.index[1]
    a = makeArray(geoDF.ix[one])
    b = makeArray(geoDF.ix[two])
    nrows, ncols = a.shape
    dtype={'names':['f{}'.format(i) for i in range(ncols)],
                    'formats':ncols * [a.dtype]}
    d = np.intersect1d(a.view(dtype), b.view(dtype))
    d = d.view(a.dtype).reshape(-1, ncols)
    lt = [] 
    for x in d:
        g = zip(*np.where(b == x))
        for t in g:
            if t[1] == 1:
                lt.append(t[0])       
    #lt.sort()
    c = b[lt]
    if len(c) == 1:
        pt = gpd.GeoSeries(Point(map(tuple,c)))
        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=pt)
    if len(c) > 1:
        line = gpd.GeoSeries(LineString(list(map(tuple,c))))
        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=line)

hache = zip(*np.where(b == now))
for t in hache:
    if t[1] == 1:
        print t[0]
hache = zip(*np.where(b == now1))

np.where(b == x).all()
zip(*np.where(b[:][0] == x[0] and b[:][1] == x[1]).all())[0][0]))a[np.isclose(a,b)]
9041-23
add = np.zeros((len(a)-len(b),2))
b = np.concatenate([add,b])


for x in d:
    print zip(*np.where(arr == x))[0][0]
    print zip(*np.where(arr2 == x))[0][0]    

       
NHD_dir = 'D:/NHDPlusV21'
inputs = np.load('%s/StreamCat_npy/zoneInputs.npy' % NHD_dir).item()
tot = dt.now()        
for zone in inputs:
    zone = '06'
    print zone
    hr = inputs[zone]
    six = gpd.read_file(r'%s\NHDPlus%s\NHDPlus%s\NHDSnapshot\Hydrography\NHDWaterbody.shp' % (NHD_dir, hr, zone))
    sr = six.crs
    six = six.ix[six.FTYPE.isin(['LakePond','Reservoir'])]
    reduced = findIntersects(six)
    keep_line = gpd.GeoDataFrame()
    keep_point = gpd.GeoDataFrame()
    start = dt.now()    
    for match in reduced:
        gdf = compareGeoms(six.ix[six.COMID.isin(match)].set_index('COMID'))
        if type(gdf.ix[gdf.index[0]].geometry) == type(Point()):
            keep_point = keep_point.append(gdf, ignore_index=True)
        if type(gdf.ix[gdf.index[0]].geometry) == type(LineString()):
            keep_line = keep_line.append(gdf, ignore_index=True)
    print dt.now()-start
    keep_line.crs = sr
    keep_point.crs = sr
    keep_line.to_file(r'D:\Projects\temp\LakeBoundaryMatch\LinesTestes6_%s.shp' % zone)
    keep_point.to_file(r'D:\Projects\temp\LakeBoundaryMatch\PointsTestes6_%s.shp' % zone)
print dt.now() - tot   
###############################################################################
# NOTES
#  sometimes swamp/marsh overlaps completely with lakePond - same poly/diff COMID
#  
###############################################################################
#g = gpd.read_file(r'D:\Projects\temp\LakeBoundaryMatch\Guntersville_06.shp')
#for coord in xys.values:
#    print coord
#    
#arr = np.array(rec.geometry.exterior.coords)
#arr[:,:2]
#
#s = pd.Series({'a':1, 'b':2, 'c':3})
#s.values # a numpy array
#
#
#x = np.arange(9.).reshape(3, 3)
#goodvalues = [3, 4, 7]
#ix = np.in1d(x.ravel(), goodvalues).reshape(x.shape)
#
#one = xys[0].flatten()
#two = xys[1].flatten()
#len(one)
#len(two)
#mask = np.in1d(one,two)
#one[mask].reshape((len(one[mask])/2,2))
#two[mask]
## buffer each poly first, then compare if there are matching points
#for h in g.index:
#    
#type(g.ix[g.index == 0])
#type(g.ix[g.index != 0])
#r = g.ix[g.index == 0]
#d = g.drop(0)
#
#def compareGeoms(df1, df2):
#    num1 = r.index[0]
#    arr1 = np.array(r.geometry.geometry.exterior.exterior.coords)[:,:2]
#    type(r)
#keep = gpd.GeoDataFrame()   
#for i in xys.index:
#    a = xys[i].flatten()
#    for j in xys.index.drop(i):
#        b = xys[j].flatten()
#        comp = np.in1d(a,b)
#        if len(a[comp]) > 0:
#            cds = a[comp].reshape((len(a[comp])/2,2))
#            line = gpd.GeoSeries(LineString(list(map(tuple,cds))))
#            keep = keep.append(gpd.GeoDataFrame({'idx1':[i],'idx2':[j]},geometry=line))
#
#jx = []
#for row in b:
#    #print row
#    if len(np.where((a == row).all(axis=1))[0]) > 0:
#        jx.append(np.where((a == row).all(axis=1))[0][0])
#[np.where((a == row).all(axis=1))[0][0] for row in b]
#a[3990]
#a[jx]
#a[np.in1d(a.view(dtype='f,f').reshape(a.shape[0]*a.shape[1]),b.view(dtype='f,f').reshape(b.shape[0]))]
#cds = np.vstack((a,b))
#
#np.array(np.all((a[:,None,:]==b[None,:,:]),axis=-1).nonzero()).T.tolist()
#a[3990,0]
#a[3990,1]
#[[3990L, 0L], [3990L, 9L], [3991L, 8L], [3992L, 7L]]
#a[3991, 0]
###############################################################################
#def compareGeoms(xys, keep):   
#    i = xys.index[0]
#    a = xys[i].flatten()
#    for j in xys.index.drop(i):
#        b = xys[j].flatten()
#        comp = np.in1d(a,b)
#        if len(a[comp]) > 0:
#            cds = a[comp].reshape((len(a[comp])/2,2))
#            line = gpd.GeoSeries(LineString(list(map(tuple,cds))))
#            gdf = gpd.GeoDataFrame({'idx1':[i],'idx2':[j]},geometry=line)
#            keep = keep.append(gdf)
#    if len(xys) > 1:
#        return compareGeoms(xys.drop(i), keep)
#    else:
#        return keep
#
#g = gpd.read_file(r'D:\Projects\temp\LakeBoundaryMatch\Guntersville_06.shp').set_index('COMID')
#xys = pd.Series()
#for idx, rec in g.iterrows():
#    xys = xys.append(pd.Series({idx :np.array(rec.geometry.exterior.coords)[:,:2]}))
#    
#
#keep = gpd.GeoDataFrame()    
#hold2 = compareGeoms(xys,keep)
#hold2.crs = g.crs
#hold2.to_file(r'D:\Projects\temp\LakeBoundaryMatch\Guntersville_06.shp')
##############################################################################
#xys = pd.Series()
#for idx, rec in six.iterrows():
#    xys = xys.append(pd.Series({idx :np.array(rec.geometry.exterior.coords)[:,:2]}))
#    
#
#keep = gpd.GeoDataFrame()    
#hold2 = compareGeoms(xys,keep)
#hold2.crs = g.crs
#hold2.to_file(r'D:\Projects\temp\LakeBoundaryMatch\LinesAll_06.shp')
#
#
#
#new = list({tuple(row) for row in cds})
#np.unique(new)
#
#
#count = 0
#for x in xys.index:
#    if len(xys[x]) > count:
#        count = len(xys[x])
#        hold = x
#touching = gpd.GeoDataFrame()        
#def findTouching(geoDF, tch):            
#    for idx, rec in geoDF.iterrows():
#        #break
#        h = geoDF.drop(idx).copy()
#        ct = 0
#        for index, rec2 in h.iterrows():
#            #break
#            if rec.geometry.touches(rec2.geometry) == True:
#                if ct == 0:
#                    tch = tch.append(geoDF.ix[[idx,index]])
#                    ct += 1
#                if ct > 0:
#                    tch = tch.append(geoDF.ix[[index]])
#    if len(geoDF) > 1:
#        return findTouching(geoDF.drop(idx).copy(), tch)
#    else:
#        return tch
#
#keepers = findTouching(g, touching)
