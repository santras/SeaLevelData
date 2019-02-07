#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy
import math
import time

#from matplotlib.backends.backend_agg import FigureCanvasAgg
#import matplotlib
#matplotlib.use('Agg')

path = "/home/sanna/PycharmProjects/Daily_files/2007/"  # Path for the original data file folder, best not to have anything else
output_path = "/home/sanna/PycharmProjects/Surfaces/TG/2007/"  # than the .txt data file in this directory
time_period_start = datetime.datetime(2007, 1, 1, 0, 0)  # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end = datetime.datetime(2007, 1, 1, 23, 00)
grid_lat_min = 53.98112672        #48.4917 to 65.85825 mid points     # lat width 0.033269252873563214       smaller:58.40593736/53.98112672
grid_lat_max = 65.85825
grid_lat_num = 358         # 523                                                                        smaller:224/314
grid_lon_min = 14.98269705     #9.047926 to 30.124683 mid points   # lon width  0.055465150000000005     smaller:16.813047 / 14.98269705
grid_lon_max = 30.124683
grid_lon_num = 274          #381                                                                        smaller:241 /274
plotting = True  # If True plots each hour to a picture of the surface. Warning, takes long...



# Function 1
def open_rfile(file_name):
    # Called by: get_headers / Function 2,Calls: -
    # Opens a readable file and reads it
    try:
        file = open(file_name, 'r')
        data = file.readlines()
        file.close()
        ok = True
    except:
        print("File {} couldn't be opened in open_rfile/Function1.".format(file_name))
        # Returns empty data variable and False if not successfull
        ok = False
        data = []
        return data, ok

    return data, ok


# Function 3
def get_data(day_time):
    # # Called by: Main, Calls: open_rfile/Funtion1, eval_values /Function 4, write_output / Function 5
    # # Finds data of correct hour and calls eval_values to get the evaluation of sea level in all points then
    # calls write_output to write the hours values into spotly file.

    okey = False

    # Open file of measurements for the correct day
    (data, get_data_success) = open_rfile(day_time.strftime("%d_%m_%Y" + ".txt"))
    if not get_data_success:
        print("Warning, couldn't open file for the date", day_time)
        exit("Exiting program early 1")  # This shouldn't cause problems since all dates should have a a file even if limited data availability

    station = []
    lat = []
    lon = []
    slev = []


    for row in data:
        split_row = row.split()
        if split_row[1].strip() == day_time.strftime("%H" + ":00"):
            if not np.isnan(float(split_row[5].strip())):       #not nan values
                if (int(split_row[6].strip())) in (1,2,8): # good value, probably good value, interpolated
                    station.append(split_row[2].strip())
                    lat.append(float(split_row[3].strip()))
                    lon.append(float(split_row[4].strip()))
                    slev.append(float(split_row[5].strip()))

    if len(slev) > 0:  ## Here later some sort of when good enough estimation... len(slev)>A, bad but workable... etc
        field = eval_values(lat, lon, slev, day_time)
        write_ok = write_output(field, day_time)
        if write_ok:
            okey = True  # TÄMÄ MIETI
        else:
            okey = False
    else:
        print("Problems with the sea level measurements file, not enough measurements.")
        okey = False

    # write - output formating
    # write - coordinate squares and width/height of area + number of squares
    # write - zeros (angle) after values
    # when write success okey=True

    return okey


