import math
import numpy as np
from geopy import distance as gd


def mid_point(k1,k2):               # Counts middle point between 2 coordinate pairs
    if k2>=k1:
        mid=((k2-k1)*0.5)+k1
    else:
        mid=((k1-k2)*0.5)+k2
    return mid

def lat_change(lat1,lat2,lon):      # Distance if only lat would change
    coor1=(lat1,lon)
    coor2=(lat2,lon)
    lat_dis=(vincenty(coor1,coor2).m)
    return lat_dis

def lon_change(lon1,lon2,lat):                   # Distance if only lon would change
    coor1=(lat,lon1)
    coor2=(lat,lon2)
    lon_dis=(vincenty(coor1,coor2).m)
    return lon_dis


def my_distance(c1,c2):
    tan_dist=(vincenty(c1,c2).m)       # Actual distance
    #print(tan_dist)
    mid_lat=mid_point(c2[0],c1[0])
    mid_lon=mid_point(c2[1],c1[1])
    lat_dist=lat_change(c1[0],c2[0],mid_lon)
    lon_dist=lon_change(c1[1],c2[1],mid_lat)
    #print(lat_dist, lon_dist)


    if (lat_dist == 0.0) and (lon_dist == 0.0):                             # No movement
        alpha=np.nan
    elif lat_dist==0:                                                       # Only lon movement:
        if c2[1]>c1[1]:                                                     # Eastwardly
            alpha=0.0
        else:                                                               # Westwardly
            alpha=180.0
    elif lon_dist==0:                                                       # Only lat movement:
        if c2[0]>c1[0]:                                                     # Northwardly
            alpha=90.0
        else:                                                               # Southwardly
            alpha=270.0
    elif (lon_dist != 0.0) and (lat_dist != 0.0):
        if (c2[0]>c1[0]) and c2[1]>c1[1]:                                   # north east direction
            alpha=math.degrees(math.atan(lat_dist/lon_dist))
        elif (c2[0]>c1[0]):                                                 # north west direction
            alpha=180-(math.degrees(math.atan(lat_dist/lon_dist)))
        elif c2[1]>c1[1]:                                                   # south east direction
            alpha=360-(math.degrees(math.atan(lat_dist/lon_dist)))
        else:                                                               # south west direction
            alpha=180+(math.degrees(math.atan(lat_dist/lon_dist)))
    else:
        print('Something weird happened')
        exit

    return(tan_dist,alpha)


### This version was for my Batchelor thesis with distances  counted from previous lat, lon
def count_dist(lat,lon):
    dist=[]
    angle=[]
    for ind in range(len(lat)-1):       # Takes 1 coordinate pair at a time
        coor1=(lat[ind],lon[ind])
        coor2=(lat[ind+1],lon[ind+1])
        (aa,bb)=my_distance(coor1,coor2)
        dist.append(aa)
        angle.append(bb)
    #print(dist[0:5],angle[0:5])
    return(dist,angle)


## This version for finding shortest distance to a point
def shortest_dist(lats,lons,comp_lat,comp_lon):
    # Find shortest distance to a point, returns index of where the shortest distance was first found and the distance in km.
    # Input can be a lists of lats and lons. Uses the newer geopy.distance.distance instead of vincenty.

    # lats can be a list of latitudes for points
    # lons can be a list of longitude for points
    # comp_lat is latitude of compare point (only one number)
    # comp_lon is longitude of compare point (only one number)

    if len(lats) != len(lons):
        exit("Can't count distance, lat and lon inputs are not same length.")

    distance_array=[]
    coor_comp=(comp_lat,comp_lon)


    for ind in range (len(lats)):
        coor=(lats[ind],lons[ind])
        meters=gd.distance(coor,coor_comp).km
        distance_array.append(meters)


    print(distance_array)
    return np.argmin(distance_array),np.amin(distance_array)


## This version for finding shortest distance to a point
def shortest_distp(coords,comp_lat,comp_lon):
    # Find shortest distance to a point, returns index of where the shortest distance was first found and the distance in km.
    # Input can be a list. Uses the newer geopy.distance.distance instead of vincenty.

    # coords in order lat,lon
    # comp_lat is latitude of compare point (only one number)
    # comp_lon is longitude of compare point (only one number)


    distance_array=[]
    coor_comp=(comp_lat,comp_lon)


    for ind in range (len(coords)):
        meters=gd.distance(coords[ind],coor_comp).km
        distance_array.append(meters)


    print(distance_array)
    return np.argmin(distance_array),np.amin(distance_array)





def main():
    #print('Main of Count distance and direction')
    lati=[65.0,70.0,65.0,70.0,65.0,65.0,70.0,65.0,65.0,65.0]
    loni=[40.0,45.0,40.0,35.0,40.0,40.0,40.0,40.0,45.0,40.0]
    #(dd,gg)=count_dist(lati,loni)
    #print(gg)
    #print(dd)
    print(shortest_dist(lati,loni,60,40))


if __name__ == '__main__':
    main()