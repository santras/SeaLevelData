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
time_period_start=datetime.datetime(2016,1,1,0,0)
time_period_end=datetime.datetime(2016,1,10,0,0)


def make_hist(histodata,name):
    histo=plt.figure()
    ax = histodata.plot(kind="hist", bins=50)
    ax.set_xlabel("Sealevels (EVRF 2007) in cm")
    plt.title(name+" tide gauge data")
    #plt.show()
    plt.savefig(output_folder + 'Histogram_' + name +'.png')

    plt.close(histo)



def make_tseries(data_in,name,plotname):
    #tseries = plt.figure()
    start = (data_in.Time.min())
    stop = (data_in.Time.max())
    titlename = plotname +": " +name +" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")
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
    plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=18)

    if plotname == "Tide Gauge Data":
        shortname="tg"
    elif plotname == "Model Data":
        shortname="model"

    plt.savefig(output_folder +shortname+'_' + name + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png')
    #plt.show()
    plt.close()




def get_tg(filename):

    print(filename)
    name=filename[:-4]

    headers = ["Dates", "Times", "Sealevels", "Q-Flags"]

    data = pd.read_csv(filename, skiprows=24, sep="\t", header=None, names=headers, na_values="nan",parse_dates={"Time": ["Dates", "Times"]})
    data.Sealevels = data.Sealevels.apply(lambda x: np.float64(x))  # Changing the types of Sealevels to float

    data_cut=(data.loc[( (data['Time'] >= time_period_start) )] ) # and (data['Time']<=time_period_end) ) ] )
    data_cut=(data_cut.loc[( (data_cut['Time'] <= time_period_end) )] )
    #print(data_cut.keys)
    #print(data_cut.shape)
    #print(data_cut.Sealevels.head)


    #make_hist(data.Sealevels,name)
    plotname="Tide Gauge Data"
    make_tseries(data_cut,name,plotname)


    return data_cut


def get_model(location,station):

    #print((time_period_end-time_period_start).days)
    days_to_do=((time_period_end-time_period_start).days)
    if days_to_do> 31:
        print("Only periods smaller than 1 month for now")
    elif time_period_end.strftime("%m") != time_period_start.strftime("%m"):
        print("Only periods smaller than 1 month for now")


    file_=location+"CMEMS_BAL_PHY_reanalysis_surface_"
    headers = ["Locations","Time","Point_Lat","Point_Lon","Sealevels","M_Latitudes","M_Longitudes"]
    new_data=pd.DataFrame(columns=headers)


    for ind in range(days_to_do):
        file=file_+((time_period_start+datetime.timedelta(days_to_do)).strftime("%Y%m%d"))+".txt"
        #print(file)
        data = pd.read_csv(file,  sep="\t", header=None, names=headers, na_values="nan",
                           parse_dates=["Time"])

        found=False

        #for ind in range(len(data)):
            #print(data.Locations[ind].lower())
            #print(station.lower())
            #if data.Locations[ind].lower().strip() == station.lower().strip():

            #data_cut = (data.loc[(data["Locations"].str.contains("helsinki"))])
        data_cut = data[data["Locations"].str.contains(station[1:])]   #
        if data_cut.empty:
            print("need upper")
            data_cut = data[data["Locations"].str.contains(station[1:].upper())]
            if data_cut.empty:
                print("Not finding match for name ",station)

        print(data_cut)
        new_data=pd.concat([new_data,data_cut])

    print(len(new_data))

    plotname="Model Data"
    make_tseries(new_data, station,plotname)


    return new_data


def main():
    # Main of plotting timeseries of stations
    #### STEPS:
    ### STEP 2
    # take stations from point list
    # make plot & write -> move to next station
    ### STEP 3
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

    # So far can only do 1 month at a time max in finding matching model data
    year_to_get=time_period_start.strftime("%Y")
    month_to_get=time_period_start.strftime("%m")
    path_model_get = path_model+year_to_get+"/"+month_to_get+"/"
    #print(path_model_get)

    #print(year_to_get,month_to_get)

    os.chdir(path_tg)

    for file in glob.glob("*.txt"):
        if file.lower() == station + ".txt":
            namematch = True
            tg_data=get_tg(file)
            model_data=get_model(path_model_get,station)






    return





if __name__ == '__main__':
    main()