# Function 4
def eval_values(lat, lon, slev, date):
    # Called by: get_data/Function 3 Calls: -
    # Evaluates sea level in all points
    # field=[]
    # HERE take the plotting code and put it here, test working

    # My grid, grid specs are given as constants after imports in this script
    grid_lat = np.linspace(grid_lat_min, grid_lat_max, num=grid_lat_num)            # grid_lat ="y"
    grid_lon = np.linspace(grid_lon_min, grid_lon_max, num=grid_lon_num)            # grid_lat="x"
    XGRID, YGRID = np.meshgrid(grid_lon, grid_lat)

    # count=0
    # for ind in range(len(grid_lat)):
    #     if grid_lat[ind]>= 53.98112672 :
    #         count=count+1
    #
    # print(grid_lat)
    # print(count)

    #print(slev)
    slev_min = min(slev)
    slev_max = max(slev)

    # Using RBF
    #print(slev)
    rbf = Rbf(lon, lat, slev,function=("thin_plate"))
    ZGRID = rbf(XGRID, YGRID)

    #print(XGRID.shape,YGRID.shape,ZGRID.shape)
    #print(XGRID[0:10,0:10])


    if plotting == True:
        # Basemap from cartopy
        ax = plt.axes(projection=cartopy.crs.PlateCarree())
        plt.pcolor(XGRID, YGRID, ZGRID, cmap=cm.jet, vmin=-30, vmax=110, zorder=1,
                   transform=cartopy.crs.PlateCarree())   # vmin=slev_min, vmax=slev_max
        ax.set_extent([16,31.2,56,66.8]) #([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
        ax.set_title('TG-surface interpolation rbf-thinplate ' + date.strftime("%d.%m.%Y %H:%M"))
        land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face',zorder=2,
                                                       facecolor="white")
                                                       #facecolor=cartopy.feature.COLORS['land'])
        ax.add_feature(land_50m)

        ax.plot(lon, lat, 'bo', markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
        ax.coastlines(resolution='50m', color='black', linewidth=1)

        plt.colorbar(fraction=0.046, pad=0.04)
        plt.savefig(output_path + 'Plots/tg_surf_' + date.strftime('%Ym%d_%H') + '.png')
        plt.close()

    return ZGRID


# Function 5
def write_output(value_field, date):
    # Called by: get_data /Function 3  , Calls: -
    # Writes the output into a file

    write_okey = True
    output_file = output_path + "/SPOTLY_" + date.strftime("%Y%m%d_%H") + ".txt"

    try:
        file = open(output_file, 'w')
        # print(output_file)
    except:
        print("Couldn't open file to print into.")
        write_okey = False
        return write_okey

    file.write('H2O\n')
    file.write('0 0 0 0 0 0\n')
    file.write('{:4.4f}\t0\n'.format(grid_lat_max))
    file.write('{:4.4f}\t0\n'.format(grid_lat_min))
    file.write('{:4.4f}\t0\n'.format(grid_lon_max))
    file.write('{:4.4f}\t0\n'.format(grid_lon_min))
    file.write('{:4.4f}\t0\n'.format(grid_lon_min))
    file.write('{:d}\t\t{:d}\n'.format(grid_lat_num, grid_lon_num))
    file.write('Surface fit: Radial Basis-Thin plate ' + date.strftime("%d.%m.%Y %H:00\n"))

    # print(value_field.shape)
    values = (np.reshape(value_field, (grid_lon_num * grid_lat_num))) * 10  ## Changing the values from cm  to mm
    zz = np.zeros(len(values))  # Adding zeros (phase) to the end of the file
    values = np.append(values, zz)

    full_lines = math.floor(len(values) / 10)

    index = 0
    for ii in range(full_lines):
        for jj in range(9):
            file.write('{:6d}\t'.format(int(values[index])))
            index = index + 1
        file.write('{:6d}\n'.format(int(values[index])))
        index = index + 1
    if full_lines * 10 - len(values) != 0:
        # print(values[full_lines * 10:])  # These are the leftovers
        for kk in range(full_lines * 10, len(values)):
            file.write('{:6d}\n'.format(int(values[index])))
            index = index + 1

    file.close()

    return write_okey


####################################################################################################


def main():
    # Called by: -, Calls:  get_data /Function
    # Use: See readme file
    # print(path)
    os.chdir(path)

    if time_period_end <= time_period_start:
        print("Something went wrong with start time and end time parameter, please check!")
        exit()
    start_time = time_period_start
    end_time = time_period_end
    count = 0

    if not os.path.exists(output_path):  # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)
    if not os.path.exists(output_path + '/Plots'):
        os.makedirs(output_path + '/Plots', exist_ok=True)

    # HERE LOOPING HOURLY
    while end_time >= start_time:
        run_timer_start=time.time()
        (data_found) = get_data(
            start_time)  # Function 3, for opening and processing and writing to file the files for that hour
        if not data_found:
            print("Warning, Couldn't find data on ", start_time)
        run_elapsed = time.time()-run_timer_start
        print('run time: {}'.format(run_elapsed))
        count = count + 1
        start_time = start_time + datetime.timedelta(hours=1)
        # print(start_time)


if __name__ == '__main__':
    main()
