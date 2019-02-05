#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to re-write the station-by-station sealevel files into day by day sealevel files to make the plotting faster

path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned/"                            # Path for the original data file folder, best not to have anything else
output_path= "/home/sanna/PycharmProjects/Daily_files/2017/"        # than the .txt data file in this directory
time_period_start=datetime.datetime(2017,1,1,0,0)                    # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end=datetime.datetime(2017,12,31,23,0)
# doing 2017



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

def get_data(start):
    # # Finds data of correct day and writes it to a file
    okey=False
    file_count=0
    station_list=[]         # to make a file of stations,countries and lat and lon that were used

    data_all=[]

    for file in glob.glob("*.txt"):                 # Opens all that ends with .txt in the path folder one by one
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
            (data_formatted,bad_station)=format_data(data,start) # Gets data and boolean false if day looked for is only nans
            if not bad_station:
                if data_formatted != []:
                    file_count = file_count + 1
                    retrieve_okey=True                  # Retriev okey, if went okey
                    #print("Data found",file)
                #else:
                    #print("Data not found,empty", file)
            #else:
                #print("Data not found,boolen",file)
        #else:
            #print(start,s_date,e_date)

        #print(len(formatted_data))
        if retrieve_okey:
            for ind in range(len(data_formatted)):                  # Adds to data_all if data found in this file
                #print(data_formatted)
                data_all.append(data_formatted[ind])

    if len(data_all)!=0:
        okey=True
        write_output(data_all,start.date())

    return okey

def format_data(data, start):
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
                time_sys = splitline[2].strip()


    #print(station,lon,lat,time_sys,datum)
    # Some checks
    if not (data[23][0]=="-"):    # juts an extra check that header size is normal    #for cmems, 21 for gl
        print("Header size of file is not expected")
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


            if (thisdate>=start and thisdate<(start+datetime.timedelta(days=1))):
                variables.append([thisdate,station,lat,lon,float(slev[ind]),int(qual[ind])])
                if (np.isnan(float(slev[ind])) or int(qual[ind]))==9:
                    nancount=nancount+1


        if len(variables)==nancount:
            bad_station=True
            #print("Station not included, just missing data entries",station,nancount,len(variables))
        #else:
            #print("Station included",station,nancount,len(variables))

        return variables, bad_station


def write_output(sl_variables,time_marker):
    # Writes the output

    output_file=output_path+time_marker.strftime("%d_%m_%Y")+".txt"

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
        prints.append("{}\t{}\t{:26}\t{:6.4}\t{:6.4}\t{:6.4}\t{:3}\n".format(date[ind],time[ind],stat[ind],lat[ind],lon[ind],slev[ind],qual[ind]))

    file=open(output_file,'w')
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


    count=0

    while end_time>start_time:

        data_found=get_data(start_time)
        if not data_found:
            print("Warning, Couldn't find data on ", start_time)

        count=count+1
        print("Day count of search & write ",count)
        start_time=start_time+datetime.timedelta(days=1)










if __name__ == '__main__':
    main()
