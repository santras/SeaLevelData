#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt

path_model="/home/sanna/PycharmProjects/ModelData/Locations/"
path_tg="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned/"
#path_surf="/home/sanna/PycharmProjects/"
points_list="/home/sanna/PycharmProjects/ModelData/NorthernBaltic_Points_of_Interest.txt"
output_folder="/home/sanna/PycharmProjects/PLOTS/Stations/"

#time_period_start=datetime.datetime(1993,1,1,0,0)
time_period_start=datetime.datetime(2017,1,1,0,0)
time_period_end=datetime.datetime(2017,12,31,23,0)


def make_hist(histodata,name):
    histo=plt.figure()
    ax = histodata.plot(kind="hist", bins=50)
    ax.set_xlabel("Sealevels (EVRF 2007) in cm")
    plt.title(name+" tide gauge data")
    #plt.show()
    plt.savefig(output_folder + 'Histogram_' + name +'.png')

    plt.close(histo)



def make_tseries(data_in,name):
    #tseries = plt.figure()
    start = (data_in.Time.min())
    stop = (data_in.Time.max())
    titlename = name +" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")
    #print(titlename)
    #print(data_in[0]) #.strftime("%Y %m %d"))

    ax = data_in.plot(x="Time",y="Sealevels", label="Sealevels (EVRF) in cm",color="b",linewidth=1)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.get_legend().remove()


    plt.xlim(start, stop) # X limits to actual data limits%
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=18)

    plt.savefig(output_folder + 'Timeseries_' + name + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png')
    #plt.show()
    plt.close()




def get_tg(filename):

    print(filename)
    name=filename[:-4]

    headers = ["Dates", "Times", "Sealevels", "Q-Flags"]

    data = pd.read_csv(filename, skiprows=24, sep="\t", header=None, names=headers, na_values="nan",parse_dates={"Time": ["Dates", "Times"]})
    data.Sealevels = data.Sealevels.apply(lambda x: np.float64(x))  # Changing the types of Sealevels to float

    # Testing that timestamp works
    #for ii in range(len(data.Sealevels)):
    #    try:
    #        data.Timestamp[ii]+datetime.timedelta(seconds=3600)
    #    except:
    #        print("Not datetime?",data.Timestamp[ii])

    #print(data[time_period_start])

    #plt.figure()
    #ax = data.plot(x="Time",y="Sealevels")
    #plt.show()
    #plt.close()

    #print(data.Time[0])



    data_cut=(data.loc[( (data['Time'] >= time_period_start) )] ) # and (data['Time']<=time_period_end) ) ] )
    data_cut=(data_cut.loc[( (data_cut['Time'] <= time_period_end) )] )
    #print(data_cut.keys)
    #print(data_cut.shape)
    #print(data_cut.Sealevels.head)

    #plt.figure()
    #ax = data_cut.plot(x="Time",y="Sealevels")
    #plt.show()
    #plt.close()

    #make_hist(data.Sealevels,name)
    make_tseries(data_cut,name)


    return

def main():
    # Main of plotting timeseries of stations
    #### STEPS:
    ### STEP 2
    # take stations from point list
    # make plot & write -> move to next station
    ### STEP 3
    # comment step 2
    # take model data of 1 station from start-end
    # plot with another colour
    ### STEP 4
    # Uncomment step 2
    # Check that step 3 works with multiple plots at a time
    ### STEP 5
    # comment step 2
    # take surface data of 1 station from start-end
    # plot with third colour
    ### STEP 6
    # uncomment 2
    # check that still works
    ### STEP 7
    # Move plots into google drive
    # Write thoughts of plots
    # github the script

    ### STEP 8
    # Make runs for different time periods

    #NEXT
    ### PLAN SURFACE/MODEL scatterplot to same file/different file with same main
    ### PLAN CORELATION OF SURFACE/MODEL to same file/different file with same main


    if not os.path.exists(output_folder):                             # Making the output folder if needed
        os.makedirs(output_folder, exist_ok=True)

    # Open stations tg-data and get time period
    station="helsinki"



    os.chdir(path_tg)

    for file in glob.glob("*.txt"):
        if file.lower() == station + ".txt":
            namematch = True
            get_tg(file)





    return





if __name__ == '__main__':
    main()
