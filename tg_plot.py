#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os, glob
import fnmatch
from scipy import stats



# The purpose of this code is to test the stations sea level values by plotting the data


path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned/"
output_path ="/home/sanna/PycharmProjects/PLOTS/TG_Data_Checks/"

start_time = datetime.datetime(2007,1,1)
end_time = datetime.datetime(2016,12,31,23)

#
def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened.".format(file_name))   # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok



def open_cmemsfiles(file,year,month):

    # Opens CMEMS  files, then reads the data
    (data,okey) = open_txtfile(file)

    # taking values and order from header

    for line in (data[0:22]):
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()
            if splitline[0]=="Station":
                station=splitline[1].strip()
            elif splitline[0]=="Longitude":
                lon=splitline[1].strip()
            elif splitline[0]=="Latitude":
                lat = splitline[1].strip()
            elif splitline[0]=="Datum":
                if len(splitline)==1:
                    datum=""
                else:
                    datum=splitline[1].strip()
            elif splitline[0]=="Source":
                if len(splitline)==1:
                    source=""
                else:
                    source=splitline[1].strip()


    date=[]
    time=[]
    slev=[]
    qual=[]
    #print(data[23])
    for ind in range(24,len(data)):
        splitline=(data[ind]).split()
        if int((splitline[0].strip()).split("-")[0]) == year:
            if int((splitline[0].strip()).split("-")[1]) == month:
                date.append(splitline[0].strip())
                time.append(splitline[1].strip())
                slev.append(float(splitline[2].strip()))
                qual.append(int(splitline[3].strip()))

    variables=[]
    for ind in range(len(date)):
        splitdate=((date[ind]).split("-"))
        splittime=((time[ind]).split(":"))
        thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                     int(splittime[1])))
        variables.append([thisdate,slev[ind],qual[ind]])

    return variables,station, okey




def process_file(filename,sl_variables,station,figu):


    sl_variables=sorted(sl_variables)



    values=[]
    for i in range(3):
        values.append([row[i] for row in sl_variables])


    tmax = np.max(values[0])
    tmin = np.min(values[0])
    maxi = np.nanmax(values[1])
    mini = np.nanmin(values[1])


    plt.plot(values[0], values[1], markersize=1,label=station)

    return figu, maxi, mini, tmax, tmin,nancount





def end_plot(figu, outputfile,maxi,mini,tmax,tmin,station_names):
    plt.gcf().autofmt_xdate()
    plt.xlim(tmin, tmax)
    plt.ylim(mini,maxi)
    plt.legend()
    figu.savefig(outputfile,dpi=100)
    #plt.show()
    plt.close(figu)



####################################################################################################



def main():

    os.chdir(path)



    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)


    #station_list = ["Hamina","Hogland","Sillamae","Kronstadt"]
    station_list=["Hogland"]



    if start_time.strftime("%Y") != end_time.strftime("%Y"):
        years = range(int(start_time.strftime("%Y")),int(end_time.strftime("%Y"))+1)

    for year in years:
        for month in range(1,13):

            figur = plt.figure()
            figur.set_size_inches(14, 8)
            plt.xlabel("Time")
            # plt.ylabel("Sea Level")
            plt.title("Baltic Tide Gauge Sealevels")

            mins = []
            maxes = []
            tmins = []
            tmaxes = []

            for file in glob.glob("*.txt"):                 # Opens all that ends with .txt in the path folder one by one                     # Matches only the needed ones
                for stat in station_list:
                    if fnmatch.fnmatch(file, "*"+stat+"*" ):
                        (sl_variables, station, okey) = open_cmemsfiles(file,year,month)
                        if len(sl_variables)>0:
                            (figur, maxi, mini, tmax, tmin)= process_file(file, sl_variables, station,figur)
                            mins.append(mini)
                            maxes.append(maxi)
                            tmins.append(tmin)
                            tmaxes.append(tmax)

            #time_min=np.min(tmins)

            end_plot(figur, output_path+"plot_hogland_"+str(year)+"_"+str(month)+".png", np.nanmax(maxes), np.nanmin(mins), np.max(tmaxes), np.min(tmins),station_list)




if __name__ == '__main__':
    main()