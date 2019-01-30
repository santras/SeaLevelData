#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import numpy.ma as ma       # Masked arrays
import os, glob
from netCDF4 import Dataset
from geopy import distance as gd


# The purpose of this code is to retrieve Copernicus CMEMS Model Data (NETCDF files) from wanted points of interest and store them  as txt files.



GLstyle= False                             # True if want to do gl-format for output
headerfilename=('header_cmems.txt')       # Path to  header titles as a txt file
headerfilename2=('header_gl.txt')         # Path to GL (style header file)
interest_points=("/home/sanna/PycharmProjects/ModelData/NorthernBaltic_Points_of_Interest.txt")
path="/home/sanna/PycharmProjects/Tests"                        # Path for the original data file folder, script goes throuh all .nc files in the folder
output_path= path +"../ModelData/Locations//"      # Outputpath
time_difference = 60                      # Expected time difference between measurements, should be 6o min.
testlat=60.0
testlon=26.6

def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        file.close()
        ok=True
    except: # Returns empty data variable and False if not successfull
        print("File {} couldn't be opened in open_txtfile/Function 1.".format(file_name))
        ok=False
        data=[]
        return data,ok

    return data, ok


def get_headers(headfile):
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    (headerfile,opened)=open_txtfile(headfile)
    if not opened:
        print('Failed to generate headers, need a headerfile for model in get_headers/Function2.')
        exit('Ending program')
    Headers = {}
    order=[]
    for line in headerfile:                 # Reads the lines of the file into a dictionary
        if not (line.strip() == "" or line.strip()[0] == "#"):
            if ":" in line:                     # Some unchanging variables are saved in into the dictionary from the headerfile
                splitline = line.split(":")
                key = splitline[0].strip()
                value = splitline[1].strip()
            else:
                key = line.strip()
                value = ""
            Headers[key] = value
            order.append(key)
    return Headers,order


