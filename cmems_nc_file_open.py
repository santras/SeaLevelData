#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from netCDF4 import Dataset


# The purpose of this code is to change Copernicus MEMS Data to GL-format
# Test that all date in order
# Makes header from a file that contains the header titles and the order, location of the file header.txt can be
# changed from the beginning of this file
# Writes output file in the "gl"-format.

# TESTING commit again again
GLstyle= False                            # True if want to do gl-format for output
headerfilename=('header_cmems.txt')      # Header titles as a txt file, should be in the working directory
headerfilename2=('header.txt')           # GL (style header file)
path="../TGData//"                      # Path for the original data file folder, best not to have anything else
output_path= path +"../TGData_txt//"      # than the .nc data file in this directory
time_difference=60                      # Time difference in minutes between measurements

# Function 1
def open_txtfile(file_name):
    # Calls: -
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

# Function 2
def get_headers(headfile):
    # Calls: open_txtfile/Function 1
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    (headerfile,opened)=open_txtfile(headfile)  # Function 1
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

# Function 3
def open_ncfiles(file):
    #Calls:update_header
    # Opens CMEMS Baltic Tide Gauge .nc files, then reads the data and updates the header, Checks the sea level data and
    # marks smaller than -9999 or bigger than 9999 as nan value, then changes sea level from meters to cm.



    nc_data = Dataset(file, 'r')
    #print_ncattr(nc_data)                          ######## Here for printing nc file attributes and variables

    try:

        lat = float(nc_data.variables['LATITUDE'][0])     # Only takes the first ones since tide gauge is stationary
        lon = float(nc_data.variables['LONGITUDE'][0])
        time = (nc_data.variables['TIME'][:])
        sealev = nc_data.variables['SLEV'][:]                # For sea level variables
        sealev_meta =nc_data.variables["SLEV"]                   # For sea level variable meta
        qual_f = nc_data.variables['SLEV_QC'][:, 0]             # Sea level quality flag




        station = ""

        for attr in nc_data.ncattrs():                           # Getting station name
            if attr == "platform_code":
                station = (getattr(nc_data,attr))



        # Getting datum from  sea level variables inner attribute
        datum=sealev_meta.sea_level_datum                                     # Datum here!
        units=str(sealev_meta.units)
        t_diff=int(sealev_meta.time_sampling)

        okey=True
        nc_data.close()
    except:
        return False, [], [], [],"","","","","",""



    #print(t[0:10],type(t))
    time_zero = datetime.datetime(1950, 1, 1, 0, 0, 0)  # Dates are given as days since 1.1.1950
    times = []

    for index in range(0, len(time)):
        times.append(datetime.timedelta(days=float(time[index])) + time_zero)

    return okey, times, sealev, qual_f, lat, lon, station, datum, units, t_diff


def print_ncattr(nc):

    # print(nc.data_model)                          # Type of nc file
    nc_keys=(nc.dimensions.keys())
    print(nc_keys)


    for key in nc_keys:
        try:
            print(nc.dimensions[key])
            print(nc.variables[key])
        except:
            print("Couldn't print variable info on key ",key)

    # For printing other needed variables
    print("................................................................")
    #print(nc.variables)
    print(nc.variables["SLEV"])
    print(nc.variables["SLEV_QC"])

    # For printing attributes
    print("................................................................")
    for attr in nc.ncattrs():
        #print (attr, '=', getattr(nc, attr))                # to print all attributes

        #if attr == "sea_level_datum":                        # no longer global attribute
        #    print(getattr(nc,attr) )

        if attr == "platform_code":
            print("station ",getattr(nc, attr))

        elif attr == "source":
            print("source", getattr(nc, attr))

        elif attr == "area":
            print("area", getattr(nc, attr))

    return

def change_qualflags(qual):
    # USE THIS ONLY IF NEEDED


    for index in range(len(qual)):
        if qual[index] in [0,2,6]: # if original flaq is 0 (no qc performed), 2 (probably good data) or 6 (not used) -> new flaq 3 (unknown)
            qual[index]=3
        elif qual[index] in [3,4,5,7]:  # if original flag is 3 (bad data, possibly correctable) 4 ( bad data), 5 (value changed) or 7 (nominal value) -> new flaq is 9 missing
            qual[index]=9
        elif qual[index] == 8: #if original flag is 8 (interpolated value) new flaq is 2 interpolated value
            qual[index] = 2

    return qual

def prep_data(file,sealev_raw,qual):

    sealev = []
    data_good = 0
    missing = 0
    no_qc = 0
    bad_data = 0
    prob_good = 0
    val_change = 0
    nominal = 0
    interpolated = 0
    #print(type(qual))

    for index in range(len(qual)):
        if qual[index]==1:
            sealev.append(float(sealev_raw[index]))
            data_good=data_good+1
        elif qual[index]==9:
            sealev.append(np.nan)
            missing=missing+1
        elif qual[index] in [3,4]:
            sealev.append(float(sealev_raw[index]))
            bad_data = bad_data + 1
        elif qual[index] in [0,6]:
            sealev.append(float(sealev_raw[index]))
            no_qc=no_qc+1
        elif qual[index] == 2:
            sealev.append(float(sealev_raw[index]))
            prob_good= prob_good + 1
        elif qual[index] == 5:
            sealev.append(float(sealev_raw[index]))
            val_change= val_change + 1
        elif qual[index] == 7:
            sealev.append(float(sealev_raw[index]))
            nominal= nominal + 1
        elif qual[index] == 8:
            sealev.append(float(sealev_raw[index]))
            interpolated= interpolated + 1
        else:
            print("Weirdness in quality flag in  ", file, index, qual[index])


    print("In file",file,":","Good data:", data_good," Missing Data:",missing," Bad Data:",bad_data," No QC:", no_qc, " Probably Good:",prob_good,
        " Value Changed:", val_change, " Nominal Value: ", nominal, " Interpolated:", interpolated)

    return sealev,missing

