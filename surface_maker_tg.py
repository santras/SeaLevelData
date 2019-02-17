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
output_path = "/home/sanna/PycharmProjects/Surfaces/TG/2007/10/"  # than the .txt data file in this directory
time_period_start = datetime.datetime(2007,10,13, 0, 0)  # As intergers, just easier   (YYYY,Month,Day,Hour,Min)
time_period_end = datetime.datetime(2007,10,14, 23, 00)
grid_lat_min = 53.98112672        #48.4917 to 65.85825 mid points     # lat width 0.033269252873563214       smaller:58.40593736/53.98112672
grid_lat_max = 65.85825
grid_lat_num = 358         # 523                                                                        smaller:224/314
grid_lon_min = 14.98269705     #9.047926 to 30.124683 mid points   # lon width  0.055465150000000005     smaller:16.813047 / 14.98269705
grid_lon_max = 30.124683
grid_lon_num = 274          #381                                                                        smaller:241 /274
plotting = False  # If True plots each hour to a picture of the surface. Warning, takes long...
spotly_write = False    # Writes file for spotly output (not tested version), in mm and with spotly grid style
write_sl = True        # Writes outputfile as txt file in cm and in order (min-max lat, min-max lon)
timers = False
test_run =False




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



def get_data(day_time):
    # # Finds data of correct hour and calls eval_values to get the evaluation of sea level in all points then
    # calls write_output to write the hours values into spotly file or sealevel file.



    # Open file of measurements for the correct day
    filename= (day_time.strftime("%d_%m_%Y") + ".txt")
    (data, get_data_success) = open_txtfile(filename)
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
    #print(len(lat))

    if len(slev) > 0:  ## Here later some sort of when good enough estimation... len(slev)>A, bad but workable... etc
        if test_run :
            for ind in range(len(station)):
                for ind2 in range(len(station)):
                    if station[ind] == station[ind2]:
                        if ind != ind2:
                            print("At xx same name stations",day_time,station[ind],station[ind2])
        else:
            field = eval_values(lat, lon, slev, day_time)
            if spotly_write :
                write_ok = write_spotly(field, day_time)
            elif write_sl :
                write_ok = write_values(field,day_time,lat,lon)
            else:
                write_ok = False

        #if write_ok:
        #    print("Wrote file ",filename)

    else:
        print("Problems with the sea level measurements file, not enough measurements.")


    return



def eval_values(lat, lon, slev, date):
    # Evaluates sea level in all points
    # field=[]


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
        plt.pcolor(XGRID, YGRID, ZGRID, cmap=cm.jet, vmin=-30, vmax=110, zorder=1,          # -25,100
                   transform=cartopy.crs.PlateCarree())   # vmin=slev_min, vmax=slev_max
        ax.set_extent([16,31.2,56,66.8]) #([16,31.2,56,66.8])#([9.20, 31, 53.4, 66.2])
        ax.set_title('TG-surface interpolation rbf-thinplate ' + date.strftime("%d.%m.%Y %H:%M"))
        land_50m = cartopy.feature.NaturalEarthFeature('physical', 'land', '50m', edgecolor='face',zorder=2,
                                                       facecolor="white")
                                                       #facecolor=cartopy.feature.COLORS['land'])
        ax.add_feature(land_50m)

        ax.plot(lon, lat, 'bo', markersize=3, transform=cartopy.crs.Geodetic(), zorder=3)
        ax.coastlines(resolution='50m', color='black', linewidth=1)

        plt.colorbar(fraction=0.046, pad=0.04,extend="both")
        plt.savefig(output_path + 'Plots/tg_surf_' + date.strftime('%Y%m%d_%H') + '.png')
        plt.close()

    return ZGRID



def write_values(value_fields,date,lat,lon):
    # Writes the output into a file
    write_okey = True
    output_file = output_path + date.strftime("%Y%m%d_%H") + ".txt"

    try:
        file = open(output_file, 'w')
        # print(output_file)
    except:
        print("Couldn't open file to print into.")
        write_okey = False
        return write_okey

    #print(value_fiels.shape)
    # Length of header 7 lines
    file.write("Interpolated Sealevels : rbf: thin plate \n")
    file.write("Date: {}\n".format(date.strftime("%d.%m.%Y %H:%M")))
    file.write("Values in cm \n")
    file.write("GRID: Lat {:f} - {:f}, Lon {:f} - {:f} \n".format(grid_lat_min,grid_lat_max,grid_lon_min,grid_lon_max))
    file.write("GRID: Lat length {:d}, Lon length {:d} \n".format(grid_lat_num,grid_lon_num))
    file.write("In the beginning of file lat,lon of used tide gauge stations as list.  \n")

    #print(len(value_fields[0]))
   # print(len(lat),len(lon))

    for ii in range(len(lat)):
        file.write("{:f},{:f}".format(lat[ii],lon[ii]))
        if ii != len(lat):
            file.write("\t")
    file.write("\n")


    for latx in range(len(value_fields)):
        for lonx in range(len(value_fields[0])):                        # This writes lon - > + on each row in order
            file.write("{:f}".format(value_fields[latx,lonx]))          # lat - > +
            if lonx != len(value_fields[0]):                            # NOT like physical field, since lat grows down on a file
                file.write("\t")
        if latx != len(value_fields):
            file.write("\n")

    file.close()


    return write_okey


def write_spotly(value_field, date):
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
    # print(path)
    os.chdir(path)

    if time_period_end <= time_period_start:
        print("Something went wrong with start time and end time parameter, please check!")
        exit()
    start_time = time_period_start
    end_time = time_period_end


    if not os.path.exists(output_path):  # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)
    if not os.path.exists(output_path + '/Plots'):
        os.makedirs(output_path + '/Plots', exist_ok=True)

    # HERE LOOPING HOURLY
    while end_time >= start_time:
        #print("once",start_time)
        run_timer_start=time.time()
        get_data(start_time)  # Function 3, for opening and processing and writing to file the files for that hour
        if timers:
            run_elapsed = time.time()-run_timer_start
            print('run time: {}'.format(run_elapsed))
        print(start_time)
        start_time = start_time + datetime.timedelta(hours=1)



if __name__ == '__main__':
    main()
