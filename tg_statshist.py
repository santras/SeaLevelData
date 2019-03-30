#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt



namefile="/home/sanna/PycharmProjects/NorthernBaltic_Points_of_Interest_cleaned.txt"
path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned_new/"
outputpath="/home/sanna/PycharmProjects/Hists/TG/"

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

def process_file(filename):

    headers = ["Dates","Times","Sealevels","Q-Flags"]
    try:
        data=pd.read_csv(filename,skiprows=24,sep="\t",header=None,names=headers,parse_dates={"Timestamp": ["Dates","Times"]}) #na_values="nan",

        data.Sealevels = data.Sealevels.apply(lambda x: np.float64(x))         # Changing the types of Sealevels to float

        print(filename)
    except:
        print("Having problems ", filename)
        for xx in range (len(data.Sealevels.values)):                           #### Problem is I went in and did stuff... now it thinks space is it's own values, shit
            try:
                data.Sealevels.values[xx] = np.float64(data.Sealevels.values[xx])
                #print("Conversion success on second try")
            except:
                print("Problematic index",xx,data.values[xx])

    #print(data.head())

    #print(data.Timestamp.head())

    #print(np.nanmin(data.Sealevels),np.nanmax(data.Sealevels))

    slevs_over=100    #120
    slevs_under=-20   #-30
    slevs_non_nan =0

    for ind in range (len(data.Sealevels)):
        if not np.isnan(data.Sealevels[ind]):
            if data.Sealevels[ind]>110:
                slevs_over=slevs_over+1
            elif data.Sealevels[ind]<-30 :
                slevs_under=slevs_under+1
            else:
                slevs_non_nan=slevs_non_nan+1

    return slevs_non_nan,slevs_over,slevs_under

    #print(np.percentile(slevs,[2.5,97.5]))









def main():

    # Opening interest points
    (data, okey) = open_txtfile(namefile)
    if not okey:
        print("Couldn't open file for interest points")


    # Finding matching tg file
    os.chdir(path)
    slevs_nonan_a=0
    slev_over_a=0
    slev_under_a=0

    print(path)
    for line in data:
        namematch = False
        splitline = line.split()
        name = splitline[0].strip().lower()  # making names lower case to help with comparison
        testname=[]
        for letter in name:
            if letter != "-":                   # dealing with hypenated name
                if not letter in ("ö","ä","å") :    # dealing with scandinavians
                    testname.append(letter)
                elif letter == "ö":
                    testname.append("o")
                elif letter =="ä" or letter =="å":
                    testname.append("a")
        name="".join(testname)

        for file in glob.glob("*.txt"):
            if file.lower() == name+".txt" :
                namematch = True
                #print(file,name)

                # Opening file and doing stuff
                (slevs_nonan,slev_over,slev_under)=process_file(file)
                slevs_nonan_a=slevs_nonan_a+slevs_nonan
                slev_over_a=slev_over_a+slev_over
                slev_under_a=slev_under_a+slev_under

        if not namematch:
            print("Cound't file match for:",name)


    #print(np.percentile(slevs_all,[2.5,97.5]))
    print("Total non nan values, Values over max drawn, Values under min drawn:",slevs_nonan_a,slev_over_a,slev_under_a)
    print("As percentage (max,min)",(slev_over_a/slevs_nonan_a)*100,(slev_under_a/slevs_nonan_a)*100)



if __name__ == '__main__':
    main()
