#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to re-write the station-by-station sealevel files into day by day sealevel files to make the plotting faster

path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt"                            # Path for the original data file folder, best not to have anything else
output_path= "../Daily_files/Test"        # than the .txt data file in this directory
time_period_start=datetime.datetime(2017,1,1,0,0)                    # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end=datetime.datetime(2017,1,1,23,0)


def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_txtfile.".format(file_name))
        # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok

def get_data(start,end):
    # # Finds data of correct day and writes it to a file
    okey=False
    file_count=0
    station_list=[]         # to make a file of stations,countries and lat and lon that were used

    data_all=[]

    for file in glob.glob("R*.txt"):                 # Opens all that ends with .txt in the path folder one by one
        (data,get_data_success)=open_txtfile(file)
        if not get_data_success:
            print("Warning, something wrong opening file", file)

        # Here check if file has correct days               % cmems header style used

        s_nums = (data[6].split()[2].split("-"))
        e_nums = (data[7].split()[2].split("-"))
        s_date=datetime.datetime(int(s_nums[0].strip()),int(s_nums[1].strip()),int(s_nums[2].strip()))
        e_date = datetime.datetime(int(e_nums[0].strip()), int(e_nums[1].strip()), int(e_nums[2].strip()))
        #print(s_date,e_date)


        retrieve_okey=False

        if not (start>e_date or start<s_date):   # To check that start date within time interval given
            #print("Data should be here",file,start,end,e_date,s_date)
            (data_formatted,bad_station)=format_data(data,start, end)
            if not bad_station:
                if data_formatted != []:
                    file_count = file_count + 1
                    retrieve_okey=True
                    #print("Data found",file)
                #else:
                    #print("Data not found,empty", file)
            #else:
                #print("Data not found,boolen",file)

        #else:
            #print(start,s_date,e_date)

    #     #print(len(formatted_data))
    #     if bad_station:
    #         bad_station_count=bad_station_count+1
    #     else:
    #         for ind in range(len(formatted_data)):
    #             data_all.append(formatted_data[ind])
    #
    # update_header(Header_dict,day,file_count,file_count-bad_station, nancount,len(data_all))
    # day_string=(day.strftime("%Y_%m_%d"))
    # write_output(data_all,Header_dict,order,day_string)
    # if len(data_all)!=0:
    #     okey=True
    return okey

def format_data(data, start, end):
    variables=[]

    station=""
    lon=np.nan
    lat=np.nan
    time_sys=""
    datum=""
    bad_station=False

    for line in (data[0:22]):                                           # for cmems header, 20 for gl
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()

            if splitline[0]=="Station":
                station=splitline[1].strip()

            elif splitline[0]=="Longitude":
                lon=float(splitline[1].strip())

            elif splitline[0]=="Latitude":
                lat = float(splitline[1].strip())

            elif splitline[0] == "Datum":
                datum = splitline[1].strip()

            elif splitline[0] == "Time":
                print(datum)
                time_sys = splitline[2].strip()


    #print(station,lon,lat,time_sys,datum)
    # Some checks
    if not (data[23][0]=="-"):    # juts an extra check that header size is normal    #for cmems, 21 for gl
        print("Header size of file is not expected in file: ",file)
        bad_station=True
        return [], bad_station
    elif (datum != "EVRF07" and datum!="EVRF2007"):
        print("Datum not EVRF2007",datum)
        bad_station = True
        return [], bad_station
    elif time_sys != "UTC":
        print("Time system not UTC",time_sys)
        bad_station = True
        return [], bad_station
    else:
        date=[]
        time=[]
        slev=[]
        qual=[]
        for ind in range(24,len(data)):                     # for cmems header, for gl 21
            splitline=(data[ind]).split()
            date.append(splitline[0].strip())
            time.append(splitline[1].strip())
            slev.append(float(splitline[2].strip()))
            qual.append(int(splitline[3].strip()))

        nancount=0                                          # If station don't have measurements on the day

        for ind in range(len(slev)):
            splitdate=((date[ind]).split("-"))
            splittime=((time[ind]).split(":"))
            thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                    int(splittime[1])))


            if (thisdate>=start and thisdate<=end):
                variables.append([thisdate,station,lat,lon,float(slev[ind]),int(qual[ind])])
                if (np.isnan(float(slev[ind])) or int(qual[ind]))==9:
                    nancount=nancount+1


        if len(variables)==nancount:
            bad_station=True
            #print("Station not included, just missing data entries",station,nancount,len(variables))
        #else:
            #print("Station included",station,nancount,len(variables))

        return variables, bad_station

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


    if time_period_end<=time_period_start:
        print("Check dates you want to have")
        exit()
    start_time=time_period_start
    end_time=time_period_end
    count=0

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    os.chdir(path)



    while end_time>start_time:

        (data_found)=get_data(start_time, end_time)

        if not data_found:
            print("Warning, Couldn't find data on ", start_time)
        count=count+1
        start_time=start_time+datetime.timedelta(days=1)
        #print(start_time)

    #print(count)


        #(sl_variables,Header_dict,station,okey)=open_glfiles(file,Header_dict)        # Function 3
        #open_files ,updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        #if not okey:
        #    print("Something went wrong opening file",file,"exiting program.")
        #    exit()
        #process_file(file,sl_variables,Header_dict,header_order,station) # Function 5





if __name__ == '__main__':
    main()
