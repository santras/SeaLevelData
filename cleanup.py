#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats

path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt/"

def open_txtfile(file_name):
    #Opens a readable file and reads it
    try:
        file=open(file_name,'r')
        data=file.readlines()
        #print(len(data))
        file.close()
        ok=True
    except:
        print("File {} couldn't be opened in open_txtfile".format(file_name))   # Returns empty data variable and False if not successfull
        ok=False
        data=[]
        return data,ok

    return data, ok

def clean_up_helper(date):
    # To check if date is at most half an hour late from when the measurement should have been
    help_variable = date - datetime.timedelta(seconds=(int(date.strftime("%M")) * 60))  # making help_variable for time when measurement should have been made
    if date - help_variable <= datetime.timedelta(seconds=1800):  # If measurement is made at most half an hour late
        help_boolean=True
    else:
        help_boolean = False
    return help_boolean



def clean_up(date,s_lev,q_label,filename):
    #clean up problematic files with more than at the hour measurements

    new_date=[]
    new_slev=[]
    new_qual=[]
    print("Cleaning up file ",filename," of length ",len(date))


    for ind in range(len(date)):
        if date[ind].strftime("%M") == "00":                # IF at the hour measurement exist, keep it
            new_date.append(date[ind])
            new_slev.append(s_lev[ind])
            new_qual.append(q_label[ind])
        elif (len(new_date))>1:                                       # Wont work for first okey line since no other measurements exis
            if date[ind].strftime("%H") != new_date[-1].strftime("%H"):       # If no measurement from same hour allready exist
                if (clean_up_helper(date[ind])):  # If measurement is okey approksimation from at the hour measurement
                    new_date.append(date[ind])
                    new_slev.append(s_lev[ind])
                    new_qual.append(q_label[ind])
                #else: # REMOVE THIS
                #    print("REMOVING bad approksimation from same hour as", new_date[-1], date[ind])
            elif date[ind].date() != new_date[-1].date() :           # If measurement allready from same hour, check if different date
                if (clean_up_helper(date[ind])):  # If measurement is okey approksimation from at the hour measurement
                    new_date.append(date[ind])
                    new_slev.append(s_lev[ind])
                    new_qual.append(q_label[ind])
                #else: # REMOVE THIS
                #    print("REMOVING from same hour as", new_date[-1], date[ind])
            #else:  # REMOVE THIS
               # print("REMOVING from same hour as", new_date[-1],date[ind])
        else:   # if first line case
            if (clean_up_helper(date[ind])):    # If measurement is okey approksimation from at the hour measurement
                new_date.append(date[ind])
                new_slev.append(s_lev[ind])
                new_qual.append(q_label[ind])
            #else:                # REMOVE THIS
                #print("REMOVING FIRST LINE",date[ind])

    print("Cleaned file now at length ",len(new_date))


    return [new_date], [new_slev], [new_qual]

def add_missing(date, s_lev, q_label, filename,inds_to_check):
    # missing measurement, add missing values
    #checking if list in order

    print("Adding missing to file ",filename, "len of original ",len(date))

    if date != sorted(date):
        print("Warning- file not in order in ",filename )



    ind_dealt_with = 0
    new_date = []
    new_slev = []
    new_qual = []

    #print(inds_to_check)

    # Fixing loop
    for ind in range(len(inds_to_check)):
        #print(inds_to_check[ind])
        #print("About to correct ",date[(inds_to_check[ind])-1],date[(inds_to_check[ind])],date[(inds_to_check[ind])+1])
        for index in range(ind_dealt_with,((inds_to_check[ind]))):                 # Putting the measurements  before the problem in for each rounds
            #print("adding ",index,date[index])
            new_date.append(date[index])
            new_slev.append(s_lev[index])
            new_qual.append(q_label[index])

        while date[(inds_to_check[ind])] - new_date[-1] >datetime.timedelta(seconds=3600):      # While difference is more than 1 hour put in  measurements
            new_date.append(new_date[-1]+datetime.timedelta(seconds=3600))
            new_slev.append(np.nan)
            new_qual.append(9)
            #print(date[inds_to_check[ind]],new_date[-1])

        ind_dealt_with=inds_to_check[ind]
        #print("done ",ind_dealt_with)


    for index3 in range(ind_dealt_with, len(date)):          # Putting the last ones in (this outside of fixing loop)
        #print("end adding",index3,date[index3])
        new_date.append(date[index3])
        new_slev.append(s_lev[index3])
        new_qual.append(q_label[index3])


    #for inds in range(403248-1,403248+12): #(len(new_date)):
     #   print(new_date[inds])

    if new_date != sorted(new_date):
        print("Warning - Problems with adding missing filename ",filename)
        bad= []
        for ind in range(1, len(new_date)):
            if new_date[ind] - new_date[ind - 1] != datetime.timedelta(seconds=3600):
                bad.append(ind)
        print("Problems with lines ",bad," len of file ",len(new_date))
        for ii in range (len(bad)):
            print(new_date[bad[ii]-1],new_date[bad[ii]],new_date[bad[ii]+1])
        exit()                                                       # I want to exit this, since I need to fix this part if needed

    print("Added missing to file ",filename," new length of file ",len(new_date))

    return [new_date], [new_slev], [new_qual]


###########################################3

def main():
    os.chdir(path)
    for filename in glob.glob("H*txt"):
        file = open (filename,"r")
        data = file.readlines()
        file.close()


        head=[]
        date=[]
        s_lev=[]
        q_label=[]


        for ii in range(0,24):
            head.append(data[ii])
            if data[ii] == "Datum*":
                if (data[ii].split()[1].strip() == "msl" or data[ii].split()[1].strip() == "MSL" ):
                    print("Warning - Datum MSL in file ",filename)


        for jj in range(24,len(data)):
            #print(filename)
            #print(data[jj])
            splitline=data[jj].split()

            date.append(datetime.datetime(int(splitline[0].strip().split("-")[0]), int(splitline[0].strip().split("-")[1]),
                                   int(splitline[0].strip().split("-")[2]),int(splitline[1].strip().split(":")[0]),int(splitline[1].strip().split(":")[1])))
            s_lev.append(float(splitline[2].strip()))
            q_label.append(int(splitline[3].strip()))

        if len(date)<2:             # NOT WORTH CHECKING FILES IF EMTY OR ONLY 1 LINE
            print("Too short file",filename)
            continue

        problematic_file = False

        for ind in range(len(date)):
            if not date[ind].strftime("%M")=="00":
                problematic_file = True

        if problematic_file:
            print("Problematic file, timeinterval not 1 hour ", filename)       ### This now clearing up multiples of same hour okey
            #print(date[0:10])
            (date,s_lev,q_label)=clean_up(date,s_lev,q_label,filename)

        non_hour_ind=[]
        for ind in range(1,len(date)):
            if date[ind]-date[ind-1] != datetime.timedelta(seconds=3600):
                non_hour_ind.append(ind)

        if len(non_hour_ind)!=0:
            print("Missing measurements ",filename)                             ########### Next now filling in the missing measuremenets!
            (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename,non_hour_ind)


        if ((not problematic_file) and non_hour_ind == []):
            print("Good file",filename)

        ########### Next, writing to file and then testing one more time untill I will run it (to another folder)
        ######## Need to check the sweden stuff as well.





if __name__ == '__main__':
    main()