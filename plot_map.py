#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import numpy.ma as ma       # Masked arrays
import os, glob
from netCDF4 import Dataset
from geopy import distance as gd
import matplotlib.pyplot as plt
import cartopy



interest_points=("/home/sanna/PycharmProjects/NorthernBaltic_Points_of_Interest_cleaned.txt")
output_path= "/home/sanna/PycharmProjects/PLOTS/Maps/"      # Outputpath
stations_folder = "/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned/"



# large_lat_min = 48.4917
# large_lat_max = 65.85825
# large_lat_num = 523
#
# large_lon_min = 9.047926
# large_lon_max = 30.124683
# large_lon_num = 381
#
# grid_lat_min = 53.98112672
# grid_lat_max = 65.85825
# grid_lat_num = 358
# #
# grid_lon_min = 14.98269705
# grid_lon_max = 30.124683
# grid_lon_num = 274


def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        file.close()
        ok=True
    except: # Returns empty data variable and False if not successfull
        print("File {} couldn't be opened: ".format(file_name))
        ok=False
        data=[]
        return data,ok

    return data, ok



def small_map(p_names, p_lat,p_lon):

    # Basemap from cartopy
    fig = plt.figure()
    fig.set_size_inches(14, 8)

    ax = plt.axes(projection=cartopy.crs.PlateCarree())
    ax.set_extent([16, 31.2, 56, 66.8])  # ([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
    ax.set_title('Tide Gauge Stations', fontsize=18)
    land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face', zorder=2,
                                                   facecolor="white")

    ocean_50m = cartopy.feature.NaturalEarthFeature('physical', 'ocean', '50m', edgecolor='face', zorder=1,
                                                    facecolor="cornflowerblue")
    # facecolor=cartopy.feature.COLORS['land'])
    ax.add_feature(land_50m)
    ax.add_feature(ocean_50m)

    for ind in range(len(p_names)):
        ax.plot(p_lon[ind], p_lat[ind], "ko", markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
        if not (p_names[ind] in ["Kemi", "Helsinki", "Rohukula", "Kalix-Storon", "Paldiski", "Stockholm", "Heltermaa",
                                 "Lehtma", "Degerby", "Tallinn", "Kronstadt"]):
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] + 0.1, p_lat[ind] - 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Kalix-Storon":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.4, p_lat[ind] - 0.3),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Kemi":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] + 0.1, p_lat[ind] + 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Helsinki":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.8, p_lat[ind] + 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Tallinn":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.4, p_lat[ind] + 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Rohukula":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind], p_lat[ind] - 0.2),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Paldiski":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind], p_lat[ind] - 0.3),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Stockholm":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 2, p_lat[ind] - 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Heltermaa":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 1.5, p_lat[ind] - 0.3),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Lehtma":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.5, p_lat[ind] + 0.1),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Degerby":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.5, p_lat[ind] - 0.3),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        elif p_names[ind] == "Kronstadt":
            plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]), xytext=(p_lon[ind] - 0.5, p_lat[ind] - 0.3),
                         transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
        else:
            print(p_names[ind])

    # plt.legend(fontsize=12)

    # ax.coastlines(resolution='50m', color='black', linewidth=1)

    plt.savefig(output_path + 'map_smaller.png', dpi=100)
    plt.close()



    return



def big_area():

    os.chdir(stations_folder)

    aq0=0; aq1=0; aq2=0; aq3=0; aq4=0; aq5=0; aq6=0; aq7=0; aq8=0;
    atot=0
    stations = []
    lats = []
    lons = []

    for file in glob.glob("*.txt"):
        (data,ok)= open_txtfile(file)
        q0 = 0; q1 = 0; q2 = 0; q3 = 0; q4 = 0; q5 = 0; q6 = 0; q7 = 0; q8 = 0;

        if not ok:
            print("Not including file, problems opening:",file)
        else:
            for line in data[0:22]:
                splitline=line.split()
                if splitline[0] == "Station":
                    station = splitline[1]
                elif splitline[0]=="Longitude":
                    lon = float(splitline[1])
                elif splitline[0] == "Latitude":
                    lat = float(splitline[1])
                elif splitline[0] == "Start":
                    starttime = splitline[2]+" "+splitline[3]
                elif splitline[0] == "End":
                    endtime = splitline[2] + " "+splitline[3]
                elif splitline[0] =="Total":
                    tot = int(splitline[2])
                elif splitline[0] =="0":
                    q0 = int(splitline[4])
                elif splitline[0] =="1":
                    q1 = int(splitline[2])
                elif splitline[0] == "2":
                    q2 = int(splitline[3])
                elif splitline[0] =="3":
                    q3 = int(splitline[4])
                elif splitline[0] =="4":
                    q4 = int(splitline[3])
                elif splitline[0] =="5":
                    q5 = int(splitline[3])
                elif splitline[0] =="6":
                    q6 = int(splitline[3])
                elif splitline[0] =="7":
                    q7 = int(splitline[3])
                elif splitline[0] =="8":
                    q8 = int(splitline[2])
                elif splitline[0] =="9":
                    q9 = int(splitline[3])

            if tot == 0:
                print("Empty file for station",station)
                continue


            # print(station,lat,lon,starttime,endtime)
            # print("Total",tot)
            # print("Q-0", (q0 / tot) * 100)
            # print("Q-1", (q1 / tot) * 100)
            # print("Q-2", (q2 / tot) * 100)
            # print("Q-3", (q3 / tot) * 100)
            # print("Q-4", (q4 / tot) * 100)
            # print("Q-5", (q5 / tot) * 100)
            # print("Q-6", (q6 / tot) * 100)
            # print("Q-7", (q7 / tot) * 100)
            # print("Q-8", (q8 / tot) * 100)

            stations.append(station)
            lats.append(lat)
            lons.append(lon)
            atot=atot+tot
            aq0 = aq0 + q0
            aq1 = aq1 + q1
            aq2 = aq2 + q2
            aq3 = aq3 + q3
            aq4 = aq4 + q4
            aq5 = aq5 + q5
            aq6 = aq6 + q6
            aq7 = aq7 + q7
            aq8 = aq8 + q8


    big_area_map(stations,lats,lons)

    # print("All stations")
    # print("Total:",atot)
    # print("AQ-0", (q0 / tot) * 100)
    # print("AQ-1", (q1 / tot) * 100)
    # print("AQ-2", (q2 / tot) * 100)
    # print("AQ-3", (q3 / tot) * 100)
    # print("AQ-4", (q4 / tot) * 100)
    # print("AQ-5", (q5 / tot) * 100)
    # print("AQ-6", (q6 / tot) * 100)
    # print("AQ-7", (q7 / tot) * 100)
    # print("AQ-8", (q8 / tot) * 100)



    return


