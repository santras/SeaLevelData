#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to take files and change the height refrence frame to EVRF07


GLstyle= False                             # True if want to do gl-format for output
headerfilename=('header_cmems.txt')       # Path to  header titles as a txt file
headerfilename_gl=('header_gl.txt')         # Path to GL (style header file)
station_country_list=('station_countries.txt')                # Stations by countries txt file, should be in the data directory
path="../TGData_txt//"                        # Path for the original data file folder, script goes throuh all .txt files in the folder
output_path= path +"../TGData_EVRF2007_txt//"      # Outputpath
datum_new="EVRF2007"                                                 # The new datum

# Change in cm according to evrs.bkg.bund.de
#BHS77 /Kronstadt datum
Estonia=19
Latvia=15
Lithuania=12
Poland=17
Russia = 25     # Lähde Jaakko Mäkinen( Ekman 1999 Marine Geodecy)


# Amsterdam (NAP) Datum
Datum_dict={}
Datum_dict["DHHN92"] = 1
Datum_dict["DVR90"] = 0
Datum_dict["RH2000"] = -1
Datum_dict["NN2000"] = -1
#Datum_dict["TGZ"] = -462.3 # Testing if this would work...
#Datum_dict["Unknown"] = -488 # Testing if this would work... probably needs some tweeking (-500 + lithuania +12)

# Kronstadt datum
Datum_dict["SNN76"] = 16
# Germany old system was 15 cm lower  than new new system and then +1 change to EVRF07
# https://www.bkg.bund.de/DE/Ueber-das-BKG/Geodaesie/Integrierter-Raumbezug/Hoehe-Deutschland/hoehe-deutsch.html


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

def get_headers(file_name):

    # Reads a headerfile that contains the header titles and the order they should be in in the final header

    (headerfile,opened)=open_txtfile(file_name)
    if not opened:
        print('Failed to generate headers, need a headerfile for model in get_headers/Function2.')
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


def open_slfiles(file,header):

    # Opens sealevel txt  files, then reads the data and updates the header
    (data,okey) = open_txtfile(file)
    #print(file)

    # taking values and order from header

    station=""
    lat=np.nan
    lon=np.nan
    source=""
    missing=0
    start=[]
    end_t=[]
    tot=0
    unit=""
    t_diff=np.nan
    timesys=""


    for line in (data[0:20]):
        if not (line.strip() == "" or line.strip()[0] == "#"):
            splitline=line.split()
            if splitline[0]=="Station":
                station=splitline[1].strip()
            elif splitline[0]=="Longitude":
                lon=splitline[1].strip()
            elif splitline[0]=="Latitude":
                lat = splitline[1].strip()
            elif splitline[0]=="Source":
                if len(splitline)==1:
                    source=""
                    print("Source missing in ",file)
                else:
                    source=splitline[1].strip()
            elif splitline[0]=="Datum":
                if len(splitline)==1:
                    datum=""
                    print("Datum missing in ",file)
                else:
                    datum=splitline[1].strip()
            elif splitline[0]=="Missing values":
                missing=splitline[2].strip()
            elif splitline[0]=="Start":
                start=splitline[2].strip()
            elif splitline[0]=="End":
                end_t=splitline[2].strip()
            elif splitline[0]=="Total observations":
                tot=splitline[2].strip()
            elif splitline[0] == "Unit":
                unit = splitline[2].strip()
            elif splitline[0] == "Interval":
                t_diff = splitline[2].strip()
            elif splitline[0] == "Time System":
                timesys = splitline[2].strip()
            elif splitline[0] == "0 *":
                tot = splitline[2].strip()

    (header)=update_header(header, station, lat, lon, source, missing,start,end_t,tot,unit,t_diff,timesys)
    #print(header)

    if not (data[20][0]=="-"):    # juts an extra check that header size is ok
        print("Header size of file is not expected in file: ",file)
        exit()
    date=[]
    time=[]
    slev=[]
    qual=[]
    for ind in range(21,len(data)):
        splitline=(data[ind]).split()
        date.append(splitline[0].strip())
        time.append(splitline[1].strip())
        slev.append(float(splitline[2].strip()))
        qual.append(int(splitline[3].strip()))

    variables=[]
    for ind in range(len(date)):
        splitdate=((date[ind]).split("-"))
        splittime=((time[ind]).split(":"))
        thisdate=(datetime.datetime(int(splitdate[0]),int(splitdate[1]),int(splitdate[2]),int(splittime[0]),
                                     int(splittime[1])))
        variables.append([thisdate,slev[ind],qual[ind]])

    return variables, header,station, okey,datum

