#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt

path_model="/home/sanna/PycharmProjects/ModelData/Locations/"
path_tg="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned_cut/"
path_surf="/home/sanna/PycharmProjects/Surfaces/TG/"
points_list="/home/sanna/PycharmProjects/NorthernBaltic_Points_of_Interest_cleaned.txt"
output_path="/home/sanna/PycharmProjects/PLOTS/Stations/T_Series/"

#time_period_start=datetime.datetime(1993,1,1,0,0)
time_period_start=datetime.datetime(2007,1,1,0,0)       # Only understands full days
time_period_end=datetime.datetime(2016,12,31,23,0)

grid_lat_min = 53.98112672
grid_lat_max = 65.85825
grid_lat_num = 358
grid_lon_min = 14.98269705
grid_lon_max = 30.124683
grid_lon_num = 274

check_limit_min = -500
check_limit_max = 500



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

def make_multi_tseries(data,station,tg_boolean,outputfolder):

    plotname="Time Series"
    shortname="tseries"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station.capitalize()+" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")


    fig=plt.figure()
    fig.set_size_inches(14, 8)
    #if tg_boolean:
    #    data.drop(["Q-Flags"],axis=1,inplace=True)


   # testing modelled data
   #  nancount=0
   #  for ind in range(len(data)):
   #      if np.isnan(data.Model_Sealevels.values[ind]):
   #          a=1
   #      elif data.Model_Sealevels.values[ind]<350:
   #          if data.Model_Sealevels.values[ind]>-200:
   #              a=1
   #      elif data.Model_Sealevels.values[ind]<1000:
   #          if data.Model_Sealevels.values[ind]>-500:
   #              data.Model_Sealevels.values[ind]=np.nan
   #              nancount=nancount+1
   #          else:
   #              print("Problems in modelled data", station, ind, data.index[ind],data.Model_Sealevels.values[ind])
   #              exit(1)
   #      else:
   #          print("Problems in modelled data",station,ind,data.index[ind],data.Model_Sealevels.values[ind])
   #          exit(1)
   #  if nancount!=0:
   #      print("Converting higher/lower model values to nan", nancount)


    ax=plt.plot(data.index,data.Model_Sealevels,color="b",linewidth=2, label="NEMO-Nordic")
    #print("test 1")

    # testing Interpolated data
    # nancount=0
    # for ind in range(len(data)):
    #     if np.isnan(data.Interp_Sealevels.values[ind]):
    #         a=1
    #     elif data.Interp_Sealevels.values[ind] < 350:
    #         if data.Interp_Sealevels.values[ind] > -200:
    #             a = 1
    #     elif data.Interp_Sealevels.values[ind] <1000:
    #         if data.Interp_Sealevels.values[ind] >-500:
    #             data.Interp_Sealevels[ind]=np.nan
    #             nancount=nancount+1
    #         else:
    #             print("Problems in interpolated data", station, ind, data.index[ind],data.Interp_Sealevels.values[ind])
    #             exit(1)
    #     else:
    #         print("Problems in interpolated data", station, ind, data.index[ind],data.Interp_Sealevels.values[ind])
    #         exit(1)
    # if nancount!=0:
    #     print("Converting higher/lower interpolated values to nan",nancount)

    plt.plot(data.index,data.Interp_Sealevels,color="g",linewidth=2,label="Interpolation from tide gauge data")
    #print("test 2")

    # nancount=0
    # if tg_boolean:
    #     # testing tg data
    #     nancount = 0
    #     for ind in range(len(data)):
    #         if np.isnan(data.TG_Sealevels.values[ind]):
    #             a=1
    #         elif data.TG_Sealevels.values[ind] < 350:
    #             if data.TG_Sealevels.values[ind] > -200:
    #                 a = 1
    #         elif data.TG_Sealevels.values[ind] < 1000:
    #             if data.TG_Sealevels.values[ind] >-500:
    #                 data.TG_Sealevels[ind]=np.nan
    #                 nancount=nancount+1
    #             else:
    #                 print("Problems in tide gauge data", station, ind, data.index[ind],data.TG_Sealevels.values[ind])
    #                 exit(1)
    #         else:
    #             print("Problems in tide gauge data", station, ind, data.index[ind],data.TG_Sealevels.values[ind])
    #             exit(1)
    #     if nancount!=0:
    #         print("Converting higher/lower tg values to nan",nancount)
    if tg_boolean:
        plt.plot(data.index, data.TG_Sealevels, color="k", linewidth=1,linestyle="--",label="Tide gauge measurements")
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
    plt.ylabel("Sea Surface height (cm)",fontsize=14)



    fig.savefig(outputfolder +shortname+'_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()


def get_tg(filename,plot_start,plot_end):

    #print(filename)
    name=filename[:-4]

    headers = ["Dates", "Times", "Sealevels", "Q-Flags"]

    data = pd.read_csv(filename, skiprows=24, sep="\t", header=None, names=headers, na_values="nan",parse_dates={"Time": ["Dates", "Times"]},index_col=False)
    data.Sealevels = data.Sealevels.apply(lambda x: np.float64(x))  # Changing the types of Sealevels to float

    #print(type(data))
    #print(data.keys())

    # Indexing dataframe by date
    data=data.set_index('Time')

    data = data[plot_start:plot_end]


    return data


def get_model(location,station,plot_start,plot_end):

    #print((plot_end-plot_start).days)
    days_to_do=((plot_end-plot_start).days)
    if days_to_do> 31:
        print("Only periods smaller than 1 month for now")
    elif plot_end.strftime("%m") != plot_start.strftime("%m"):
        print("Only periods smaller than 1 month for now")

    #print(days_to_do)

    filestart=location+"CMEMS_BAL_PHY_reanalysis_surface_"

    headers = ["Locations","Time","Sealevels","M_Latitudes","M_Longitudes"]
    new_data=pd.DataFrame(columns=headers)

    model_latitude = np.nan
    model_longitude = np.nan


    for ind in range(0,days_to_do+1):  ## files are 1 day /file

        file=filestart+((plot_start+datetime.timedelta(days=ind)).strftime("%Y%m%d"))+".txt"
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

def get_surf(location,lat,lon,station,plot_start,plot_end):

    days_to_do = ((plot_end - plot_start).days)

    if days_to_do > 31:
        print("Only periods smaller than 1 month for now")
    elif plot_end.strftime("%m") != plot_start.strftime("%m"):
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

            timestamp = plot_start + datetime.timedelta(days=ind)+datetime.timedelta(seconds=3600*ind2)
            #print(timestamp)

            filename = location+(timestamp.strftime("%Y%m%d_%H")) + ".txt"

            data = pd.read_csv(filename, skiprows=7, sep="\t", header=None, na_values="nan")
            #print(data.shape)
            #print(filename)

            appendoitava = pd.DataFrame({"Time":[timestamp],"Sealevels":[data.values[lat_i,lon_i]]})
            #print(appendoitava.shape)
            new_data=pd.concat([new_data,appendoitava])


    new_data = new_data.set_index('Time')

    #print(new_data.Sealevels.values)

    return new_data


def get_station_list(data):

    stations=[]

    for line in data:  # Going through all stations
        splitline = line.split()
        station = splitline[0].strip().lower()
        testname = []
        for letter in station:
            if letter != "-":  # dealing with hypenated name (leaving away hypenation, making ä->a etc.)
                if not letter in ("ö", "ä", "å"):  # dealing with scandinavians
                    testname.append(letter)
                elif letter == "ö":
                    testname.append("o")
                elif letter == "ä" or letter == "å":
                    testname.append("a")
        if testname != []:
            stations.append( "".join(testname))

    return stations

def check_sldata(data):

    nancount = 0
    for ind in range(len(data.values)):
        if data.Sealevels.values[ind]>check_limit_max:
            data.Sealevels.values[ind] = np.nan
            nancount = nancount +1
        elif data.Sealevels.values[ind]<check_limit_min:
            data.Sealevels.values[ind] = np.nan
            nancount = nancount + 1

    if nancount != 0:
        print("Changed values over/under the max check limit to nan: ",nancount)

    return data

def main():
    # Main of plotting timeseries of stations

    if (time_period_end-time_period_start)< datetime.timedelta(days=1):   # Time periods for longer than 1 day
        print("Search for longer timeperiods")
        exit(1)

    # Open stations lists
    (station_data, okey) = open_txtfile(points_list)
    if not okey:
        print("Couldn't open file for interest points")
    stations = get_station_list(station_data)

    # Moving to tg-path
    os.chdir(path_tg)

    # Going through all interest points (stations + 3 points)
    for station in stations:

        print(station)
        # Year loop
        year_start = int(time_period_start.strftime("%Y"))
        year_end = int(time_period_end.strftime("%Y"))

        years = range(year_start, year_end + 1)
        #print(years)


        for plot_year in years:

            output_folder = output_path + station + "_" + str(plot_year) + "/"
            if not os.path.exists(output_folder):  # Making the output folder if needed
                os.makedirs(output_folder, exist_ok=True)

            if plot_year == years[0]:
                first_year = True
            else:
                first_year = False
            if plot_year == years[-1]:
                last_year = True
            else:
                last_year = False

            # To loop plotting 1 month a time
            if first_year:
                month_start = int(time_period_start.strftime("%-m"))
            else:
                month_start = 1
            if last_year :
                month_end = int(time_period_end.strftime("%-m"))
            else:
                month_end = 12
            months = range(month_start,month_end+1)
            #print(months)

            for month in months:

                # define plotting start - end
                if (first_year and month == months[0] ):
                    plot_start = time_period_start
                else:
                    plot_start = datetime.datetime(plot_year,month,1,0)


                if (last_year and month == months[-1]):
                    plot_end = time_period_end
                else:
                    if month in [1,3,5,7,8,10,12]:
                        plot_end = datetime.datetime(plot_year,month,31,23)
                    elif month == 2:
                        if plot_year in [2008,2016]:
                            plot_end = datetime.datetime(plot_year, month, 29, 23)
                        else:
                            plot_end = datetime.datetime(plot_year,month,28,23)
                    else:
                        plot_end = datetime.datetime(plot_year,month,30,23)
                print(plot_start,plot_end)
                #continue                                ################################# for testing the time loop

                # find tg data
                tgdata = []
                tg_found = False
                for file in glob.glob("*.txt"):  # Looks for matching file
                    if file.lower() == station + ".txt":
                        tg_found = True
                        tgdata = get_tg(file, plot_start, plot_end)
                        if len(tgdata) < 1:
                            tg_found = False
                        else:
                            tgdata = check_sldata(tgdata)

                if not tg_found:
                    if station not in ["perameri", "pohjanlahti", "suomenlahti"]:
                        print("Coudn't find tide gauge data for station", station)

                # find model data
                month_to_get = plot_start.strftime("%m")
                path_model_get = path_model + str(plot_year) + "/" + month_to_get + "/"
                model_data = get_model(path_model_get, station,plot_start,plot_end)
                if len(model_data) < 1:
                    print("Couldn't find model and surface data on:", station)
                    continue
                elif tg_found:
                    if len(model_data) != len(tgdata):
                        print("Model data not same length as tg-data in:", station, len(tgdata), len(model_data))
                        exit(1)
                model_data = check_sldata(model_data)
                model_lat = (model_data.M_Latitudes.values[0])  ## getting model lat and lon for getting the surface value
                model_lon = (model_data.M_Longitudes.values[0])

                # find surface data

                path_surf_get = path_surf + str(plot_year) +"_cut/all/"
                surf_data = get_surf(path_surf_get, model_lat, model_lon, station,plot_start,plot_end)
                if len(surf_data) < 1:
                    print("Couldn't find surface data on:", station)
                    continue
                elif tg_found:
                    if len(surf_data) != len(tgdata):
                        print("Surface data not same length as tg-data in:", station, len(tgdata), len(surf_data))
                        exit(1)

                if len(surf_data) != len(model_data):
                    print("Surface data not same length as model data in:", station, len(tgdata), len(surf_data))
                    exit(1)
                surf_data = check_sldata(surf_data)


                # renaming columns and joining data frames into 1 dataframe for plotting
                model_data = model_data.rename(columns={"Sealevels": "Model_Sealevels"})
                model_data.drop(["Locations", "M_Latitudes", "M_Longitudes"], axis=1, inplace=True)

                surf_data = surf_data.rename(columns={"Sealevels": "Interp_Sealevels"})

                # Surface is the main data frame to wich others join
                surf_data["Model_Sealevels"] = model_data.Model_Sealevels

                if tg_found:
                    tgdata = tgdata.rename(columns={"Sealevels": "TG_Sealevels"})
                    surf_data["TG_Sealevels"] = tgdata.TG_Sealevels


                make_multi_tseries(surf_data,station,tg_found,output_folder) #(tg_data,model_data,surf_data,station)

    return





if __name__ == '__main__':
    main()
