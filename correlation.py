#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt

path_model="/home/sanna/PycharmProjects/ModelData/Locations/"
#path_tg="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned_cut/"
path_surf="/home/sanna/PycharmProjects/Surfaces/TG/"
points_list="/home/sanna/PycharmProjects/NorthernBaltic_Points_of_Interest_cleaned.txt"
output_path="/home/sanna/PycharmProjects/Year_file_resampled/"

#time_period_start=datetime.datetime(1993,1,1,0,0)
time_period_start=datetime.datetime(2015,1,1,0,0)       # Only understands full days
#time_period_end=datetime.datetime(2007,1,31,23,0)
time_period_end=datetime.datetime(2015,12,31,23,0)

grid_lat_min = 53.98112672
grid_lat_max = 65.85825
grid_lat_num = 358
grid_lon_min = 14.98269705
grid_lon_max = 30.124683
grid_lon_num = 274


# 2007,2011,2012,2016
# 2008,2009,2010
# 2013,2014,2015,2016



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
    new_data.Sealevels = new_data.Sealevels.apply(lambda x: np.float64(x))
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
    new_data.Sealevels = new_data.Sealevels.apply(lambda x: np.float64(x))

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


def main():

    # 6. Count monthly by station: correlation and differences (min,max,median, mean)
    # 7. Count by station (whole data set): correlation and differences (min,max,median, mean)
    # 8. Plot by station (whole data set): histogram of difference
    # 9. Count by month (all stations): correlation and differences (min,max,median, mean)
    # 10. Count by month (all stations): histogram of differences
    # 11. Count from all data correlation and differences (min, max, median, mean)
    # 12. Count from all data: histogram of differences

    # Open stations lists
    (station_data, okey) = open_txtfile(points_list)
    if not okey:
        print("Couldn't open file for interest points")
    stations = get_station_list(station_data)

    # Moving to tg-path
    #os.chdir(path_tg)

    # Checking that output folder is made
    output_folder = output_path
    if not os.path.exists(output_folder):  # Making the output folder if needed
        os.makedirs(output_folder, exist_ok=True)


    # Initializing data frames
    indexes = pd.date_range(time_period_start,time_period_end,freq="H")
    mycolumns=["Model_Sealevel","Interp_Sealevel"]


    #data_all={}                 # Dictionary of dataframes by station
    # Going through data with station by station
    for station in stations:
        #data_all[station] = pd.DataFrame(index=indexes,columns=mycolumns)
        #this_station = pd.DataFrame(index=indexes, columns=mycolumns)
        #this_station[:]=np.nan
        #print(station, len(this_station))
        print(station)
        # Year loop
        year_start = int(time_period_start.strftime("%Y"))
        year_end = int(time_period_end.strftime("%Y"))

        years = range(year_start, year_end + 1)
        #print(years)

        # Going through years
        for plot_year in years:                         # copied from plotting script so names a bit silly
                                                        # for example plot_year= year_analysing would be better...
            this_station = pd.DataFrame(index=indexes, columns=mycolumns)
            this_station[:] = np.nan
            print(plot_year)

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

            # Going through months
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
                #print(plot_start,plot_end)

                # I think reference to data frame would be data_all[station].columnname

                # find model data
                month_to_get = plot_start.strftime("%m")
                path_model_get = path_model + str(plot_year) + "/" + month_to_get + "/"
                model_data = get_model(path_model_get, station,plot_start,plot_end)
                if len(model_data) < 1:
                    print("Couldn't find model and surface data on:", station)
                    continue
               # elif tg_found:
               #     if len(model_data) != len(tgdata):
               #         print("Model data not same length as tg-data in:", station, len(tgdata), len(model_data))
               #         exit(1)
                #model_data = check_sldata(model_data)
                model_lat = (model_data.M_Latitudes.values[0])  ## getting model lat and lon for getting the surface value
                model_lon = (model_data.M_Longitudes.values[0])
                #print (model_data.Sealevels.head())

                #data_all[station].loc[model_data.index,"Model_Sealevel"] = model_data.Sealevels
                #print(data_all[station].loc[model_data.index].head())

               # data_all[station].loc(model_data.index,"Model_Sealevel")=model_data.Sealevels
    #
                # find surface data

                path_surf_get = path_surf + str(plot_year) +"_cut/all/"
                surf_data = get_surf(path_surf_get, model_lat, model_lon, station,plot_start,plot_end)
                if len(surf_data) < 1:
                    print("Couldn't find surface data on:", station)
                    continue
               # elif tg_found:
               #     if len(surf_data) != len(tgdata):
                #        print("Surface data not same length as tg-data in:", station, len(tgdata), len(surf_data))
                #        exit(1)

                if len(surf_data) != len(model_data):
                    print("Surface data not same length as model data in:", station, len(tgdata), len(surf_data))
                    exit(1)
                #surf_data = check_sldata(surf_data)
                #print(surf_data.Sealevels.head())

                this_station.loc[surf_data.index,["Interp_Sealevel"]] = surf_data.Sealevels
                this_station.loc[model_data.index,["Model_Sealevel"]] = model_data.Sealevels
                month_corr = surf_data.astype("float64").corrwith(model_data.Sealevels.astype("float64"))
                #print(month_corr)



            this_station["Difference"] = this_station.Interp_Sealevel - this_station.Model_Sealevel
            print("Year_Correlation")
            correlation = (this_station.astype("float64").corr())
            #print(time_period_start.strftime("%d.%m.%Y - "), time_period_end.strftime("%d.%m.%Y"))
            print(correlation)
            stats=(this_station.astype("float64").describe())
            print(stats)
            #print("original")
            #print(this_station.head())
            series_interp = this_station.Interp_Sealevel.astype("float64").resample("4H").mean()
            series_model = this_station.Model_Sealevel.astype("float64").resample("4H").mean()
            #print("new")
            #print(series_interp.head())

            filename=output_folder+station+"_"+str(plot_year)+".txt"
            file = open(filename,"w")
            for ii in range (len(series_interp)):
                file.write("{:20}\t{:10.6}\t{:10.6}\n".format(series_interp.index[ii].strftime("%Y-%m-%d %H:00"),series_interp.values[ii],series_model.values[ii]))

            file.close()

        #this_station["Difference"] = this_station.Interp_Sealevel-this_station.Model_Sealevel
        #correlation=(this_station.astype("float64").corr())
        #print(time_period_start.strftime("%d.%m.%Y - "),time_period_end.strftime("%d.%m.%Y"))
        #print(correlation)
        #stats=this_station.astype("float64").describe()
        #print(stats)




    return





if __name__ == '__main__':
    main()