def prep_data2(file,sealev_raw,qual,headers):

    sealev = []
    data_good = 0
    missing = 0
    no_qc = 0
    bad_data_pos = 0
    bad_data = 0
    prob_good = 0
    val_change = 0
    nominal = 0
    not_used = 0
    interpolated = 0
    #print(type(qual))

    for index in range(len(qual)):
        if qual[index]==1:
            sealev.append(float(sealev_raw[index]))
            data_good=data_good+1
        elif qual[index]==9:
            sealev.append(np.nan)
            missing=missing+1
        elif qual[index] == 3:
            sealev.append(float(sealev_raw[index]))
            bad_data_pos = bad_data_pos + 1
        elif qual[index] == 4:
            sealev.append(float(sealev_raw[index]))
            bad_data = bad_data + 1
        elif qual[index] == 0:
            sealev.append(float(sealev_raw[index]))
            no_qc=no_qc+1
        elif qual[index] ==6:
            sealev.append(float(sealev_raw[index]))
            not_used = not_used + 1
        elif qual[index] == 2:
            sealev.append(float(sealev_raw[index]))
            prob_good= prob_good + 1
        elif qual[index] == 5:
            sealev.append(float(sealev_raw[index]))
            val_change= val_change + 1
        elif qual[index] == 7:
            sealev.append(float(sealev_raw[index]))
            nominal= nominal + 1
        elif qual[index] == 8:
            sealev.append(float(sealev_raw[index]))
            interpolated= interpolated + 1

        else:
            print("Weirdness in quality flag in  ", file, index, qual[index])

    headers["0 No QC performed"] = no_qc
    headers["1 Good"] = data_good
    headers["2 Probably good"] = prob_good
    headers["3 Bad pos. corr."] = bad_data_pos
    headers["4 Bad Data"] = bad_data
    headers["5 Value changed"] = val_change
    headers["6 Not used"] = not_used
    headers["7 Nominal value"] = nominal
    headers["8 Interpolated"] = interpolated
    headers["9 Missing value"] = missing

    #print("In file",file,":","Good data:", data_good," Missing Data:",missing," Bad Data:",bad_data," No QC:", no_qc, " Probably Good:",prob_good,
    #    " Value Changed:", val_change, " Nominal Value: ", nominal, " Interpolated:", interpolated)


    return sealev,missing,headers

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


# Function 4
def update_header(Headers, stationname, latitude, longitude,datum,time_dif,starttime, endtime,total,missing,units):
    #Called by: open_ncfiles/Function3,  Calls:-
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

# Function 5
def write_file(filename,Headers,order, times,sealev,qual,station):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
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


#Function 6
def check_order(file, dates):

    if dates != sorted(dates):
        print("Warning, data is not in order in file: ",file)

    return





####################################################################################################



def main():
    # Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file

    headfile = headerfilename
    if GLstyle:
        headfile=headerfilename2

    (Header_dict,header_order)=get_headers(headfile)        # Function 2, getting header model

    os.chdir(path)

    for file in glob.glob("*Aarhus.nc"):                 # Opens all that ends with .nc files in the path folder one by one

        (okey,time,sealev,qual_f,lat, lon, station, datum, units, t_diff)=open_ncfiles(file)        # Function 3, opens nc file


        missing="not count"
        if not okey:
            print("Something went wrong opening nc-file",file, "Coudn't convert to txt file.")
        else:

            if GLstyle:
                qual_f=change_qualflags(qual_f)
                (sealev, missing) = prep_data(file, sealev, qual_f)
            else:
                (sealev, missing,Header_dict) = prep_data2(file, sealev, qual_f, Header_dict)

            if units != "cm":
                if units == "m":
                    (sealev, units)=change_tocm(sealev,qual_f,units)   ### Changing from meters to cm
                else:
                    print("Units not in meters or centimeters, units",file, units)
                    exit()

            check_order(file,time)
            if t_diff!=time_difference:
                print("Wrong sampling rate", time_difference,t_diff)
                exit()
            Header_dict=update_header(Header_dict,station,lat,lon,datum,t_diff,time[0],time[-1],len(time),missing,units)
            write_file(file,Header_dict,header_order,time,sealev,qual_f,station)


            #check_nsfile(time,sealev,qual_f)

        #print(lat,lon,times[0:10],slev[0:10],qual[0:10])
        #process_file(file,sl_variables,Header_dict,header_order,station) # Function 5
        # process_file, checks the order, adds missing, counts some header info, writes gl-files





if __name__ == '__main__':
    main()