def roundTime(dt=None, roundTo=60):
    # From  Stack Overflow aswer by Le Droid (copied 23.1.2019)
    # https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python/10854034#10854034

    """Round a datetime object to any time lapse in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None :
        dt = datetime.datetime.now()

    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def grid_find(p_lat,p_lon,lat,lon,delta_lat,delta_lon):

    # Forming the grid boxes

    gp_latmax = []  # Grid point lat max
    gp_latmin = []  # Grid point lat min
    gp_lonmax = []  # Grid point lon max
    gp_lonmin = []  # Grid point lon min

    for ii in range(len(lat)):
        gp_latmax.append(lat[ii]+0.5*delta_lat)
        gp_latmin.append(lat[ii]-0.5*delta_lat)

    for jj in range(len(lon)):
        gp_lonmax.append(lon[jj]+0.5*delta_lon)
        gp_lonmin.append(lon[jj]-0.5*delta_lon)

    # search
    no_match = False

    lat_matchindex = find_match(p_lat,gp_latmin,gp_latmax)
    if lat_matchindex == -1:
        no_match = True

    lon_matchindex = find_match(p_lon,gp_lonmin,gp_lonmax)
    if lon_matchindex == -1:
        no_match = True


    return lat_matchindex,lon_matchindex,no_match



def find_match(point_coor,mins,maxes):
    # Finds match between min-max  and gives index of match, if none found returns -1

    found_ind = -1

    for ind in range(len(mins)):
        if ( ( point_coor <= maxes[ind] ) and ( point_coor >= mins[ind] ) ) :
            found_ind = ind

    return found_ind


def get_grid(file,p_names,p_lat,p_lon):     # p_lat, p_lon = interest point coordinates

    nc_data = Dataset(file, 'r')
    #print_ncattr(nc_data)                          ######## Here for printing nc file attributes and variables
    lat = ma.masked_array(nc_data.variables['latitude'][:])
    #print(lat.shape)
    #print(min(lat),lat[0],lat[-1],max(lat))
    lon = ma.masked_array(nc_data.variables['longitude'][:])
    sealev = ma.masked_array(nc_data.variables['sla'][:])               ## In mask true=masked

    sealev.mask=ma.nomask  ## no mask makes masked nans
    lat.mask=ma.nomask
    lon.mask=ma.nomask

    #print(nc_data.variables["sla"])
    #print(lon.shape)
    #print(min(lon), lon[0], lon[-1], max(lon))

    # Latitudes are in order small>big from 48.4917 to 65.85825  ###lat shape 523
    # Longitudes are in order small>big from 9.047926 to 30.124683  #### lon shape 381
    # Lat, lon are probably middle points of grid since gridding is done
    # lat width of grid square 0.033269252873563214 (half  0.016634626436781607)
    # lon width of grid square 0.055465150000000005 (half  0.027732575000000002)
    delta_lat= lat[1]-lat[0]             #0.03333     #lat[1]-lat[0]                                             # difference between 2 measurements lat
    delta_lon=  lon[1]-lon[0]                        #0.05556            #lon[1]-lon[0]                                             # difference between 2 measurements lon
    print("GRID: delta lat,delta lon:",delta_lat,delta_lon)
    print("GRID: minlat,maxlat, minlon, maxlon:",np.min(lat),np.max(lat),np.min(lon),np.max(lon))
    print("GRID: delta lat in km, delta lon in km:",round(gd.distance((lat[0],lon[0]),(lat[1],lon[0])).km,2)," km",round(gd.distance((lat[0],lon[0]),(lat[0],lon[1])).km,2)," km")

    match_indexes = []

    # For each point of interest
    for index in range(len(p_names)):
        (lat_ind,lon_ind,no_match)=grid_find(p_lat[index],p_lon[index],lat,lon,delta_lat,delta_lon)
        # Test if land if match was found
        if not no_match:    # if found in area
            if np.isnan(sealev[0][lat_ind][lon_ind]):   # if point on lands
                # Need to find another point that's not land
                (match,dist) = find_nearest_sea(p_names[index],p_lat[index],p_lon[index],lat,lon,delta_lat,delta_lon,sealev,lat_ind,lon_ind)
                #print(match)
                lat_ind = match[0]
                lon_ind = match[1]
               # print(lat_ind)
            else:       # point on sea, all good
                point = (p_lat[index],p_lon[index])
                g_lat=lat[lat_ind]
                g_lon=lon[lon_ind]
                g_point = (g_lat,g_lon)
                dist = (gd.distance(point, g_point).km )                          # geopy.distance.distance
                #print(p_names[index],round(dist,2)," km")

            match_indexes.append([p_names[index], lat_ind, lon_ind,dist])


        else:   # if outside model area
            print("No match was found for ",p_names[index])

    #print(match_indexes)

    return match_indexes


def check_land(point,lat,lon,sealev,lat_ind,lon_ind,lat_indchange = 0, lon_indchange = 0):    # here sealev.shape=(523,381) / only t=0
    # Check that the tested grid square is not out of area and not land, the counts the distance to it
    dist_to_point=np.nan
    direction_ok =True

    #print(lat_ind,lon_ind,lat_indchange,lon_indchange)

    if lat_ind + lat_indchange < 0 or lat_ind + lat_indchange > len(lat)-1 :      # The edges of the grid/lat
        direction_ok = False

    elif lon_ind + lon_indchange < 0 or lon_ind + lon_indchange > len(lon)-1:      # The edges of the grid/lon

        direction_ok = False

    elif not np.isnan(sealev[lat_ind + lat_indchange][lon_ind + lon_indchange]):  # sealev not nan = water grid square
        g_point = (lat[lat_ind + lat_indchange], lon[lon_ind + lon_indchange])
        dist_to_point = gd.distance(point, g_point).km                            # using geopy.distance.distance

    return dist_to_point, direction_ok              # dist_to_point = nan if bad square, direction= False if out of area


def check_match(point,lat,lon,sealev,lat_ind,lon_ind):
    # checking the surrounding grid-squares (9)
    found = False
    distances_topoint = []
    match_indexes= []  # To record indexes when the square is valid
    direction_map = []

    for jj_lat in range(-1,2):      # Squares from lat -1 to lat +1
        for ii_lon in range(-1,2) :  # Squares from lat -1 to lat +1
            (dist_to_point,direction)=check_land(point, lat, lon, sealev[0][:][:], lat_ind, lon_ind, jj_lat,ii_lon) # checks the point
            if not np.isnan(dist_to_point):             # if valid square
                distances_topoint.append(dist_to_point)
                match_indexes.append([lat_ind + jj_lat,lon_ind + ii_lon])
            elif not (jj_lat == 0 and ii_lon == 0) :  # Not in the middle
                direction_map.append([jj_lat,ii_lon,direction])

    if distances_topoint !=[] :
        found = True
        #print(np.argmin(distances_topoint))
    else:
        return found, [],[],direction_map

    # return boolean true if found, the indexes of closest grid square to point and the distance between them in km
    return found, match_indexes[np.argmin(distances_topoint)],distances_topoint[np.argmin(distances_topoint)],[]


def find_nearest_sea(p_name,p_lat,p_lon,lat,lon,delta_lat,delta_lon,sealev,lat_ind,lon_ind):
# Trying to find matches from surrounding grid boxes

    point = (p_lat,p_lon)
    (found_ok,match_index,dist,direction_map) = check_match(point,lat,lon,sealev,lat_ind,lon_ind)
    if found_ok:
        #print(p_name,round(dist,2)," km" )
        return match_index,dist


    # Trying to enlarge the area

    distances_topoint = []
    match_indexes = []
    new_directionmap = []
    found_expanded = False
    #print("len direc. map",len(direction_map))

    for ind in range(len(direction_map)):       # 8 directions to expand search
        if direction_map[ind][2] == True:
            new_latind = lat_ind + (direction_map[ind][0])*3    # jumping to new 9 square box
            new_lonind = lon_ind + (direction_map[ind][1])*3
            (found_ok,match_index,dist,direction_map2) = check_match(point,lat,lon,sealev,new_latind,new_lonind)
            if found_ok == True:
                found_expanded = True         # To book keep if second round was successfull
                match_indexes.append(match_index)         # To book keep  best matches from each box
                distances_topoint.append(dist)
                #print("dist",dist)
            else:
                new_directionmap.append(direction_map2)   # In case this fails..

    if not found_expanded:
        print("Problems finding ",p_name)
    else:
        min_ind=np.argmin(distances_topoint)
        #print(p_name, round(distances_topoint[min_ind],2)," km") #,match_indexes[min_ind])
        return match_indexes[min_ind],distances_topoint[min_ind]




def open_ncfiles(file,p_names,p_lat,p_lon,grid_matches):
    nc_data = Dataset(file, 'r')
    lat = (nc_data.variables['latitude'])
    #print(model_grid_lat.shape)
    lon = (nc_data.variables['longitude'])
    #print(model_grid_lon.shape)
    sealev = nc_data.variables['sla'][:]
    #print(sealev[0][(lat_gridmatch[0])][(lon_gridmatch[0])])
    #print(len(p_names),len(lon_gridmatch))

    time = nc_data.variables['time'][:]

    time_zero = datetime.datetime(1950, 1, 1, 0, 0, 0)  # Dates are given as days since 1.1.1950
    time_datenum = []
    for ind in range(len(time)):
        time_datenum.append(roundTime((datetime.timedelta(days=float(time[ind])) + time_zero),roundTo=60*60))

    all_sealevels=[]
    latitude = []
    longitude = []
    #print(sealev.shape)
    print(len(time_datenum))
    
    for name in p_names:
        for index in range(len(grid_matches)):
            if name == grid_matches[index][0]:         # the right row of grid_matches
                lat_ind = grid_matches[index][1]
                lon_ind = grid_matches[index][2]
                latitude.append( lat[lat_ind] )
                longitude.append(lon[lon_ind] )

                for tt in range(0,24):
                    all_sealevels.append(sealev[tt][lat_ind][lon_ind])


    print_values=[]

    for ind in range(len(p_names)):
        for tt in range(0,24):
            print_values.append("{:20}\t\{:15}t{:10.6}\t{:10.6}\t{:10.6}\n".format(p_names[ind],time_datenum[tt],p_lat[ind],p_lon[ind],all_sealevels[tt]),latitude[ind],longitude[ind])


    return

def print_ncattr(nc):

    # print(nc.data_model)                          # Type of nc file
    nc_keys=(nc.dimensions.keys())
    print(nc_keys)


    # for key in nc_keys:
    #     try:
    #         print(nc.dimensions[key])
    #         print(nc.variables[key])
    #     except:
    #         print("Couldn't print variable info on key ",key)

    # # For printing other needed variables
    # print("................................................................")
    # #print(nc.variables)
    print(nc.variables["sla"])          ### This now sea level anomalies
    print(nc.variables["latitude"])
    print(nc.variables["longitude"])
    print(nc.variables["time"])
    # print(nc.variables["SLEV_QC"])
    #
    # # For printing attributes
    # print("................................................................")
    #for attr in nc.ncattrs():
     #   print (attr, '=', getattr(nc, attr))                # to print all attributes
    #
    #     #if attr == "sea_level_datum":                        # no longer global attribute
    #     #    print(getattr(nc,attr) )
    #
    #     if attr == "platform_code":
    #         print("station ",getattr(nc, attr))
    #
    #     elif attr == "source":
    #         print("source", getattr(nc, attr))
    #
    #     elif attr == "area":
    #         print("area", getattr(nc, attr))
    #
    # return

def change_qualflags(qual):
    # USE THIS ONLY IF NEEDED FOR GL TYPE quality flags

    for index in range(len(qual)):
        if qual[index] in [0,2,6]: # if original flaq is 0 (no qc performed), 2 (probably good data) or 6 (not used) -> new flaq 3 (unknown)
            qual[index]=3
        elif qual[index] in [3,4,5,7]:  # if original flag is 3 (bad data, possibly correctable) 4 ( bad data), 5 (value changed) or 7 (nominal value) -> new flaq is 9 missing
            qual[index]=9
        elif qual[index] == 8: #if original flag is 8 (interpolated value) new flaq is 2 interpolated value
            qual[index] = 2

    return qual



def change_tocm(sealev, qual, units):

    if units =="m":
        for index in range(len(qual)):
            if not qual[index] == 9:
                sealev[index]=sealev[index]*100             # Change from meters to cm
                units="cm"
    else:
        print("Units were not in meter.")
    return sealev, units


def check_nsfile(time, sealev, qual):


    return


def update_header(Headers, stationname, latitude, longitude,datum,time_dif,starttime, endtime,total,missing,units):
    # Updates header info
    # like in tgtools
    Headers["Source"] = "CMEMS"
    Headers["Interval"] = time_dif
    Headers["Datum"] = datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)

    if GLstyle:
        Headers["Missing values"] = str(missing)

    if units == "cm":
        Headers["Unit"] = "centimeter"
    else:
        Headers["Unit"] = "meter"

    return Headers

def write_file(filename,Headers,order, times,sealev,qual,station):
    # Makes an output folder if it doesen't exist and then calls in functions to check that data is in order
    # and creates needed variables for header, then it updates and orders the header and finally writes the output.


    output_file=output_path+station.replace(" ", "")+".txt"                   # HERE OUTPUTFILENAME
    # output_file=output_path+"Gl_"+filename[:-3]+".txt"                             # replace takes away empty spaces

    #print("outputpath",output_path)
    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)


    if len(Headers.keys()) == 0:
        # Check for empty header, warn if so.
        print("! Warning: empty header")
    Header = []
    # print(order)
    # print(HeaderDict)
    for key in order:
        try:
            Header.append([key, Headers[key]])
        except KeyError:
            Header.append([key, ""])
    #print(Header)
    output = []
    for line in Header:
        # print(line)
        # Loop through all header lines
        if not len(line) == 2:
            # Header line should only have to elements (key and value)
            print("! Warning: broken header line:", line)
        else:
            # If there's nothing in either position of the header,
            # replace it with an empty string.
            if line[0] == None:
                line[0] = ""
                print("! Warning: nameless header field: ", line)
            if line[1] == None:
                line[1] = ""
                print("! Warning: valueless header field: ", line)
            # Header name length
            if len(line[0]) > 20:
                print('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))
        output.append("%-20s%s\n" % (line[0][0:20], line[1]))

    file = open(output_file, 'w')
    # print(output)

    # Writing headers
    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')

        # Writing values


    for ii in range(len(times)):
        file.write("{}\t{:6.4}\t{:3}\n".format(times[ii],  sealev[ii], qual[ii]))
    file.close()


def check_order(file, dates):

    if dates != sorted(dates):
        print("Warning, data is not in order in file: ",file)

    return





####################################################################################################



def main():
    ##### Plan first open one nc file from test folder, then search for location of single lat,lon, get variables,write variables to file
    ##### Suomenlahti_point (others would be Selkameri_point, Perameri_point, and the sl stations with their names)
    ##### Then expand the search to all the stations needed, this requires station list of needed stations
    ##### Then think about the format of writing the files and the folder structure, do we need headers for this data?
    ##### When output is how we like it to be, expand the the search to all nc files (years,months,days)




    # Use: See readme file

    #headfile = headerfilename
    #if GLstyle:
    #    headfile=headerfilename2

    #(Header_dict,header_order)=get_headers(headfile)        #  getting header model

    (data,okey)=open_txtfile(interest_points)
    if not okey:
        print("Not finding a file of interest points. ",interest_points)

    p_names=[]                      # point names
    p_lat=[]                        # point lat
    p_lon=[]                        # pont lon

    for ii in range(len(data)):
        p_names.append(data[ii].split()[0].strip())
        p_lat.append(float(data[ii].split()[1].strip()))
        p_lon.append(float(data[ii].split()[2].strip()))
    
    #print(p_names[-1],p_lat[-1],p_lon[-1])

    
   # print(data[0:3])

    os.chdir(path)

    file_number=0


    for file in glob.glob("*.nc"):                 # Opens all that ends with .nc files in the path folder one by one

        file_number=file_number+1
        print(file)
        if file_number == 1:
            match_index=get_grid(file,p_names,p_lat,p_lon)        # gets grid matches from first file (files need to be in a same grid all)
        open_ncfiles(file,p_names,p_lat,p_lon,match_index)


        # missing="not count"
        #  if not okey:
        #    print("Something went wrong opening nc-file",file, "Coudn't convert to txt file.")
        # else:
        #
        #    if GLstyle:
        #        qual_f=change_qualflags(qual_f) # changes quality flags to gl format
        #         (sealev, missing) = prep_data(file, sealev, qual_f)
        #     else:
        #         (sealev, missing,Header_dict) = prep_data2(file, sealev, qual_f, Header_dict)
        #
        #     if units != "cm":
        #         if units == "m":
        #             (sealev, units)=change_tocm(sealev,qual_f,units)   ### Changing from meters to cm
        #         else:
        #             print("Units not in meters or centimeters, units",file, units)
        #             exit()
        #
        #     check_order(file,time)
        #     if t_diff!=time_difference:
        #         print("Wrong sampling rate", time_difference,t_diff)
        #         exit()
        #     Header_dict=update_header(Header_dict,station,lat,lon,datum,t_diff,time[0],time[-1],len(time),missing,units)
        #     write_file(file,Header_dict,header_order,time,sealev,qual_f,station)
        #     print(station," done")


            # Missing code if sampling rate is wrong, or if order is wrong





if __name__ == '__main__':
    main()