# Function 4
def update_header(Headers, stationname, latitude, longitude,source,missing,starttime,endtime,total):
    #Called by: open_ncfiles/Function3,  Calls:-
    # Updates header info
    # like in tgtools
    # later, start, end, total, missing
    Headers["Source"] = source
    Headers["Datum"] = datum_new
    Headers["Station"] = stationname
    Headers["Longitude"] = longitude
    Headers["Latitude"] = latitude
    Headers["Unit"] = "centimeters"
    Headers["Interval"] = "1 hour"
    Headers["Time system"] = "UTC"
    Headers["Missing values"]= missing
    Headers["Start time"] = starttime
    Headers["End time"] = endtime
    Headers["Total observations"] = total
    return Headers

# Function 5
def process_file(filename,sl_variables,Headers,order,station,country,datum):
    # Called by: Main, Calls: check_data/Function5, fill_headers/Function8, write_output/Function9
    # Makes an output folder if it doesen't exist and creates needed variables for header, then it updates and orders
    # the header and finally writes the output of spesified time period.

    # HERE OUTPUTFILENAME

    output_file = output_path + station.replace(" ", "") + "_EVRF2007"


    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    sl_variables = change_to_evrf(sl_variables,country,datum)               # Funtion 6

    write_output(Headers,sl_variables,order,output_file)                     # Function 7


# Function 6
def change_to_evrf(sl_variables,country,datum):
    if datum=="BHS77":
        if country == "Estonia":
            to_add = Estonia
        elif country == "Latvia":
            to_add = Latvia
        elif country == "Lithuania":
            to_add = Lithuania
        elif country == "Russia":
            to_add = Russia
        elif country == "Poland":
            to_add = Poland
        else:
            print("Can't find country: ",country)
            return []
    else:
        try:
            to_add = Datum_dict[datum]
        except:
            print("Can't find datum: ",datum)
            return []

    new_variable=[]
    for ind in range(len(sl_variables)):
        new_variable.append([sl_variables[ind][0],sl_variables[ind][1]+to_add,sl_variables[ind][2]])

    return (new_variable)

# Function 7
def write_output(HeaderDict, sl_variables, order, outputfile):
    # Called by: process_file /Function 4  , Calls: -
    # Writes the output
    # Very much like in tgtools
    if len(HeaderDict.keys()) == 0:
        # Check for empty header, warn if so.
        print ("! Warning: empty header")
    Header = []
    for key in order:
        try:
            Header.append([key, HeaderDict[key]])
        except KeyError:
            Header.append([key, ""])
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

    # Writing headers
    file.writelines(output)
    file.write('\n')
    file.write('--------------------------------------------------------------\n')


    # Writing values
    date=[]
    time=[]
    slev=[]
    qual=[]

    for ii in range(len(sl_variables)):
        date.append((sl_variables[ii][0]).strftime("%Y-%m-%d"))
        time.append((sl_variables[ii][0]).strftime("%H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints=[]
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:6.4}\t{:3}\n".format(date[ind],time[ind],slev[ind],qual[ind]))

    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()

# Function 8
def check_country(filename):
    # Called by: Main, Calls: open_rfile()/ Function 1
    # Checks the country from the list if not given
    (data,okey)=open_rfile(station_country_list)
    if not okey:
        print("Couldn't open file:",station_country_list)
        exit("Check availability of station_country_list.")
    found=False
    for line in data:
        splitline=line.split()
        if filename==splitline[0]:
            country=splitline[1]
            found=True

    if not found:
        country="not_found"

    return country

####################################################################################################



def main():

    if GLstyle:
        (Header_dict,header_order)=get_headers(headerfilename_gl)        #gettin header model
    else:
        (Header_dict, header_order) = get_headers(headerfilename)


    (station_list,okey)=open_txtfile(station_country_list)
    if not okey:
        exit("Something went wrong opening station country list")

    stations=[]
    countries=[]
    for line in station_list:
        #print(line)
        stations.append((line.split()[0]))
        countries.append((line.split()[1]))
    #print(countries)


    os.chdir(path)
    for file in glob.glob("*.txt"):                 # Opens all that ends with .txt in the path folder one by one
        country = ""
        if file not in stations:
            print(file," Coudn't be found in station list")
        else:
            for ii in range(len(stations)):
                if file == stations[ii]:
                    country = countries[ii]
                    print(file, stations[ii], country)

            (sl_variables,Header_dict,station,okey,datum)=open_slfiles(file,Header_dict)
       #     country=check_country(file)                                                  # Function 8
                                                                                   # list has stations by the filename

        #    if not okey:
        #        print("Something went wrong opening Cmems file",file,"exiting program.")
        #        exit()
         #   process_file(file,sl_variables,Header_dict,header_order,station,country,datum) # Function 5






if __name__ == '__main__':
    main()