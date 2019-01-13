#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import numpy as np
import os, glob
import pandas as pd

# The purpose of this code is to change SMHI Open Data to same txt format as the CMEMS data

GLstyle = False
headerfilename=('header_cmems.txt')       # Path to  header titles as a txt file
headerfilename2=('header_gl.txt')         # Path to GL (style header file)
path="/home/sanna/PycharmProjects/TG_SMHI_raw//" # Path for the original data file folder
output_path= path + "../SMHI//"
time_difference=60                      # Time difference in minutes between measurements


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


def get_headers(headfile):
    # Reads a headerfile that contains the header titles and the order they should be in in the final header
    (headerfile,opened)=open_txtfile(headfile)
    if not opened:
        print('Failed to generate headers, need a headerfile for model in get_headers.')
        exit('Ending program')
    Headers = {}
    order=[]
    for line in headerfile:                 # Reads the lines of the file into a dictionary
        if not (line.strip() == "" or line.strip()[0] == "#"):
            if ":" in line:                     # Some unchanging variables are saved in into the dictionary from the headerfile
                splitline = line.split(":")
                key = splitline[0].strip()
                value = splitline[1].strip()
            else:
                key = line.strip()
                value = ""
            Headers[key] = value
            order.append(key)
    return Headers,order




def open_swedenfiles(file,header):

    # Opens Swedens open data .csv files  then reads the data and updates the header
    try:
        file_ = open(file, 'r')
        data = file_.readlines()
        file_.close()
    except:
        print("Problem opening file: ", file)
        data = []
        okey = False

    name=((data[1].split(";"))[0])
    # if name.startswith("BARS"):          # Trying to deal with Scandinavians.. basically just rewriting them
    #     name="Barseback"
    # elif name.startswith("BJ"):
    #     name="Bjorn"
    # elif name.startswith("DRAG"):
    #     name="Draghallan"
    # elif name.startswith("FURU"):
    #     name="Furuogrund"
    # elif name.startswith("G"):
    #     name="Goteborg"
    # elif name.startswith("MAL"):
    #     name="Malmo"
    # elif name.startswith("SKAN"):
    #     name="Skanor"
    # elif name.startswith("SM"):
    #     name="Smogen"
    # elif name.startswith("Ã"):
    #     name="Olands Norra Udde"
    # else:
    #     name=name.title()       # This makes the name start with big letter but to be small otherwise

    units = ((data[4].split(";"))[1]).strip()
    datum = ((data[10].split(";"))[5]).split(":")[1].strip()
    lat = ((data[1].split(";"))[2]).strip()
    lon = ((data[1].split(";"))[3]).strip()
    #print(lat,lon,units,datum)
    header=update_header(header,name,lat,lon,units,datum)
    okey = True
    date_str=[]
    slev=[]
    quality=[]
    sl_variables = []

    if ((data[6].split(";"))[0])=="Datum Tid (UTC)":    # juts an extra check that header size is ok
        for ind in range(7,len(data)):
            date_str.append(data[ind].split(";")[0])    # Reads in the variables
            slev.append(float(data[ind].split(";")[1]))
            quality.append(data[ind].split(";")[2])
        date=[]
        time=[]
        for line in date_str :
            date.append((line.split()[0]).strip())
            time.append((line.split()[1]).strip())
        year=[]
        month=[]
        day=[]
        #print(date[0:10])
        #print(time[0:10])
        for line in date:
            year.append(int((line.split("-")[0]).strip()))
            month.append(int((line.split("-")[1]).strip()))
            day.append(int((line.split("-")[2]).strip()))
        #print(year)
        hour=[]
        minutes=[]
        for line in time:
            hour.append(int((line.split(":")[0]).strip()))
            minutes.append(int((line.split(":")[1]).strip()))
        #print(minutes[0:10])
        date_time=[]
        for inde in range(len(minutes)):                    # changes date + time strings into datetime
            date_time.append(datetime.datetime(year[inde],month[inde],day[inde],hour[inde],minutes[inde]))

        for ii in range(len(date_time)):
            sl_variables.append([date_time[ii],slev[ii],quality[ii]])

    else:
        print("Header size don't match expected in open_swedenfiles with file : ",file)
        okey=False
   # print(sl_variables[0:10])

    return sl_variables,header,okey,name


