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
path_surf="/home/sanna/PycharmProjects/Surfaces/TG/"
points_list="/home/sanna/PycharmProjects/NorthernBaltic_Points_of_Interest_cleaned.txt"
output_folder="/home/sanna/PycharmProjects/PLOTS/Stations/T_Series/2007/"

#time_period_start=datetime.datetime(1993,1,1,0,0)
time_period_start=datetime.datetime(2007,10,1,0,0)       # Only understands full days
time_period_end=datetime.datetime(2007,10,31,23,0)

grid_lat_min = 53.98112672
grid_lat_max = 65.85825
grid_lat_num = 358
grid_lon_min = 14.98269705
grid_lon_max = 30.124683
grid_lon_num = 274



def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened:".format(file_name))   # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok


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
    elif plotname == "Interpolated Surface":
        shortname="int_surf"

    plt.savefig(output_folder +shortname+'_' + name +"_test"+ start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png')
    #plt.show()
    plt.close()

def make_multi_tseries(data,station,tg_boolean):

    plotname="Time Series"
    shortname="tseries"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station.capitalize()+" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")


    fig=plt.figure()
    fig.set_size_inches(14, 8)
    if tg_boolean:
        data.drop(["Q-Flags"],axis=1,inplace=True)


   # testing modelled data
    nancount=0
    for ind in range(len(data)):
        if np.isnan(data.Model_Sealevels.values[ind]):
            a=1
        elif data.Model_Sealevels.values[ind]<350:
            if data.Model_Sealevels.values[ind]>-200:
                a=1
        elif data.Model_Sealevels.values[ind]<1000:
            if data.Model_Sealevels.values[ind]>-500:
                data.Model_Sealevels.values[ind]=np.nan
                nancount=nancount+1
            else:
                print("Problems in modelled data", station, ind, data.index[ind],data.Model_Sealevels.values[ind])
                exit(1)
        else:
            print("Problems in modelled data",station,ind,data.index[ind],data.Model_Sealevels.values[ind])
            exit(1)
    if nancount!=0:
        print("Converting higher/lower model values to nan", nancount)


    ax=plt.plot(data.index,data.Model_Sealevels,color="b",linewidth=2, label="Model Sealevels (floating 0-level)")
    #print("test 1")

    # testing Interpolated data
    nancount=0
    for ind in range(len(data)):
        if np.isnan(data.Interp_Sealevels.values[ind]):
            a=1
        elif data.Interp_Sealevels.values[ind] < 350:
            if data.Interp_Sealevels.values[ind] > -200:
                a = 1
        elif data.Interp_Sealevels.values[ind] <1000:
            if data.Interp_Sealevels.values[ind] >-500:
                data.Interp_Sealevels[ind]=np.nan
                nancount=nancount+1
            else:
                print("Problems in interpolated data", station, ind, data.index[ind],data.Interp_Sealevels.values[ind])
                exit(1)
        else:
            print("Problems in interpolated data", station, ind, data.index[ind],data.Interp_Sealevels.values[ind])
            exit(1)
    if nancount!=0:
        print("Converting higher/lower interpolated values to nan",nancount)

    plt.plot(data.index,data.Interp_Sealevels,color="g",linewidth=2,label="Sealevels Interpolated from Tide Gauge data (in cm EVRF2007)")
    #print("test 2")

    nancount=0
    if tg_boolean:
        # testing tg data
        nancount = 0
        for ind in range(len(data)):
            if np.isnan(data.TG_Sealevels.values[ind]):
                a=1
            elif data.TG_Sealevels.values[ind] < 350:
                if data.TG_Sealevels.values[ind] > -200:
                    a = 1
            elif data.TG_Sealevels.values[ind] < 1000:
                if data.TG_Sealevels.values[ind] >-500:
                    data.TG_Sealevels[ind]=np.nan
                    nancount=nancount+1
                else:
                    print("Problems in tide gauge data", station, ind, data.index[ind],data.TG_Sealevels.values[ind])
                    exit(1)
            else:
                print("Problems in tide gauge data", station, ind, data.index[ind],data.TG_Sealevels.values[ind])
                exit(1)
        if nancount!=0:
            print("Converting higher/lower tg values to nan",nancount)

        plt.plot(data.index, data.TG_Sealevels, color="k", linewidth=1,linestyle="--",label="Tide Gauge Value (in cm EVRF2007)")
        #print("test 3")
    plt.legend(fontsize=12)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=18)



    fig.savefig(output_folder +shortname+'_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()


def get_tg(filename):

    #print(filename)
    name=filename[:-4]

    headers = ["Dates", "Times", "Sealevels", "Q-Flags"]

    data = pd.read_csv(filename, skiprows=24, sep="\t", header=None, names=headers, na_values="nan",parse_dates={"Time": ["Dates", "Times"]},index_col=False)
    data.Sealevels = data.Sealevels.apply(lambda x: np.float64(x))  # Changing the types of Sealevels to float

    #print(type(data))
    #print(data.keys())

    # Indexing dataframe by date
    data=data.set_index('Time')

    data = data[time_period_start:time_period_end]


    # Not tested if works anymore
    #make_hist(data.Sealevels,name)
    #plotname="Tide Gauge Data"
    #make_tseries(data_cut,name,plotname)


    return data


def get_model(location,station):

    #print((time_period_end-time_period_start).days)
    days_to_do=((time_period_end-time_period_start).days)
    if days_to_do> 31:
        print("Only periods smaller than 1 month for now")
    elif time_period_end.strftime("%m") != time_period_start.strftime("%m"):
        print("Only periods smaller than 1 month for now")

    #print(days_to_do)

    filestart=location+"CMEMS_BAL_PHY_reanalysis_surface_"

    headers = ["Locations","Time","Sealevels","M_Latitudes","M_Longitudes"]
    new_data=pd.DataFrame(columns=headers)

    model_latitude = np.nan
    model_longitude = np.nan


    for ind in range(0,days_to_do+1):  ## files are 1 day /file

        file=filestart+((time_period_start+datetime.timedelta(days=ind)).strftime("%Y%m%d"))+".txt"
        #print(file)
        data = pd.read_csv(file,  sep="\t", header=None, usecols=[0,1,4,5,6], names=headers,na_values="nan",
                           parse_dates=["Time"])

        # Finding the matching location
        found=False
        data_cut = data[data["Locations"].str.contains(station[1:])]
        if data_cut.empty:
            #print("need upper")
            data_cut = data[data["Locations"].str.contains(station[1:].upper())]
            if data_cut.empty:
                if (station.strip().lower()) =="kalixstoron":
                    data_cut = data[data["Locations"].str.contains("Kalix-Storon")]
                else:
                    print("Not finding model match for name ",station)
        else:
            found = True



        #print("shape",data.shape)
        #print(data.head())
        #data_cut = data_cut.drop(['Locations',"Point_Lat","Point_Lon","M_Latitudes","M_Longitudes"],axis=1,inplace=True)
        #print("After", data_cut.shape)


        #print(data_cut)
        new_data=pd.concat([new_data,data_cut])

    new_data = new_data.set_index('Time')
    #print(new_data.shape)


    return new_data

def get_surf(location,lat,lon,station):

    days_to_do = ((time_period_end - time_period_start).days)

    if days_to_do > 31:
        print("Only periods smaller than 1 month for now")
    elif time_period_end.strftime("%m") != time_period_start.strftime("%m"):
        print("Only periods smaller than 1 month for now")

    new_data = pd.DataFrame(columns=["Time","Sealevels"])

    lats_surf = np.linspace(grid_lat_min, grid_lat_max, num=grid_lat_num)
    lons_surf = np.linspace(grid_lon_min, grid_lon_max, num=grid_lon_num)

    # Finding the matching indexes for the correct values
    lat_i = []
    lon_i = []
    for lat_ind in range(len(lats_surf)):
        if np.abs((lats_surf[lat_ind])-lat)<=0.0166:
            lat_i = lat_ind
    for lon_ind in range(len(lons_surf)):
        if np.abs((lons_surf[lon_ind])-lon) <=0.0277 :                                              #if np.around(lons_surf[lon_ind], decimals=3) == np.around(lon,decimals=3):
            lon_i = lon_ind

    if lat_i == []:
        print("Something went wrong in get_surf, probably rounding error for lat",lat,station)
    elif lon_i == []:
        print("Something went wrong in get_surf, probably rounding error forr lon",lon,station)
    #else:
    #    print(lat_i,lon_i)
   # print(lons_surf)


    for ind in range(0,days_to_do+1):

        #print("here")
        for ind2 in range(0,24):

            timestamp = time_period_start + datetime.timedelta(days=ind)+datetime.timedelta(seconds=3600*ind2)
            #print(timestamp)

            filename = location+(timestamp.strftime("%Y%m%d_%H")) + ".txt"

            data = pd.read_csv(filename, skiprows=7, sep="\t", header=None, na_values="nan")
            #print(data.shape)
            #print(filename)

            appendoitava = pd.DataFrame({"Time":[timestamp],"Sealevels":[data.values[lat_i,lon_i]]})
            #print(appendoitava.shape)
            new_data=pd.concat([new_data,appendoitava])


    #print(new_data.shape)
    #print(new_data.Time)

    #plotname = "Interpolated Surface"
    #make_tseries(new_data, station, plotname)

    new_data = new_data.set_index('Time')

    #print(new_data.Sealevels.values)

    return new_data


def main():
    # Main of plotting timeseries of stations
    #### STEPS:
    ### STEP 2
    # take stations from point list
    # make plot & write -> move to next station
    ### STEP 3
    # plot with another colour
    ### STEP 5
    # comment step 2
    # plot with third colour

    ### STEP 7
    # Move plots into google drive
    # Write thoughts of plots
    # github the script

    ### STEP 8
    # Make runs for different time periods

    #NEXT
    ### PLAN SURFACE/MODEL scatterplot to same file/different file with same main
    ### PLAN CORELATION OF SURFACE/MODEL to same file/different file with same main


    if (time_period_end-time_period_start)< datetime.timedelta(days=1):
        print("Search for longer timeperiods")
        exit(1)


    if not os.path.exists(output_folder):                             # Making the output folder if needed
        os.makedirs(output_folder, exist_ok=True)

    # Open stations tg-data and get time period
    (data, okey) = open_txtfile(points_list)
    if not okey:
        print("Couldn't open file for interest points")
    #station="Helsinki"

    for line in data:           # Going through all stations
        splitline = line.split()
        station = splitline[0].strip().lower()
        testname = []
        for letter in station:
            if letter != "-":                   # dealing with hypenated name
                if not letter in ("ö","ä","å") :    # dealing with scandinavians
                    testname.append(letter)
                elif letter == "ö":
                    testname.append("o")
                elif letter =="ä" or letter =="å":
                    testname.append("a")
        if testname != []:
            station="".join(testname)

        #station="helsinki"
        print(station)


        # So far can only do 1 month at a time max in finding matching model data
        year_to_get=time_period_start.strftime("%Y")
        month_to_get=time_period_start.strftime("%m")
        month_to_get2=time_period_start.strftime("%-m")
        path_model_get = path_model+year_to_get+"/"+month_to_get+"/"
        path_surf_get = path_surf+year_to_get+"/"+month_to_get2+"/"
        #print(path_model_get)
        #print(path_surf_get)

        #print(year_to_get,month_to_get)

        os.chdir(path_tg)
        namematch = False

        #if station.lower() in ["paldiski"]:  #["rauma","paldiski","porvoo"]
        #    continue

        for file in glob.glob("*.txt"):
            if file.lower() == station + ".txt":
                namematch = True

                # gets and checks tg data
                data = get_tg(file)
                if len(data)<1:
                    print("Couldn't find tg data on:",station)
                    continue

                # gets and checks model data
                model_data=get_model(path_model_get,station)
                if len(model_data)<1:
                    print("Couldn't find model data on:",station)
                    continue
                elif len(model_data)!=len(data):
                    print("Model data not same length as tg-data in:",station,len(data),len(model_data))
                    exit(1)

                model_data=model_data.rename(columns={"Sealevels":"Model_Sealevels"})
                model_lat = (model_data.M_Latitudes.values[0])  ## getting model lat and lon for getting the surface value
                model_lon = (model_data.M_Longitudes.values[0])
                model_data.drop(["Locations","M_Latitudes","M_Longitudes"],axis=1,inplace=True)

                #gets and checks surf data
                surf_data = get_surf(path_surf_get,model_lat,model_lon,station)
                if len(surf_data)<1:
                    print("Couldn't find surface data on:",station)
                    continue
                elif len(surf_data)!=len(data):
                    print("Surface data not same length as tg-data in:",station,len(data),len(surf_data))
                    exit(1)

                surf_data=surf_data.rename(columns={"Sealevels":"Interp_Sealevels"})
                data["Model_Sealevels"]=model_data.Model_Sealevels
                data["Interp_Sealevels"]=surf_data.Interp_Sealevels
                data = data.rename(columns={"Sealevels": "TG_Sealevels"})

                #plot
               # print(len(data),len(model_data),len(surf_data),surf_data.shape,surf_data.keys())
                #print(surf_data.Interp_Sealevels.values)
                make_multi_tseries(data,station,namematch) #(tg_data,model_data,surf_data,station)

        if not namematch:
            print("Not finding match with tg-data for",station)
            # if station in ("perameri","pohjanlahti","suomenlahti") :
            #     data = get_model(path_model_get, station)
            #     #print("1",data.shape,data.keys())
            #     model_lat = (data.M_Latitudes.values[0])  ## getting model lat and lon for getting the surface value
            #     model_lon = (data.M_Longitudes.values[0])
            #     data.drop(["Locations", "M_Latitudes", "M_Longitudes"], axis=1, inplace=True)
            #     #print("2",data.shape,data.keys())
            #     surf_data = get_surf(path_surf_get, model_lat, model_lon, station)
            #     #print("3",surf_data.shape,surf_data.keys())
            #     surf_data=surf_data.rename(columns={"Sealevels": "Interp_Sealevels"})
            #     #print("4",surf_data.shape,surf_data.keys())
            #     data["Interp_Sealevels"] = surf_data.Interp_Sealevels
            #     #print("5",data.shape,data.keys())
            #     data = data.rename(columns={"Sealevels": "Model_Sealevels"})
            #     #print("6",data.shape,data.keys())
            #     make_multi_tseries(data, station,namematch)
    return





if __name__ == '__main__':
    main()
