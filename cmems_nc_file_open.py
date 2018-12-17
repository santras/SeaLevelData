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

headerfilename=('header.txt')           # Header titles as a txt file, should be in the working directory
path="../TGData//"                      # Path for the original data file folder, best not to have anything else
output_path= path +"../Tests//"      # than the .nc data file in this directory
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
def get_headers():
    # Calls: open_txtfile/Function 1
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    (headerfile,opened)=open_txtfile(headerfilename)  # Function 1
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

        lat = nc_data.variables['LATITUDE'][0]      # Only takes the first ones since tide gauge is stationary
        lon = nc_data.variables['LONGITUDE'][0]
        time = (nc_data.variables['TIME'][:])
        sealev = nc_data.variables['SLEV'][:]                # For sea level variables
        sealev_meta =nc_data.variables["SLEV"]                   # For sea level variable meta
        qual_f = nc_data.variables['SLEV_QC'][:, 0]               # Sea level quality flag




        station = ""

        for attr in nc_data.ncattrs():                           # Getting station name
            if attr == "platform_code":
                station = (getattr(nc_data,attr))



        # Getting datum from  sea level variables inner attribute
        datum=sealev_meta.sea_level_datum                                     # Datum here!

        # Checking that units are in meters
        if sealev_meta.units != "m":
            print("Warning in file", file, "unit is not in meter.")

        okey=True
        nc_data.close()
    except:
        return False, [], [], [],"","","",""

    return okey,time, sealev,qual_f,lat,lon, station,datum

    #print(t[0:10],type(t))
    time_zero = datetime.datetime(1950, 1, 1, 0, 0, 0)  # Dates are given as days since 1.1.1950
    times = []

    for index in range(0, len(t)):
        times.append(datetime.timedelta(days=float(t[index])) + time_zero)

    #
    if (not len(s)==len(t)) and (not len(s)==len(q)):           # Extra test, variables need to be of same length
        print("Something wrong possibly in the NC-files, variables are not of same length")
        exit()

    if len(times)>2:
        t_diff=(times[1]-times[0])
    else:
        print("File too short",file)
        return [], header,"", okey

    #print(type(s))

    count_dummy=0
    count_dummy2=0
    count_dummy3=0

    variables=[]

    #####PROBLEMS HERE with Masked Arrays and strange empty list (len=1) that are sometimes there instead of value marking

    for ind in range(len(s)):                   # Checks that sea level value ok and changes it to cm  #


        if str(s[ind][0]) in ["nan","NAN", "NaN", "", " ", "-", "--"]:
            count_dummy=count_dummy+1
            variables.append([times[ind],np.nan,9])
        elif float(s[ind]) == -999.0:                             ## This is what missing measurement should be
            count_dummy2 = count_dummy2 + 1
            variables.append([times[ind], np.nan, 9])
        else:
            variables.append([times[ind], (float(s[ind])) * 100, int(q[ind])])  # CHANGE FROM CM TO METER
            count_dummy3=count_dummy3+1

    #check_data()

    #print(len(s),count_dummy,count_dummy2, count_dummy3)
    header = update_header(header, station, lat, lon, datum, t_diff,times[0],times[-1],len(variables),
                           count_dummy+count_dummy2)                                            # Function 4


    return variables, header,station,okey


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

    count_dummy1 = 0
    count_dummy2 = 0
    count_dummy3 = 0
    count_dummy4 = 0
    counting_again_dummy =0

    for index in range(len(qual)):
        if qual[index] in [0,2,6]: # if original flaq is 0 (no qc performed), 2 (probably good data) or 6 (not used) -> new flaq 3 (unknown)
            qual[index]=3
            count_dummy1=count_dummy1+1
        elif qual[index] in [3,4,5]:  # if original flag is 3 (bad data, possibly correctable) 4 ( bad data) or 5 (value changed) new flaq is 0 bad data
            qual[index]=0
            count_dummy2 = count_dummy2 + 1
            if qual[index] in [3,4]:
                counting_again_dummy=counting_again_dummy+1
        elif qual[index] == 7: # if original flag is 7 (nominal value) new flaq is 9 missing value
            qual[index] = 9
            count_dummy3 = count_dummy3 + 1
        elif qual[index] == 8: #if original flag is 8 (interpolated value) new flaq is 2 interpolated value
            qual[index] = 2
            count_dummy4 = count_dummy4 + 1
        # 1 (good data) remains 1 (known to be good) and 9 (missing value) remains 9 (gap in data)

    print(count_dummy1,count_dummy2,count_dummy3,count_dummy4,counting_again_dummy)
    count_dummy=count_dummy1+count_dummy2+count_dummy3+count_dummy4

    return qual, count_dummy