def process_file(filename,sl_variables,Headers,station):

    # Makes an output folder if it doesen't exist and calls in functions to check data

    station=station.strip()

    if " " in station:
        station1=(station.split(" ")[0]).capitalize()
        station2 = (station.split(" ")[1]).capitalize()
        station=station1+station2
    else:
        station=station.capitalize()
    station=station.replace(" ","")
    station=station.replace("ä","a")
    station = station.replace("ö", "o")
    station = station.replace("å", "a")
    station=station.replace("Ä","A")
    station = station.replace("Ö", "O")
    station = station.replace("Å", "A")

    output_file=output_path + station+".txt"                   # HERE OUTPUTFILENAME

    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)


    (sl_variables, missing, tot_values, start, end)=check_data(filename,sl_variables)
    #print(Headers)
    Headers_filled=fill_headers(Headers,missing,tot_values,start,end)

    return(sl_variables,Headers_filled,output_file)



def check_data(name,sl_variables):
    # Checks order, inserts missing values, counts number of total values,start date, end date

    transposed = []         # Trick to only send timestamps to the check_listorder function
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    (inorder,inds)=check_listorder(transposed[0],time_difference) # checking if entries with 60 min time interval

    if not inorder:
        print("File "+name+" is not in order or entries are missing, ordering.")
        sl_variables=sorted(sl_variables)                           # And timestamps can be sorted..

        transposed = []
        for i in range(3):
            transposed.append([row[i] for row in sl_variables])
        (inorder, inds) = check_listorder(transposed[0],time_difference)

        if not inorder:
            print("File ",name," seems to have missing entries, making new entries to patch. ")
            ind_copied=0
            new_variable=[]                             # This will be sl_variable with new empty entries
            for ind in range(len(inds)):
                index_wrong = (inds[ind])             # The first one where time step not = time_difference
                for index in range(ind_copied,(index_wrong) ):  # Copies the "in order" part directly to new_variable
                    new_variable.append(sl_variables[index])
                ind_copied=(index_wrong)
                thisone=sl_variables[index_wrong-1]             # this is last "good"
                nextone=sl_variables[index_wrong]               # this is first after jump

                # Could be done with while loop as well.. but got a headacke from the indexes and infinite loops..
                rounds=((nextone[0]-thisone[0])/datetime.timedelta(seconds=time_difference*60))
                for indexi in range(0,int(rounds)-1):       # Adding the "empty" values
                    thisone = ([thisone[0] + datetime.timedelta(seconds=time_difference * 60),np.nan,9])
                    new_variable.append(thisone)  # nan for sea level and 9 =missing value for quality label

            for index in range(ind_copied,len(sl_variables)):       # Adding the what's left after last "problem"
                new_variable.append(sl_variables[index])

            transposed=[]
            for i in range(3):
                transposed.append([row[i] for row in new_variable])
            (inorder, inds) = check_listorder(transposed[0], time_difference)
            if not inorder:
                print("Problem with ordering in check_data")
            sl_variables=new_variable

    missing=0
    for index in range(len(sl_variables)):              # Missing= either 9 as a quality flag or nan as the value
        if sl_variables[index][2]==9:
            missing = missing + 1
        elif np.isnan(sl_variables[index][1]):
            sl_variables[index][2]=9
            missing=missing+1
    #print(missing)

    transposed = []                                     # Start date and end date
    for i in range(3):
        transposed.append([row[i] for row in sl_variables])
    start_date=min(transposed[0])
    end_date=max(transposed[0])
    #print(start_date,end_date)                         # Length of file
    length=len(sl_variables)


    return sl_variables,missing,length,start_date,end_date




def check_listorder(dates,diff,current_ind=1):
    # Checks that the time difference between measurements is correct
    # starts from current ind , default is 1 (it counts time difference between current ind and ind -1)

    count = 0
    inds = []
    for ind in range(current_ind, len(dates)):
        if (dates[ind]-dates[ind-1]) != datetime.timedelta(seconds=diff*60):
            count = count + 1
            inds.append(ind)
    if count == 0:
        ok = True
    else:
        ok = False
    return ok, inds


def update_header(Headers, stationname, latitude, longitude,units,datum):
    # Updates header info
    Headers["Source"] = "SMHI"
    Headers["Datum"] = datum
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    if units == "cm":
        Headers["Unit"] = "centimeter"
    else:
        exit("Units not cm")
    return Headers


def fill_headers(Headers,missing,total,starttime,endtime):
    # Called by: , Calls: -
    # Fills headers
    # Almost completely like in tgtools
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = str(total)
    Headers["Interval"] = 60
    if GLstyle:
        Headers["Missing values"] = missing

    return Headers

