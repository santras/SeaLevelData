#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
#import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.pylab as plb

register_matplotlib_converters()
path="/home/sanna/PycharmProjects/Year_file_resampled/"
output_path="/home/sanna/PycharmProjects/PLOTS/Points/Trendit_new/"

time_period_start=datetime.datetime(2007,1,1,0,0)
#time_period_start=datetime.datetime(2011,1,1,0,0)
time_period_end=datetime.datetime(2016,12,31,23,0)




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

def make_model_tseries(data,station,outputfolder):

    plotname="10 Day Average of Model"
    shortname="ave"

    if station == "perameri":
        station = "Bay of Bothnia"
    elif station == "pohjanlahti":
        station = "Bothnian Sea"
    elif station == "suomenlahti":
        station = "Gulf of Finland"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station+" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")


    fig=plt.figure()
    fig.set_size_inches(20, 8)

    #xticks = pd.date_range(start=start,end=stop,freq="10D")
    #print(xticks)

    #dates = data.index.astype('O')  #.to_datetime


    ax=plt.plot(data.index,data.values,color="b", label="NEMO-Nordic reanalysis ",marker="*",linestyle="--")
    num_date = mdates.date2num(data.index)

    #special_day =mdates.datestr2num("2014-1-1")   # 735234       ind 85     255
    #print(num_date[255])
    #print(x)
    (slope,intercept) = np.polyfit(num_date, data.values.flatten(), 1)
    (partial_slope1,partial_intercept1)= np.polyfit(num_date[0:254],data.values[0:254],1)
    (partial_slope2,partial_intercept2)= np.polyfit(num_date[255:],data.values[255:],1)
    ideal_fit = intercept+slope*num_date
    ideal_fit_partial1= partial_intercept1+partial_slope1*num_date[0:254]
    ideal_fit_partial2= partial_intercept2+partial_slope2*num_date[255:]
    plt.plot(num_date,ideal_fit,color="k",linestyle="-",label="slope="+"{:6.2}".format(slope*365)+" cm/y")  #", intercept="+"{:6.4}".format(intercept))
    plt.plot(num_date[0:254],ideal_fit_partial1,color="c",linestyle="-",label="slope="+"{:6.2}".format(partial_slope1*365)+" cm/y") #+", intercept="+"{:6.4}".format(partial_intercept1))
    plt.plot(num_date[255:],ideal_fit_partial2,color="m",linestyle="-",label="slope="+"{:6.2}".format(partial_slope2*365)+" cm/y") #+", intercept="+"{:6.4}".format(partial_intercept2))
    #print(ideal_fit)
    #print(fitter)
    #p_fitter = np.poly1d(fitter)
    #plb.plot(data.values,
       #p_fitter(data.values), "-k")
    #plt.ylim(-50,80)
    #xx = np.linspace(x.min(), x.max(), 100)
    #dd = mdates.num2date(xx)
    #print(len(dd),len(fitter_b))
    
    #plt.plot(dd, fitter_b(xx), '-b')
    
    #print("test 1")
    #sns.regplot(data.index,data.values)

    #plt.plot(data.index,data.Surface,color="g",linewidth=2,label="Interpolation from tide gauge data")
    #print("test 2")



    plt.legend(fontsize=20)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    #plt.ylim(-55,130)
    plt.yticks(fontsize=20, fontweight="bold")
    plt.xticks(fontsize=20,fontweight="bold")
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=22,fontweight="bold")
    plt.ylabel("Sea Level Height",fontsize=20,fontweight="bold")
    fig.autofmt_xdate()
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #print(len(data))

    fig.savefig(outputfolder +shortname+'_10d_model_BIGGER_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()


def make_surf_tseries(data,station,outputfolder):

    plotname="10 Day Average of Interpolated Sea Level Surfaces"
    shortname="ave"

    if station == "perameri":
        station = "Bay of Bothnia"
    elif station == "pohjanlahti":
        station = "Bothnian Sea"
    elif station == "suomenlahti":
        station = "Gulf of Finland"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station+" " + start.strftime("%-m/%Y") + " - " + stop.strftime("%-m/%Y")


    fig=plt.figure()
    fig.set_size_inches(20, 8)

    #xticks = pd.date_range(start=start,end=stop,freq="10D")
    #print(xticks)

    #dates = data.index.astype('O')  #.to_datetime


    ax=plt.plot(data.index,data.values,color="b", label="Interpolated Sea Level ",marker="*",linestyle="--")
    num_date = mdates.date2num(data.index)

    #special_day =mdates.datestr2num("2014-1-1")   # 735234       ind 85     255
    #print(num_date[255])
    #print(x)
    (slope,intercept) = np.polyfit(num_date, data.values.flatten(), 1)
    #(partial_slope1,partial_intercept1)= np.polyfit(num_date[0:254],data.values[0:254],1)
    #(partial_slope2,partial_intercept2)= np.polyfit(num_date[255:],data.values[255:],1)
    ideal_fit = intercept+slope*num_date
    #ideal_fit_partial1= partial_intercept1+partial_slope1*num_date[0:254]
    #ideal_fit_partial2= partial_intercept2+partial_slope2*num_date[255:]
    plt.plot(num_date,ideal_fit,color="k",linestyle="-",label="slope="+"{:6.2}".format(slope*365)+" cm/y")  #, intercept="+"{:6.4}".format(intercept))
    #plt.plot(num_date[0:254],ideal_fit_partial1,color="c",linestyle="-",label="slope="+"{:6.4}".format(partial_slope1)+", intercept="+"{:6.4}".format(partial_intercept1))
    #plt.plot(num_date[255:],ideal_fit_partial2,color="m",linestyle="-",label="slope="+"{:6.4}".11format(partial_slope2)+", intercept="+"{:6.4}".format(partial_intercept2))
    #print(ideal_fit)
    #print(fitter)
    #p_fitter = np.poly1d(fitter)
    #plb.plot(data.values,
       #p_fitter(data.values), "-k")
    #plt.ylim(-50,80)
    #xx = np.linspace(x.min(), x.max(), 100)
    #dd = mdates.num2date(xx)
    #print(len(dd),len(fitter_b))

    #plt.plot(dd, fitter_b(xx), '-b')

    #print("test 1")
    #sns.regplot(data.index,data.values)

    #plt.plot(data.index,data.Surface,color="g",linewidth=2,label="Interpolation from tide gauge data")
    #print("test 2")



    plt.legend(fontsize=20)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    #plt.ylim(-55,130)
    plt.yticks(fontsize=20,fontweight="bold")
    plt.xticks(fontsize=20, fontweight="bold")
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=22,fontweight="bold")
    plt.ylabel("Sea Level Height (cm)",fontsize=20,fontweight="bold")
    fig.autofmt_xdate()
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #print(len(data))

    fig.savefig(outputfolder +shortname+'_surf_10d_BIGGER_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()





def make_dif_tseries(data,station,outputfolder):

    plotname="60 Day Rolling Average of Difference Between Interpolation and Model"
    shortname="roll"

    if station == "perameri":
        station = "Bay of Bothnia"
    elif station == "pohjanlahti":
        station = "Bothnian Sea"
    elif station == "suomenlahti":
        station = "Gulf of Finland"

    start = (data.index.min())
    stop = (data.index.max())
    titlename = station+": "+plotname # +": " + #+" " + start.strftime("%-m/%Y") + " - " + stop.strftime("%-m/%Y")


    fig=plt.figure()
    fig.set_size_inches(20, 8)

    #xticks = pd.date_range(start=start,end=stop,freq="10D")
    #print(xticks)

    #dates = data.index.astype('O')  #.to_datetime


    ax=plt.plot(data.index,data.values,color="r", label="Difference ",linewidth=4.0)
    #num_date = mdates.date2num(data.index)

    #special_day =mdates.datestr2num("2014-1-1")   # 735234       ind 85     255
    #print(num_date[255])
    #print(x)
    #(slope,intercept) = np.polyfit(num_date, data.values.flatten(), 1)
    #(partial_slope1,partial_intercept1)= np.polyfit(num_date[0:254],data.values[0:254],1)
    #(partial_slope2,partial_intercept2)= np.polyfit(num_date[255:],data.values[255:],1)
    #ideal_fit = intercept+slope*num_date
    #ideal_fit_partial1= partial_intercept1+partial_slope1*num_date[0:254]
    #ideal_fit_partial2= partial_intercept2+partial_slope2*num_date[255:]
    #plt.plot(num_date,ideal_fit,color="k",linestyle="-",label="slope="+"{:6.2}".format(slope*365)+" cm/y")  #, intercept="+"{:6.4}".format(intercept))
    #plt.plot(num_date[0:254],ideal_fit_partial1,color="c",linestyle="-",label="slope="+"{:6.4}".format(partial_slope1)+", intercept="+"{:6.4}".format(partial_intercept1))
    #plt.plot(num_date[255:],ideal_fit_partial2,color="m",linestyle="-",label="slope="+"{:6.4}".11format(partial_slope2)+", intercept="+"{:6.4}".format(partial_intercept2))
    #print(ideal_fit)
    #print(fitter)
    #p_fitter = np.poly1d(fitter)
    #plb.plot(data.values,
       #p_fitter(data.values), "-k")
    #plt.ylim(-50,80)
    #xx = np.linspace(x.min(), x.max(), 100)
    #dd = mdates.num2date(xx)
    #print(len(dd),len(fitter_b))

    #plt.plot(dd, fitter_b(xx), '-b')

    #print("test 1")
    #sns.regplot(data.index,data.values)

    #plt.plot(data.index,data.Surface,color="g",linewidth=2,label="Interpolation from tide gauge data")
    #print("test 2")



    #plt.legend(fontsize=20)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    #plt.ylim(-55,130)
    plt.yticks(fontsize=20,fontweight="bold")
    plt.xticks(fontsize=20, fontweight="bold")
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)                                                                                                                                             
    plt.title(titlename,fontsize=22,fontweight="bold")
    plt.ylabel("Interpolation - Model (cm)",fontsize=20,fontweight="bold")
    fig.autofmt_xdate()
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    #print(len(data))

    fig.savefig(outputfolder +shortname+'_dif_10d_BIGGER_' + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
    #plt.show()
    plt.close()




def make_multi_tseries(data,station,outputfolder):


    plotname="Averages of Interpolated Surface and Model"
    shortname="ave"

    if station == "perameri":
        station = "Bay of Bothnia"
    elif station == "pohjanlahti":
        station = "Bothnian Sea"
    elif station == "suomenlahti":
        station = "Gulf of Finland"




    start = (data.index.min())
    stop = (data.index.max())
    titlename = plotname +": " +station+" " + start.strftime("%-d.%-m.%Y") + " - " + stop.strftime("%-d.%-m.%Y")


    fig=plt.figure()
    fig.set_size_inches(22, 8)

    #xticks = pd.date_range(start=start,end=stop,freq="10D")
    #print(xticks)

    #dates = data.index.astype('O')  #.to_datetime


    ax=plt.plot(data.index,data.Model,color="b",linewidth=2, label="NEMO-Nordic")
    #print("test 1")


    plt.plot(data.index,data.Surface,color="g",linewidth=2,label="Interpolation from tide gauge")
    #print("test 2")



    plt.legend(fontsize=20)
    #print("test 4")

    plt.xlim(start, stop) # X limits to actual data limits%
    plt.ylim(-55,130)
    plt.yticks(fontsize=16) #,fontweight="bold")
    plt.xticks(fontsize=16) #,fontweight="bold")
    #plt.tick_params(axis="x",which="minor",bottom=False,top=False,labelbottom=False)
    #setmajorlocation

    #(locations,xlabels)=plt.xticks()    #fontsize=14
    #print(locations,xlabels)

    #plt.xlabel("Sealevels (EVRF) in cm",fontsize=16)
    plt.title(titlename,fontsize=22, fontweight="bold")
    plt.ylabel("Sea Surface height (cm)",fontsize=20,fontweight="bold")
    fig.autofmt_xdate()
    #ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')



    fig.savefig(outputfolder +shortname+"_BIG_plotlimits_" + station + start.strftime("%Y%m%d") + "_" + stop.strftime("%Y%m%d") + '.png',dpi=100)
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
    #make_multi_tseries(data,station,outputfolder)


    return data



def main():
    # Main of plotting timeseries of stations

    output_folder = output_path
    if not os.path.exists(output_folder):  # Making the output folder if needed
        os.makedirs(output_folder, exist_ok=True)

    os.chdir(path)

    year_start = int(time_period_start.strftime("%Y"))
    year_end = int(time_period_end.strftime("%Y"))

    years = range(year_start, year_end + 1)
    indexes = pd.date_range(time_period_start, time_period_end, freq="4H")
    mycolumns = ["Surface","Model"]
    #print(years)

    for station in ["perameri","pohjanlahti","suomenlahti"]:
        this_station = pd.DataFrame(index=indexes, columns=mycolumns)
        this_station[:] = np.nan
        for plot_year in years:
            file=path+station+"_"+str(plot_year)+".txt"
            #(data,okey)=open_txtfile(file)
            #print(data[0:10])
            data = process_file(file,station,output_folder)
            this_station.loc[data.index] = data
            #print(this_station.loc[data.index].head())

        this_station["Difference"] = this_station.Surface-this_station.Model
        #print(len(this_station))
        #this_station = this_station.Surface.astype("float64").resample("10D").mean()
        #this_station = this_station.Model.astype("float64").resample("10D").mean()
        this_station = this_station.Difference.astype("float64").rolling(window=60,min_periods=20,center=True, win_type=None).mean()
        #print(len(this_station))

        #print(this_station)
        #make_surf_tseries(this_station, station, output_folder)
        #make_model_tseries(this_station,station,output_folder)
        make_dif_tseries(this_station, station, output_folder)
    return





if __name__ == '__main__':
    main()
