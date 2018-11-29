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

# TESTING

headerfilename=('header.txt')           # Header titles as a txt file, should be in the working directory
path="..\\"                      # Path for the original data file folder, best not to have anything else
output_path= path +"\Test\\"      # than the .nc data file in this directory
time_difference=60                      # Time difference in minutes between measurements

# Function 1
def open_rfile(file_name):
    # Called by: get_headers / Function 2,Calls: -
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_rfile/Function1.".format(file_name))   # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok

# Function 2
def get_headers():
    # Called by: Main , Calls: open_rfile/Function 1
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    # Almost completely like in tgtools
    (headerfile,opened)=open_rfile(headerfilename)  # Function 1
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
def open_ncfiles(file,header):
    data = Dataset(file)
    #Called by: Main , Calls:update_header
    # Opens CMEMS .nc files, then reads the data and maybe updates the header, Checks the sea level data and
    # marks smaller than -9999 or bigger than 9999 as nan value, then changes sea level from meters to cm.
    #print(data.dimensions.keys())
    #print(data.dimensions['TIME'])
    #print(data.variables.keys())
    #print(data.variables['TIME'])
    try:
        nc = Dataset(file, 'r')
        lat = nc.variables['LATITUDE'][0]
        lon = nc.variables['LONGITUDE'][0]
        t = nc.variables['TIME']
        s = nc.variables['SLEV'][:]
        q = nc.variables['SLEV_QC'][:, 0]
        #print(nc.variables['Time'])
        for attr in nc.ncattrs():
            if attr=="sea_level_datum":
                datum=(getattr(nc,attr))
            elif attr=="platform_code":
                station=(getattr(nc,attr))
                #print(datum)
                print(station)
            #print (attr, '=', getattr(nc, attr))   # This can be used if want to see all of the attributes
        okey=True
    except:
        okey=False
        return [], header,"", okey


    time_zero = datetime.datetime(1950, 1, 1, 0, 0, 0)  # Dates are given as days since 1.1.1950
    times = []
    for index in range(0, len(t)):
        times.append(datetime.timedelta(days=t[index]) + time_zero)
        # print
        # lat, lon
    variables=[]

    if (not len(s)==len(t)) and (not len(s)==len(q)):           # Extra test, variables need to be of same length
        print("Something wrong possibly in the NC-files, variables are not of same length")
        exit()
    if len(times)>2:
        t_diff=(times[1]-times[0])
    header = update_header(header, station, lat, lon, datum,t_diff)  # Function 4

    #print(s)
    #s_s=0
    for ind in range(len(s)):                   # Checks that sea level value ok [-9999,9999] and changes it to cm
        if not len(s[ind])==1:
            print("Problem with opening NC-file in function open_nc, multiple values for a single timestamp:",s[ind])
            #s_s=s_s+1
        elif s[ind]<9999 and s[ind]>-9999:
            variables.append([times[ind],(s[ind][0])*100,int(q[ind])])
            #print(times[ind],s[ind],s[ind]*100)
        else:
            variables.append([times[ind],np.nan,9])
            # here append 9 to flag
    #print("Problems:",s_s)
    return variables, header,station,okey


# Function 4
def update_header(Headers, stationname, latitude, longitude,datum,time_dif):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    Headers["Source"] = "CMEMS"
    Headers["Interval"] = time_dif
    Headers["Datum"] =datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
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
    #print(Headers)
    #print(output_file)
    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)               # Function 8
    write_output(Headers_filled,sl_variables,order,output_file)                             # Function 9

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

    missing=0
    nans=0
    counting_sev=0
    counting_bad=0
    counting_maybe=0
    counting_strange=0
    counting_shouldnt=0
    for index in range(len(sl_variables)):              # Missing= either 9 as a quality flag or nan as the value
        if sl_variables[index][2]==9:                   # old flag 3,4,7,9 -> 9 (missing)
            missing = missing + 1                       # value=nan
            sl_variables[index][1] = np.nan
        elif np.isnan(sl_variables[index][1]):
            sl_variables[index][2] = 9
            nans=nans+1
            missing = missing + 1
        elif sl_variables[index][2]=="7":
            sl_variables[index][2] = 9
            counting_sev=counting_sev+1
            missing = missing + 1
            sl_variables[index][1]=np.nan
        elif sl_variables[index][2]==4 or sl_variables[index][2]==3:
            counting_bad=counting_bad+1
            missing = missing + 1
            sl_variables[index][1]=np.nan
            sl_variables[index][2] = 9

        elif sl_variables[index][2]==0:                 # old flag 0,2,6,5 -> 3 (unknown)
            sl_variables[index][2]=3
        elif sl_variables[index][2]==2:
            counting_maybe = counting_maybe + 1
            sl_variables[index][2] = 3
        elif sl_variables[index][2]==6:
            counting_strange=counting_strange+1                 # old flag 1 =1
            sl_variables[index][2] = 3
        elif sl_variables[index][2]==5:
            counting_strange=counting_strange+1
            sl_variables[index][2] = 3

        elif sl_variables[index][2]==8:                         # old flag 8-> 2
            sl_variables[index][2] = 2
        elif sl_variables[index][2]==1:
            a=1
        else:
            counting_shouldnt=counting_shouldnt+1


    #print("Qual flaq Gul=Y",counting_y)
    #print(missing)
    #print("nans",nans)
    print("nominal values changed to nan",counting_sev)
    print("bad values changed to nan", counting_bad)
    print("counting maybe okey", counting_maybe)
    print("counting not used or changed", counting_strange)
    print("counting flags that don't mach", counting_shouldnt)

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







def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: process_file /Function 4 , Calls: -
    # Fills headers
    # Almost completely like in tgtools
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Missing values"] = str(missing)

    return Headers


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
    # Called by: -, Calls: get_headers/Function2, open_ncfiles/Function 3, process_file/Function 4
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, gettin header model

    os.chdir(path)
    for file in glob.glob("*.nc"):                 # Opens all that ends with .csv in the path folder one by one
        (sl_variables,Header_dict,station,okey)=open_ncfiles(file,Header_dict)        # Function 3
        #print(Header_dict)
        #open_ncfiles ,updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable, changes sealevel measurements from m to cm
        if not okey:
            print("Something went wrong opening nc-file",file,"exiting program.")
            exit()

        #print(lat,lon,times[0:10],slev[0:10],qual[0:10])
        process_file(file,sl_variables,Header_dict,header_order,station) # Function 5
        # process_file, checks the order, adds missing, counts some header info, writes gl-files





if __name__ == '__main__':
    main()