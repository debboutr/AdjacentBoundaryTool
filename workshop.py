# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 13:31:13 2017

@author: Rdebbout
"""

import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin
from datetime import datetime as dt
from shapely.geometry import MultiPoint, polygon, mapping

def findIntersects(geoDF, col='COMID'):
    geoDF.columns = geoDF.columns[:-1].str.upper().tolist() + [geoDF.columns[-1]]
    copy = geoDF.copy()
    intrsct = sjoin(geoDF,copy)[[col+'_left',col+'_right']].reset_index(drop=True)
    intrsct = intrsct.ix[intrsct[col+'_left'] != intrsct[col+'_right']]
    return intrsct.apply(sorted, axis=1).drop_duplicates()

def makeArray(ser): # there is opportunity here to make this type of function work inside of geopandas, not shapely
    d = mapping(ser.geometry)
    if d['type'] == 'Polygon':
        xys = [i[:2] for u in d['coordinates'] for i in u]
    if d['type'] == 'MultiPolygon':        
        xys = [i[:2] for u in d['coordinates'] for p in u for i in p]
    arr = np.array(xys)
    return np.around(arr,decimals=10)
    
def compareGeoms(geoDF):
    iface = "/".join(geoDF.FTYPE.sort_values().tolist())
    one, two = geoDF.index
    a = makeArray(geoDF.ix[one])
    b = makeArray(geoDF.ix[two])
    nrows, ncols = a.shape
    dtype = {'names':['f{}'.format(i) for i in range(ncols)],
                    'formats':ncols * [a.dtype]}
    c = np.intersect1d(a.view(dtype), b.view(dtype))
    c = c.view(a.dtype).reshape(-1, ncols)
    if len(c) == 0: # there are no intersecting points, look for line intersects
        print one
        print two
        a = geoDF.ix[one].geometry.exterior
        b = geoDF.ix[two].geometry.exterior
        c = np.array(a.intersection(b))        
    if len(c) == 0: # interiors cross
        a = geoDF.ix[one].geometry
        b = geoDF.ix[two].geometry
        if a.area > b.area:
            for geom in a.interiors:
                if len(b.exterior.intersection(geom)) > 0:
                    c = np.array(b.exterior.intersection(geom))            
        else:
            for geom in b.interiors:
                if len(a.exterior.intersection(geom)) > 0:
                    c = np.array(a.exterior.intersection(geom))
    if len(c) == 0: # overlapping poly completely inside the other
        a = geoDF.ix[one].geometry
        b = geoDF.ix[two].geometry
        if a.area > b.area:
            c = np.array(b.exterior.coords)[:,:2]
        else:
            c = np.array(a.exterior.coords)[:,:2]            
    pts = gpd.GeoSeries(MultiPoint(map(tuple,c)))
    return gpd.GeoDataFrame({'comid1':[one],'comid2':[two], 'iface':[iface], 
                             '#points':[len(c)]},geometry=pts)   

###############################################################################
if __name__ == '__main__':
      
    NHD_dir = 'D:/NHDPlusV21'
    inputs = np.load('%s/StreamCat_npy/zoneInputs.npy' % NHD_dir).item()
    tot = dt.now()
    final =  gpd.GeoDataFrame()  
    for zone in inputs:
        print zone
        start = dt.now()
        hr = inputs[zone]
        wbs = gpd.read_file(r'%s\NHDPlus%s\NHDPlus%s\NHDSnapshot\Hydrography\NHDWaterbody.shp' % (NHD_dir, hr, zone))
        sr = wbs.crs
        wbs = wbs.ix[wbs.FTYPE.isin(['LakePond','Reservoir'])]
        reduced = findIntersects(wbs)
        keep = gpd.GeoDataFrame()
        for idx, match in reduced.iterrows():
            gdf = compareGeoms(wbs.ix[wbs.COMID.isin(match)].set_index('COMID'))
            keep = keep.append(gdf, ignore_index=True)
        print dt.now()-start
        keep.crs = sr
        keep['VPU'] = zone
        final = final.append(keep, ignore_index=True)
    final.to_file(r'D:\Projects\temp\LakeBoundaryMatch\TOTAL2.shp')
    print dt.now() - tot 




###############################################################################

#tits = mapping(ser.geometry)
## THIS WORKS! for exteriors && interiors!!!!
#len([it[:2] for tit in tits['coordinates'] for it in tit])
## This works for MultiPolgons!!!!
#len([it[:2] for tit in tits['coordinates'] for pop in tit for it in pop])
#
#
#
#for idx, match in reduced.iterrows():
#    for uid in match:
#        chk = wbs.ix[wbs.COMID.isin([uid])].set_index('COMID')
#        if not type(chk.iloc[0].geometry) == type(polygon.Polygon()):
#            print uid
#geoDF = wbs.ix[wbs.COMID.isin([166997583,166997626])].set_index('COMID')
#one = geoDF.index
#ser = geoDF.ix[one]
#type(ser.geometry.iloc[0]) == type(polygon.Polygon())
#tits = mapping(ser.geometry)
#
## different approach for MultiPolygon!!
#tits.keys()
#tits['type']
#tits['bbox']
#feats = tits['features']
#len(tits)
#len(feats)
#type(feats[0])
#tits[0]
#
#tits['features']['geometry']
#
#tits['geometry']
#feats[0].keys()
#feats[0]['type']
#feats[0]['id']
#feats[0]['bbox']
#feats[0]['properties']
#feats[0]['geometry'].keys()
#feats[0]['geometry']['type']
#feats[0]['geometry']['coordinates']
#len([it[:2] for tit in feats[0]['geometry']['coordinates'] for pop in tit for it in pop])
#
## maybe just this
#len([it[:2] for tit in tits['coordinates'] for pop in tit for it in pop])
#
#
#def compareGeoms2(geoDF):
#    one, two = geoDF.index
#    a = makeArray(geoDF.ix[one])
#    b = makeArray(geoDF.ix[two])
#    print 'length A orig: %s' % str(len(a))
#    print 'length B orig: %s' % str(len(b))
#    a = makeArray2(geoDF.ix[one])
#    b = makeArray2(geoDF.ix[two])
#    print 'length A new: %s' % str(len(a))
#    print 'length B new: %s' % str(len(b))
#    
#for idx, match in reduced.iterrows():    
#    compareGeoms2(wbs.ix[wbs.COMID.isin(match)].set_index('COMID'))

###############################################################################
#count = 0
#for idx, x in final.iterrows():
#    #print type(x.geometry)
##    if not type(x.geometry[0]) == type(MultiPoint()):
##        print idx
#    if len(x.geometry) == 0:
#        print idx
#        count += 1

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
#for idx, rec in wbs.iterrows():
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
##########################################################################
# b4 move to multiPoint()
#def compareGeoms(geoDF):
#    one = geoDF.index[0]
#    two = geoDF.index[1]
#    a = makeArray(geoDF.ix[one])
#    b = makeArray(geoDF.ix[two])
#    nrows, ncols = a.shape
#    dtype={'names':['f{}'.format(i) for i in range(ncols)],
#                    'formats':ncols * [a.dtype]}
#    d = np.intersect1d(a.view(dtype), b.view(dtype))
#    d = d.view(a.dtype).reshape(-1, ncols)
#    lt = [] 
#    for x in d:
#        g = zip(*np.where(b == x))
#        for t in g:
#            if t[1] == 1:
#                lt.append(t[0])       
#    #lt.sort()
#    c = b[lt]
#    if len(c) == 1:
#        pt = gpd.GeoSeries(MultiPoint(map(tuple,c)))
#        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=pt)
#    if len(c) > 1:
#        line = gpd.GeoSeries(MultiPoint(list(map(tuple,c))))
#        return gpd.GeoDataFrame({'idx1':[one],'idx2':[two]},geometry=line)
#
#hache = zip(*np.where(b == now))
#for t in hache:
#    if t[1] == 1:
#        print t[0]
#hache = zip(*np.where(b == now1))
