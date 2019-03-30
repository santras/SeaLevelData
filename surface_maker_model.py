#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import numpy.ma as ma
import os, glob
from scipy import stats
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy
import math
import time
from netCDF4 import Dataset
import pandas as pd

#from matplotlib.backends.backend_agg import FigureCanvasAgg
#import matplotlib
#matplotlib.use('Agg')

path ="/home/sanna/PycharmProjects/ModelData/NEMO/2007/07/"  # Path for the original data file folder, best not to have anything else
output_path = "/home/sanna/PycharmProjects/Surfaces/Model/2007/"  # than the .txt data file in this directory
interpolation_path="/home/sanna/PycharmProjects/Surfaces/TG/2007_cut/all/"
time_period_start = datetime.datetime(2007, 7, 31, 0, 0)  # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
days_to_plot=1
#time_period_end = datetime.datetime(2007, 1, 1, 1, 00)
#grid_lat_min = 53.98112672        #48.4917 to 65.85825 mid points     # lat width 0.033269252873563214       smaller:58.40593736/53.98112672
#grid_lat_max = 65.85825
#grid_lat_num = 358         # 523                                                                        smaller:224/314
#grid_lon_min = 14.98269705     #9.047926 to 30.124683 mid points   # lon width  0.055465150000000005     smaller:16.813047 / 14.98269705
#grid_lon_max = 30.124683
#grid_lon_num = 274          #381                                                                        smaller:241 /274
plot_model=True
surf_minus_model = False


#2007
#2011
#2012
#2016

def open_txtfile(file_name):

    # Opens a readable file and reads it
    try:
        file = open(file_name, 'r')
        data = file.readlines()
        file.close()
        ok = True
    except:
        print("File {} couldn't be opened:".format(file_name))
        # Returns empty data variable and False if not successfull
        ok = False
        data = []
        return data, ok

    return data, ok

def get_surf_data(day_time,hh):
    if hh<=9:
        hours="0"+str(hh)
    else:
        hours=str(hh)
    file=interpolation_path+day_time.strftime("%Y%m%d_"+hours+".txt")

    #open_txtfile(file)
    data = pd.read_csv(file, skiprows=7, sep="\t", header=None, na_values="nan")
    #print(data.shape)

    return data

def get_data(day_time):

    # Open file of measurements for the correct day
    # Data: CMEMS_BAL_PHY_reanalysis_surface_20070101.nc

    file=("CMEMS_BAL_PHY_reanalysis_surface_"+day_time.strftime("%Y%m%d") + ".nc")
    try:
        nc_data = Dataset(file, 'r')
        lat = ma.masked_array(nc_data.variables['latitude'][:])
        lon = ma.masked_array(nc_data.variables['longitude'][:])
        sealev = ma.masked_array(nc_data.variables['sla'][:])


        sealev.mask = ma.nomask  ## no mask makes masked nans
        sealev = sealev[:]*100 # to cm
        lat.mask = ma.nomask
        lon.mask = ma.nomask
        okey = True


    except:
        okey = False
        return okey, file, [], [], []

    #print(sealev.shape)
    for hh in range(0, 24):
        # print(sealev[hh][:][:].shape)
        # print(day_time)
        if plot_model == True:
            plot_surf(day_time + datetime.timedelta(seconds=(3600 * hh)), lat, lon, sealev[hh][:][:])

        if surf_minus_model == True:
            surf_data = get_surf_data(day_time,hh)
            #print(sealev.shape)
            #print((sealev[hh][:][:]).shape)
            model_sealev = sealev[hh][:][:]
            model_sealev = model_sealev[165:523,106:381]
            difference=np.empty((358,275),dtype=float)
            difference[:]=np.nan
            for lat_ind in range(0,358):
                for lon_ind in range(0,275):
                    if not (np.isnan(model_sealev[lat_ind,lon_ind])):
                        if not (np.isnan(surf_data.values[lat_ind,lon_ind])):
                            difference[lat_ind,lon_ind]=surf_data.values[lat_ind,lon_ind]-(model_sealev[lat_ind,lon_ind])

            lat_new=lat[165:523]
            lon_new=lon[106:381]
            #print(np.nanmax(difference),np.nanmin(difference),np.percentile(difference,[10,50,90]))
            plot_diff_surf(day_time + datetime.timedelta(seconds=(3600 * hh)), lat_new, lon_new, difference)



    return okey,file,lat,lon,sealev



