#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# This is the old code from daily files maker and the spotly write from read_files.py


# def SPOTLwrite3(savename, date, gridx, gridy, sea, Sporder):  # writes output into spotl format
#     #    from weteread  import WeteRead  #for testing
#     #    import matplotlib.pyplot as plt
#     print
#     'writing in:', savename
#     spfile = open(savename, 'w')
#     spfile.write('H2O\n')
#     spfile.write('0 0 0 0 0 0\n')
#     line1 = "{:9.3f}".format(gridy[-1, -1])  # writes max latitude
#     spfile.write(line1[0:5] + '    ' + line1[6:9] + '\n')  # writes max latitude
#     line1 = "{:9.3f}".format(gridy[0, 0])  # writes min latitude
#     spfile.write(line1[0:5] + '    ' + line1[6:9] + '\n')  # writes min latitude
#     line1 = "{:9.3f}".format(gridx[-1, -1])  # max longitude
#     spfile.write(line1[0:5] + '    ' + line1[6:9] + '\n')
#     line1 = "{:9.3f}".format(gridx[0, 0])  # min longitude
#     spfile.write(line1[0:5] + '    ' + line1[6:9] + '\n')
#
#     nn = shape(sea.T)
#     spfile.write("{:5d} {:5d}".format(nn[0], nn[1]) + '\n')
#     spfile.write("surface fit" + str(date) + '\n')
#     if Sporder == 1:
#         SPsea = 10 * flipud(sea).T.reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 2:
#         SPsea = 10 * flipud(sea).reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 3:
#         SPsea = 10 * fliplr(sea).T.reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 4:
#         SPsea = 10 * fliplr(sea).reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 5:
#         SPsea = 10 * sea.reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 6:
#         SPsea = 10 * sea.T.reshape((10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     elif Sporder == 7:
#         SPsea = 10 * flipud(fliplr(sea)).T.reshape(
#             (10, -1))  # the order of writing of output file   # 10* converts cm to mm
#     else:  # 0  or 8
#         SPsea = 10 * flipud(fliplr(sea)).reshape(
#             (10, -1))  # the order of writing of output file   # 10* converts cm to mm
#
#     # may need also or instead flipud(sea) or fliplr(sea)
#     for ii in range(shape(SPsea)[1]):
#         for jj in range(10):  # 10i7  10 digits per line
#             spfile.write(" {:6.0f}".format(int(SPsea[jj, ii])))
#         spfile.write('\n')
#     for ii in range(shape(SPsea)[1]):  # writes zeros (imaginary part)
#         for jj in range(10):
#             spfile.write("      0")  # must contain 6 spaces exactly (each number consists of 7 digits)
#         spfile.write('\n')
#
#     print
#     'saved.'
#     spfile.close
#
#
# # x,y,z=WeteRead(savename)
# # p=plt.contour(x,y,z)
# # plt.show


headerfilename=('header_daily.txt')                       # Header titles as a txt file, should be in the working directory
path="..\DATA\Data_new\CMEMS_hourly_EVRF07\Time_range\Checked\Years_2005_2009\\"                            # Path for the original data file folder, best not to have anything else
output_path= "..\Daily\Year_2006\\"        # than the .txt data file in this directory
time_period_start=datetime.datetime(2006,1,1,0,0)                    # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end=datetime.datetime(2006,12,31,23,0)


# Function 1
def open_rfile(file_name):
    # Called by: get_headers / Function 2,Calls: -
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_rfile/Function1.".format(file_name))
        # Returns empty data variable and False if not successfull
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
            if ":" in line:
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
def get_data(day, Header_dict,order):
    # # Called by: Main , Calls: update_header / Function 5, open_rfile/Funtion1, format_data /Function 4
    # # Finds data of correct day and writes it to a file

    okey=False
    file_count=0
    bad_station_count=0
    data_all=[]
    nan_all=0
                                # File count= Number of all the files in that directory
                                # Bad_station_count= number of all the stations where no data for that day or file coudn't be opened

    for file in glob.glob("*.txt"):                 # Opens all that ends with .txt in the path folder one by one
        nancount=0
        file_count=file_count+1
        (data,get_data_success)=open_rfile(file)            # Function 1 open_rfile
        if not get_data_success:
            print("Warning, something wrong opening file", file)
            bad_station_count=bad_station_count+1
        (formatted_data,nancount,bad_station)=format_data(data,day)   # Function 4 Format data
        #print(len(formatted_data))                                     # Bad station is logical, nancount is number
        if bad_station:
            bad_station_count=bad_station_count+1
        else:
            for ind in range(len(formatted_data)):
                data_all.append(formatted_data[ind])
            nan_all=nan_all+nancount


    update_header(Header_dict,day,file_count,file_count-bad_station_count, nan_all,len(data_all)) # Function 5 update_header
    day_string=(day.strftime("%Y_%m_%d"))
    write_output(data_all,Header_dict,order,day_string)
    if len(data_all)!=0:
        okey=True
    return okey