def big_area_map(p_names,p_lat,p_lon):
    # Basemap from cartopy
    fig = plt.figure()
    fig.set_size_inches(14, 8)

    ax = plt.axes(projection=cartopy.crs.PlateCarree())
    ax.set_extent([9.20, 31, 53.4, 66.2])  # ([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
    ax.set_title('Tide Gauge Stations', fontsize=18)
    land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face', zorder=2,
                                                   facecolor="white")

    ocean_50m = cartopy.feature.NaturalEarthFeature('physical', 'ocean', '50m', edgecolor='face', zorder=1,
                                                    facecolor="cornflowerblue")
    # facecolor=cartopy.feature.COLORS['land'])
    ax.add_feature(land_50m)
    ax.add_feature(ocean_50m)

    for ind in range(len(p_lon)):
        ax.plot(p_lon[ind], p_lat[ind], "ko", markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
        #plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]),transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=6)

    plt.savefig(output_path + 'map_larger.png', dpi=100)
    plt.close()
    return

def data_points_map():
    # Basemap from cartopy
    Perameri = [65.0,23.0]
    Pohjanlahti = [62.0,19.2]
    Suomenlahti = [59.9,25.0]
    fig = plt.figure()
    fig.set_size_inches(8, 6)

    ax = plt.axes(projection=cartopy.crs.PlateCarree())
    ax.set_extent([16, 31.2, 56, 66.8])  # ([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
    #ax.set_title('', fontsize=18)
    land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face', zorder=2,
                                                   facecolor="white")

    ocean_50m = cartopy.feature.NaturalEarthFeature('physical', 'ocean', '50m', edgecolor='face', zorder=1,
                                                    facecolor="cornflowerblue")
    # facecolor=cartopy.feature.COLORS['land'])
    ax.add_feature(land_50m)
    ax.add_feature(ocean_50m)

    ax.plot(23.0,65.0, "ko", markersize=10, transform=cartopy.crs.Geodetic(), zorder=3)
    plt.annotate("Bay of Bothnia", (23.0-1.5,65.0-0.8),transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
    ax.plot(19.2,62.0, "ko", markersize=10, transform=cartopy.crs.Geodetic(), zorder=3)
    plt.annotate("Bothnian Sea",(19.2-1.1,62.0-0.8), transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)
    ax.plot(25,59.9, "ko", markersize=10, transform=cartopy.crs.Geodetic(), zorder=3)
    plt.annotate("Gulf of Finland", (25+0.5,59.9-0.1,), transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=14)

        # plt.annotate(p_names[ind], (p_lon[ind], p_lat[ind]),transform=cartopy.crs.Geodetic(), color="k", zorder=4, fontsize=6)

    plt.savefig(output_path + 'map_points.png', dpi=100)
    plt.close()

    return

####################################################################################################



def main():

    # Making outputfolder
    if not os.path.exists(output_path):  # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)




    # Opening interest points
    (data,okey)=open_txtfile(interest_points)

    if not okey:
        print("Not finding a file of interest points. ",interest_points)

    p_names=[]                      # point names
    p_lat=[]                        # point lat
    p_lon=[]                        # pont lon

    for ii in range(len(data)):         # Plotting only tide gauges
        if ii>2:
            p_names.append(data[ii].split()[0].strip())
            p_lat.append(float(data[ii].split()[1].strip()))
            p_lon.append(float(data[ii].split()[2].strip()))

    #for ii in range(len(p_names)):
    #    print(p_names[ii])

    #small_map(p_names,p_lat,p_lon)
    #big_area()
    data_points_map()



if __name__ == '__main__':
    main()