def plot_surf(date,lat, lon, slev):

   # Basemap from cartopy

    #slev_min=np.nanmin(slev)
    #slev_max=np.nanmax(slev)
    #print(slev_min,slev_max)
    #print(lat.shape,lon.shape,slev.shape)

    ax = plt.axes(projection=cartopy.crs.PlateCarree())
    plt.pcolor(lon, lat, slev, cmap=cm.jet, vmin=-20,vmax=100, zorder=1, transform=cartopy.crs.PlateCarree())   # vmin=slev_min, vmax=slev_max
    ax.set_extent([16, 31.2, 58, 66.8]) #([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
    ax.set_title('NEMO Sea Levels ' + date.strftime("%d.%m.%Y %H:%M"),fontsize=14)
    #land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face', zorder=2,facecolor=cartopy.feature.COLORS['land'])
    #ax.add_feature(land_50m)

    #ax.plot(lon, lat, 'bo', markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
    #ax.coastlines(resolution='50m', color='black', linewidth=1)

    plt.colorbar(fraction=0.046, pad=0.04,extend="both")
    plt.savefig(output_path + 'model_surf_' + date.strftime('%Y%m%d_%H') + '.png')
    plt.close()


def plot_diff_surf(date,lat, lon, slev):

   # Basemap from cartopy

    #slev_min=np.nanmin(slev)
    #slev_max=np.nanmax(slev)
    #print(slev_min,slev_max)
    #print(lat.shape,lon.shape,slev.shape)

    ax = plt.axes(projection=cartopy.crs.PlateCarree())
    plt.pcolor(lon, lat, slev, cmap=cm.jet, vmin=-30,vmax=50, zorder=1, transform=cartopy.crs.PlateCarree())   # vmin=slev_min, vmax=slev_max
    ax.set_extent([16, 31.2, 58, 66.8]) #([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
    ax.set_title("Diff:surf-model test -30,50",fontsize=14)
    #land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face', zorder=2,facecolor=cartopy.feature.COLORS['land'])
    #ax.add_feature(land_50m)

    #ax.plot(lon, lat, 'bo', markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
    #ax.coastlines(resolution='50m', color='black', linewidth=1)

    plt.colorbar(fraction=0.046, pad=0.04,extend="both")
    plt.savefig(output_path + "substraction/"+ 'difference' + date.strftime('%Y%m%d_%H') + '.png')
    plt.close()

####################################################################################################


def main():


    ### ONLY WORKS IF MONTH GIVEN IN PATH... need to loop the month

    os.chdir(path)

    #if time_period_end <= time_period_start:
    #    print("Something went wrong with start time and end time parameter, please check!")
    #    exit()
    start_time = time_period_start
    #end_time = time_period_end
    count = 0

    if not os.path.exists(output_path):  # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)
    if not os.path.exists(output_path+"substraction/"):
        os.makedirs(output_path+"substraction/", exist_ok=True)

    # HERE LOOPING HOURLY
    for ii in range(0,days_to_plot):
        run_timer_start=time.time()
        (data_found,filename,lat,lon,sealev) = get_data(
            start_time)
        if not data_found:
            print("Warning, Couldn't find data on ", filename)
        run_elapsed = time.time()-run_timer_start
        print('run time: {}'.format(run_elapsed))
        count = count + 1
        start_time = start_time + datetime.timedelta(hours=24)
        # print(start_time)


if __name__ == '__main__':
    main()
