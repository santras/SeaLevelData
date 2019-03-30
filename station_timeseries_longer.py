#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates

register_matplotlib_converters()
path="/home/sanna/PycharmProjects/Year_file_resampled/"
output_path="/home/sanna/PycharmProjects/PLOTS/Points/T_Series_longer_all/"

#time_period_start=datetime.datetime(1993,1,1,0,0)
time_period_start=datetime.datetime(2011,1,1,0,0)
time_period_end=datetime.datetime(2011,12,31,23,0)




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




def make_multi_tseries(data,station,outputfolder):


    plotname="Time Series"
    shortname="l_tseries"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station.capitalize()+" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")


    fig=plt.figure()
    fig.set_size_inches(20, 8)

    #xticks = pd.date_range(start=start,end=stop,freq="10D")
    #print(xticks)

    #dates = data.index.astype('O')  #.to_datetime


    ax=plt.plot(data.index,data.Model,color="b",linewidth=2, label="NEMO-Nordic")
    #print("test 1")


    plt.plot(data.index,data.Surface,color="g",linewidth=2,label="Interpolation from tide gauge data")
    #print("test 2")



    plt.legend(fontsize=12)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    plt.ylim(-55,130)
    plt.yticks(fontsize=14)
    plt.xticks(fontsize=14)
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=18)
    plt.ylabel("Sea Surface height (cm)",fontsize=14)
    fig.autofmt_xdate()
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')



    fig.savefig(outputfolder +shortname+'_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()


def process_file(filename, station,outputfolder):

    #print(filename)
    #test = pd.read_csv(filename)
    #print(test.head())

    headers = ["Dates", "Surface", "Model"]

    data = pd.read_csv(filename,sep="\t", header=None, names=headers,  parse_dates=["Dates"]) #parse_dates={"Time": ["Dates", "Times"]}
    data.Surface = data.Surface.apply(lambda x: np.float64(x))  # Changing the types of Sealevels to float
    data.Model = data.Model.apply(lambda x: np.float64(x))

    #print(type(data))
    #print(data.keys())

    # Indexing dataframe by date
    data=data.set_index('Dates')



    #data = data.loc["2011-3-1":"2011-5-31"]
    #data = data.loc["2011-8-1":"2011-10-31"]
    #data = data.loc["2007-3-1":"2007-5-31"]
    #data = data.loc["2007-8-1":"2007-10-31"]
    #data = data.loc["2012-3-1":"2012-5-31"]
    #data = data.loc["2012-8-1":"2012-10-31"]

    #data = data.loc["2011-1-1":"2011-3-31"]
    #data = data.loc["2011-4-1":"2011-6-30"]
    #data = data.loc["2011-7-1":"2011-9-30"]
    #data = data.loc["2011-10-1":"2011-12-31"]

    print(data.head())
    make_multi_tseries(data,station,outputfolder)


    return



def main():
    # Main of plotting timeseries of stations

    output_folder = output_path
    if not os.path.exists(output_folder):  # Making the output folder if needed
        os.makedirs(output_folder, exist_ok=True)

    os.chdir(path)

    year_start = int(time_period_start.strftime("%Y"))
    year_end = int(time_period_end.strftime("%Y"))

    years = range(year_start, year_end + 1)
    #print(years)

    for station in ["perameri","pohjanlahti","suomenlahti"]:
        for plot_year in years:
            file=path+station+"_"+str(plot_year)+".txt"
            #(data,okey)=open_txtfile(file)
            #print(data[0:10])
            process_file(file,station,output_folder)

    return





if __name__ == '__main__':
    main()
