#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to re-write the station-by-station sealevel files into day by day sealevel files to make the plotting faster

path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt/"                           # Path for the original data file folder, best not to have anything else
output_path= "../Daily_files/Test/"                                             # than the .txt data file in this directory
period_from=datetime.datetime(2007,1,1)
lat_lim=58.7




####################################################################################################



def main():

    os.chdir(path)

    for filename in glob.glob("*txt"):
        file = open(filename, "r")
        data = file.readlines()
        file.close()
        #print(data[0])

        head=[]

        for ii in range(0,24):
            head.append(data[ii])

        for xx in range(len(head)):
            if  head[xx].find("Start")>=0:        # If find successfull, gives index as results, othewise -1
                splitline=(head[xx].strip().split()[2].split("-"))
                start_date = datetime.datetime(int(splitline[0]),int(splitline[1]),int(splitline[2]))

            elif head[xx].find("End")>=0:        # If find successfull, gives index as results, othewise -1
                splitline=(head[xx].strip().split()[2].split("-"))
                end_date = datetime.datetime(int(splitline[0]),int(splitline[1]),int(splitline[2]))

                #print(end_date)
            elif head[xx].find("Lat") >= 0:
                lat =float(head[xx].strip().split()[1])

            elif head[xx].find("Lon") >= 0:
                lon = float(head[xx].strip().split()[1])

            elif head[xx].find("Station") >= 0:
                station = (head[xx].strip().split()[1])
                #print(lat)

        if end_date<=period_from :               # Looking if measurement end date is before the start of our data period
        # print("Not including ", filename)
            continue
        elif lat<=lat_lim:
            #print("Not including ", filename)
            continue
        else:
            print("{:15}{:22.15f}{:22.15f}\t\t{:15}{:15}{:20}".format(station,lat,lon,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"),filename))

                #print(start_date)











if __name__ == '__main__':
    main()