# Function 4
def format_data(data, date_):
    # Called by: get_data/Function 3 Calls: -
    # Opens the datafile and reads it to a variable
    variables=[]
    bad_station=False
    nancount=0
    for line in (data[0:20]):
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()
            if splitline[0]=="Station":
                station=splitline[1].strip()
            elif splitline[0]=="Longitude":
                lon=splitline[1].strip()
            elif splitline[0]=="Latitude":
                lat = splitline[1].strip()
    if not (data[20][0]=="-"):    # juts an extra check that header size is normal
        print("Header size of file is not expected in file: ",file)
        exit()

        # Reading the file
    date=[]
    time=[]
    slev=[]
    qual=[]
    for ind in range(21,len(data)):
        splitline=(data[ind]).split()
        try:
            date.append(splitline[0].strip())
        except:
            print(splitline, ind)
            print(len(data))
        time.append(splitline[1].strip())
        slev.append(float(splitline[2].strip()))
        qual.append(int(splitline[3].strip()))

    for ind in range(len(slev)):
        splitdate=((date[ind]).split("-"))
        splittime=((time[ind]).split(":"))
        thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                    int(splittime[1])))
        # Making sure that if value=nan then flag=9 and vise versa

        if (thisdate>=date_ and thisdate<(date_ + datetime.timedelta(days=1))):

            if np.isnan(float(slev[ind])) or int(qual[ind])==9:
                variables.append([thisdate,station,lat,lon, np.nan, 9])
                nancount=nancount+1
            else:
                variables.append([thisdate,station,lat,lon,float(slev[ind]),int(qual[ind])])
    if len(variables)==nancount:
        bad_station=True

    return variables,nancount, bad_station

# Function 5
def update_header(Headers, date_, StaNro, StaGood, missing, total):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    Headers["Day"] = date_
    Headers["Stations expected"] = StaNro
    Headers["Stations with data"] = StaGood
    Headers["Missing values"] = missing
    Headers["Total values"] = total
    return Headers

# Function 9
def write_output(sl_variables,HeaderDict, order, time_marker):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output
    # Very much like in tgtools

    output_file=output_path+time_marker+".txt"
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []

    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])

    # The header writing code, contains various checks.
    output=[]
    for line in Header:
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
            #if line[0] == "" :
            #    print ("! Warning: nameless header field: ", line)
            #if line[1] == "" :
             #   print ("! Warning: valueless header field: ", line)
            # Finally write header line. Limit first field to 20 characters.
            if len(line[0]) > 20 :
                print ('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))

            output.append("%-20s%s\n" % (line[0][0:20], line[1]))

    try:
        file = open(output_file, 'w')
        # print(output_file)
    except:
        print("Couldn't open file to print into.")


    # Writing headers
    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')


    # Writing values
    date=[]
    time=[]
    slev=[]
    qual=[]
    stat=[]
    lat=[]
    lon=[]

    for ii in range(len(sl_variables)):
        date.append((sl_variables[ii][0]).strftime("%Y-%m-%d"))
        time.append((sl_variables[ii][0]).strftime("%H:%M"))
        stat.append(sl_variables[ii][1])
        lat.append(str(sl_variables[ii][2]))
        lon.append(str(sl_variables[ii][3]))
        slev.append(str(sl_variables[ii][4]))
        qual.append(sl_variables[ii][5])
    prints=[]
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:12}\t{:3.4}\t{:3.4}\t{:6.4}\t{:3}\n".format(date[ind],time[ind],stat[ind],lat[ind],lon[ind],slev[ind],qual[ind]))

    try:
        for ind in range(len(sl_variables)):
            file.write(prints[ind])
    except:
        print("Couldn't write file")
    file.close()





####################################################################################################



def main():
    # Called by: -, Calls: get_headers/Function2, get_data /Function
    # Use: See readme file
    (Header_dict,header_order)=get_headers()        # Function 2, getting header model
    os.chdir(path)

    if time_period_end<=time_period_start:
        print("Check dates you want to have")
        exit()
    start_time=time_period_start
    end_time=time_period_end
    count=0

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    while end_time>start_time:
        (data_found)=get_data(start_time,Header_dict, header_order) # Function 3, for opening and processing and writing to file the files for that day
        if not data_found:
            print("Warning, Couldn't find data on ", start_time)
        count=count+1
        start_time=start_time+datetime.timedelta(days=1)
        #print(start_time)






if __name__ == '__main__':
    main()