def check_nsfile():

    return


# Function 4
def update_header(Headers, stationname, latitude, longitude,datum,time_dif,starttime, endtime,total,missing):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    Headers["Source"] = "CMEMS"
    Headers["Interval"] = time_dif
    Headers["Datum"] =datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)
    return Headers

# Function 5
def process_file(filename,sl_variables,Headers,order,station):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and then calls in functions to check that data is in order
    # and creates needed variables for header, then it updates and orders the header and finally writes the output.


    output_file=output_path+"Gl_"+station.replace(" ", "")+".txt"                   # HERE OUTPUTFILENAME
    # output_file=output_path+"Gl_"+filename[:-3]+".txt"                             # replace takes away empty spaces

    #print("outputpath",output_path)
    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    (sl_variables, missing, tot_values, start, end)=check_data(filename,sl_variables)   # Function 6


    write_output(Headers,sl_variables,order,output_file)                             # Function 9

#Function 6
def check_data(name,sl_variables):
    # Called by: process file/Function 5, Calls: check_listorder
    # Checks order, inserts missing values, counts number of total values,start date, end date

    transposed = []         # Trick to only send timestamps to the check_listorder function
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    (inorder,inds)=check_listorder(transposed[0],time_difference*60) # Function 7, checking if entries with 60 min time interval

    if not inorder:
        print("File "+name+" is not in order or entries are missing, ordering.")
        sl_variables=sorted(sl_variables)                           # And timestamps can be sorted..


    transposed = []                                     # Start date and end date
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    start_date=min(transposed[0])
    end_date=max(transposed[0])
    #print(start_date,end_date)                         # Length of file
    length=len(sl_variables)


    return sl_variables,missing,length,start_date,end_date



# Function 7
def check_listorder(dates,diff,current_ind=1):
    # Called by: check_data/Function6, Calls:-
    # Checks that the time difference between measurements is correct

    count = 0
    inds = []
    for ind in range(current_ind, len(dates)):
        if (dates[ind]-dates[ind-1]) != datetime.timedelta(seconds=diff):
            count = count + 1
            inds.append(ind)
    if count == 0:
        ok = True
    else:
        ok = False
    return ok, inds




def write_output(HeaderDict, sl_variables, order, outputfile):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output
    # Very much like in tgtools
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []
    #print(order)
    #print(HeaderDict)
    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])
    #print(Header)
    # The header writing code, contains various checks.
    output=[]
    for line in Header:
        #print(line)
        # Loop through all header lines
        if not len(line) ==  2:
            # Header line should only have to elements (key and value)
            print ("! Warning: broken header line:", line)
        else:
            # If there's nothing in either position of the header,
 			# replace it with an empty string.
            if line[0] == None:
                line[0] = ""
            if line[1] == None:
                line[1] = ""
            # Warn if header key or value are empty.
            if line[0] == "" :
                print ("! Warning: nameless header field: ", line)
            if line[1] == "" :
                print ("! Warning: valueless header field: ", line)
            # Finally write header line. Limit first field to 20 characters.
            if len(line[0]) > 20 :
                print ('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))

            output.append("%-20s%s\n" % (line[0][0:20], line[1]))

    file = open(outputfile, 'w')
    #print(output)

    # Writing headers
    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')


    # Writing values
    date=[]
    time=[]
    slev=[]
    qual=[]

    for ii in range(len(sl_variables)):
        date.append((sl_variables[ii][0]).strftime("%Y-%m-%d"))
        time.append((sl_variables[ii][0]).strftime("%H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints=[]
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:6.4}\t{:3}\n".format(date[ind],time[ind],slev[ind],qual[ind]))

    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()





####################################################################################################



def main():
    # Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, getting header model

    os.chdir(path)

    for file in glob.glob("*Aarhus.nc"):                 # Opens all that ends with .nc files in the path folder one by one

        (okey,time,sealev,qual_f,lat, lon, station, datum)=open_ncfiles(file)        # Function 3, opens nc file

        if not okey:
            print("Something went wrong opening nc-file",file, "Coudn't convert to txt file.")
        else:
            qual_f,count=change_qualflags(qual_f)
            print(file, " had quality flag count of",count," other than 1 good data or 9 missing data.")

        #print(lat,lon,times[0:10],slev[0:10],qual[0:10])
        #process_file(file,sl_variables,Header_dict,header_order,station) # Function 5
        # process_file, checks the order, adds missing, counts some header info, writes gl-files





if __name__ == '__main__':
    main()