def write_output(HeaderDict, sl_variables, order, outputfile):

    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []
    #print(order)
    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])
    #print(Header)
    # The header writing code, contains various checks.
    output=[]
    for line in Header:
        # Loop through all header lines
        if not len(line) ==  2:
            # Header line should only have to elements (key and value)
            print ("! Warning: broken header line:", line)
        else:
            # If there's nothing in either position of the header,
 			# replace it with an empty string.
            if line[0] == None:
                line[0] = ""
            if line[1] == None:
                line[1] = ""
            # Warn if header key or value are empty.
            if line[0] == "" :
                print ("! Warning: nameless header field: ", line)
            if line[1] == "" :
                print ("! Warning: valueless header field: ", line)
            # Finally write header line. Limit first field to 20 characters.
            if len(line[0]) > 20 :
                print ('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))

            output.append("%-20s%s\n" % (line[0][0:20], line[1]))

    file = open(outputfile, 'w')
    #print(output)

    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')

    dates=[]
    slev=[]
    qual=[]

    for ii in range(len(sl_variables)):
        dates.append((sl_variables[ii][0]).strftime("%Y-%m-%d %H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints=[]
    for ind in range(len(dates)):
        prints.append("{}\t{:6.4}\t{:3}\n".format(dates[ind],slev[ind],qual[ind]))



    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()


def qual_flag_cmems(variables):
    for ii in range(len(variables)):
        if variables[ii][2]=="G":
            variables[ii][2] = 1
        elif variables[ii][2]=="Y":
            variables[ii][2] = 8
        elif variables[ii][2] == "O":
            variables[ii][2] = 0
        else:
            variables[ii][2] = 9

    #print(variables[0:10])
    return variables


def qual_flag_gl(variables):
    for ii in range(len(variables)):
        if variables[ii][2]=="G":
            variables[ii][2] = 1
        elif variables[ii][2]=="Y":
            variables[ii][2] = 2
        elif variables[ii][2] == "O":
            variables[ii][2] = 3
        else:
            variables[ii][2] = 9
    return variables

def prep_data(file, sl_variables, headers):

    data_good = 0
    missing = 0
    no_qc = 0
    interpolated = 0
    # print(type(qual))

    for index in range(len(sl_variables)):
        if sl_variables[index][2] == 1:
            data_good = data_good + 1
        elif sl_variables[index][2] == 9:
            missing = missing + 1
        elif sl_variables[index][2] == 0:
            no_qc = no_qc + 1
        elif sl_variables[index][2] == 8:
            interpolated = interpolated + 1

        else:
            print("Weirdness in quality flag in  ", file, index, sl_variables[index])

    headers["0 No QC performed"] = no_qc
    headers["1 Good"] = data_good
    headers["2 Probably good"] = 0
    headers["3 Bad pos. corr."] = 0
    headers["4 Bad Data"] = 0
    headers["5 Value changed"] = 0
    headers["6 Not used"] = 0
    headers["7 Nominal value"] = 0
    headers["8 Interpolated"] = interpolated
    headers["9 Missing value"] = missing

    # print("In file",file,":","Good data:", data_good," Missing Data:",missing," Bad Data:",bad_data," No QC:", no_qc, " Probably Good:",prob_good,
    #    " Value Changed:", val_change, " Nominal Value: ", nominal, " Interpolated:", interpolated)

    return headers




def main():

    if GLstyle:
        (Header_dict,header_order)=get_headers(headerfilename2)        # gettin header model
    else:
        (Header_dict, header_order) = get_headers(headerfilename)

    os.chdir(path)
    for file in glob.glob("*.csv"):                 # Opens all that ends with .csv in the path folder one by one
        print(file)
        (sl_variables,header,okey,station)=open_swedenfiles(file,Header_dict)


        if GLstyle:
            sl_variables = qual_flag_gl(sl_variables)
        else:
            sl_variables=qual_flag_cmems(sl_variables)

        # open_swedenfiles opens the files, updates header, changes date+time strings into datetime object and puts it
        # with the rest of the data as sl_variable
        if not okey:
            print("Something went wrong opening datafile, exiting program.")
            exit()
        print(file)
        (sl_variables, header, output_file)=process_file(file,sl_variables,header,station)

        if not GLstyle:
            header=prep_data(file, sl_variables, header)

        write_output(header, sl_variables, header_order, output_file)


        print(station, " done")
        # process_file, checks the order, adds missing, counts some header info, writes gl-files
    #(filenames,found)=open_rfile('filenames.txt')
    #if not found:
       # print('Needs a file with filenames to be processed')
        #exit('Ending program')
    #for line in filenames:
       # process_file(Header_dict,header_order,line.strip())





if __name__ == '__main__':
    main()