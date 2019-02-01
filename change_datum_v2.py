#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats



# The purpose of this code is to take files and change the height refrence frame to EVRF07




station_country_list=('station_countries.txt')                # Stations by countries txt file, should be in the data directory
path="../TGData_txt//"                        # Path for the original data file folder, script goes throuh all .txt files in the folder
output_path= path +"../TGData_EVRF2007_txt//"      # Outputpath
datum_new="EVRF2007"                                                 # The new datum
fin_change_table="/home/sanna/PycharmProjects/SeaLevelData/Fin_MSL_NN2000_chart_1931_2018.txt"

# Changes in cm from https://evrs.bkg.bund.de/Subsites/EVRS/EN/Projects/HeightDatumRel/height-datum-rel.html
#BHS77 /Kronstadt datum
Estonia=19.0
Latvia=15.0
Lithuania=12.0
Poland=17.0
Russia = 25.0     # Lähde Jaakko Mäkinen( Ekman 1999 Marine Geodecy)


# Amsterdam (NAP) Datum
Datum_dict={}
Datum_dict["DHHN92"] = 1.0
Datum_dict["DVR90"] = 0.0
Datum_dict["RH2000"] = -1.0
Datum_dict["NN2000"] = -1.0
#Datum_dict["TGZ"] = -462.3 # Testing if this would work...
#Datum_dict["Unknown"] = -488 # Testing if this would work... probably needs some tweeking (-500 + lithuania +12)

# Kronstadt datum
Datum_dict["SNN76"] = 16.0
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

def get_headers(data):

    # Reads a headers that contains the header titles and the order they should be in in the final header

    Headers = {}
    order=[]
   # print(type(Headers))

    for line in data:                 # Reads the lines of the file into a dictionary
        line_s=line.strip()
        #print(line_s)
        if not (line_s == "" or line_s[0] == "#"):
            if " " in line_s:
                splitline = line_s.split()
                value=""
                if len(splitline) <= 2:
                    #print(splitline)
                    if splitline[0].strip() == "Datum":
                        datum=splitline[1].strip()

                    key = splitline[0].strip()
                    value = splitline[1].strip()
                else:
                    if splitline[0].strip() == "Time":
                        key ="Time system"
                        value = splitline[2].strip()
                    elif splitline[0].strip() == "Total":
                        key ="Total Observations"
                        value = splitline[2].strip()
                    elif splitline[0].strip() == "Station":
                        key = "Station"
                        for jj in range(1,len(splitline)):
                            value = value+(splitline[jj].strip())+" "
                    elif splitline[0].strip() == "Start":
                        key ="Start time"
                        value = splitline[2].strip()+" " +splitline[3].strip()
                    elif splitline[0].strip() == "End":
                        key = "End time"
                        value = splitline[2].strip() + " " + splitline[3].strip()
                    elif splitline[0].strip() == "Quality":
                        key ="Quality flags CMEMS"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "0":
                        key ="0 No QC performed"
                        value = splitline[4].strip()
                    elif splitline[0].strip() == "1":
                        key ="1 Good"
                        value = splitline[2].strip()
                    elif splitline[0].strip() == "2":
                        key ="2 Probably good"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "3":
                        key ="3 Bad pos. corr."
                        value = splitline[4].strip()
                    elif splitline[0].strip() == "4":
                        key ="4 Bad Data"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "5":
                        key ="5 Value changed"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "6":
                        key ="6 Not used"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "7":
                        key ="7 Nominal values"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "8":
                        key ="8 Interpolated "
                        value = splitline[2].strip()
                    elif splitline[0].strip() == "9":
                        key ="9 Missing values"
                        value = splitline[3].strip()
                    else:
                        print(splitline)
                #print(key,value)

            Headers[key] = value
            order.append(key)

    #print(Headers)
    #print(type(Headers))

    return Headers,order,datum


def open_slfiles(file):

    # Opens sealevel txt  files, then reads the data and updates the header
    (data,okey) = open_txtfile(file)
    if not okey:
        print("Couldn't open file ",file)



    #for ii in range(0,22):
    #    print(data[ii])

    if not (data[23][0]=="-"):    # juts an extra check that header size is ok  ### For gl 20
        print("Header size of file is not expected in file: ",file)
        exit()
    else:
        (Headers,order,datum_old)=get_headers(data[0:22])  ### Needs to be 19 ?for gl-data type
        #print(type(Headers))

    print("Original file ",file," length", len(data[24:]))

    date=[]
    time=[]
    slev=[]
    qual=[]
    for ind in range(24,len(data)):  ############### For gl 21
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
        #else                                                               # Some files were not hourly even if metadata said so
        #     print(thisdate)

    #print(variables[0:5])

    return variables, Headers,order,datum_old


def update_header(Headers,datum):
    # Updates header info
    Headers["Datum"] = datum

    return Headers


def process_file(filename,sl_variables,Headers,order,country,datum_old):
    # Makes an output folder if it doesen't exist and creates needed variables for header, then it updates and orders
    # the header and finally writes the output of spesified time period.

    # HERE OUTPUTFILENAME

    output_file = output_path +filename.replace(" ", "")


    if not os.path.exists(output_path):                             # Making the output folder if needed
        os.makedirs(output_path, exist_ok=True)

    #print(sl_variables[0:5])
    sl_variables = change_to_evrf(sl_variables,country,datum_old,Headers,filename)
    if sl_variables == []:
        print("Something wrong with conversion, for file ",filename)
    #print(sl_variables[0:5])

    write_output(sl_variables,Headers,order,output_file)



def change_to_evrf(sl_variables,country,datum,Headers,filename):


    if country == "Finland":
        if datum == "msl" or datum == "MSL":
            to_add = Datum_dict["NN2000"]

            msl_nn2000 = get_fin_change_nn2000(sl_variables,filename)

            update_header(Headers, datum_new)
            new_variable = []
            for ind in range(len(sl_variables)):
                new_variable.append([sl_variables[ind][0], sl_variables[ind][1] + msl_nn2000[ind]+ to_add, sl_variables[ind][2]])

            return (new_variable)

        elif datum == "NN2000":
            to_add = Datum_dict[datum]
        else:
            print("Can't find datum: ", datum, country, filename)
            return []

    elif datum=="BHS77":
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
            print("Can't find datum: ",datum,country,filename)
            return []

    update_header(Headers,datum_new)
    new_variable=[]
    for ind in range(len(sl_variables)):
        new_variable.append([sl_variables[ind][0],sl_variables[ind][1]+to_add,sl_variables[ind][2]])

    return (new_variable)

def get_fin_change_nn2000(sl_variable,filename):

    # Opening change table
    (changedata,okey)=open_txtfile(fin_change_table)
    if not okey:
        print("Coulnd't open file for Finnish msl conversions to NN2000")
        return

    #checking index from filename
    index=check_station(filename)
    if index == []:
        print("Warning, coudn't change datum for, missing index for search",filename)

    msl_to_nn2000=[]
    aa=""

    #print(changedata)
    for ii in range (len(sl_variable)):
        #print(sl_variable[ii][0].date().year) # the year
        #print (changedata[(4+(int(sl_variable[ii][0].date().year)-1931))])                # the line    # year 1931 = line 1
        year_= (sl_variable[ii][0].date().year)
        line_ind= 1 + int(year_)-1931
        line=changedata[line_ind]
        splitline=line.split()
        aa=(splitline[index+1])             # correct item  from chart
        aa=((float(aa.strip()))*0.1)       # change to cm
        msl_to_nn2000.append(aa)
        #print(aa)

    #print (msl_to_nn2000)
    #print(len(msl_to_nn2000),len(sl_variable))
    return msl_to_nn2000

def check_station(name):
    # Matching the names of the stations to the corresponding column in the file for the conversion
    name=name[:-4].strip()
    if name=='Kemi':
        ind=0
    elif name=='Oulu':
        ind=1
    elif name=='Raahe':
        ind=2
    elif name=='Pietarsaari':
        ind=3
    elif name=='Vaasa':
        ind=4
    elif name=='Kaskinen':
        ind=5
    elif name=='Pori' or name=='Mäntyluoto' or name=='Mantyluoto':
        ind=6
    elif name=='Rauma':
        ind=7
    elif name=='Turku':
        ind=8
    elif name=='Föglö' or name=='Foglo' or name=='Degerby' or name=='FÃ¶glÃ¶':
        ind=9
    elif name=='Hanko':
        ind=10
    elif name=='Helsinki':
        ind=11
    elif name=='Porvoo':
        ind=12
    elif name=='Hamina':
        ind=13
    else:
        print("Couldn't find station "+name)
        return []
    return ind


def write_output(sl_variables,Headers ,order, outputfile):

    #print(type(Headers))
    # Writes the output
    # Very much like in tgtools
    if len(Headers.keys()) == 0:
        # Check for empty header, warn if so.
        print("! Warning: empty header")
    Header = []
    # print(order)
    # print(HeaderDict)
    for key in order:
        try:
            Header.append([key, Headers[key]])
        except KeyError:
            Header.append([key, ""])
    # print(Header)
    output = []
    for line in Header:
        # print(line)
        # Loop through all header lines
        if not len(line) == 2:
            # Header line should only have to elements (key and value)
            print("! Warning: broken header line:", line)
        else:
            # If there's nothing in either position of the header,
            # replace it with an empty string.
            if line[0] == None:
                line[0] = ""
                print("! Warning: nameless header field: ", line)
            if line[1] == None:
                line[1] = ""
                print("! Warning: valueless header field: ", line)
            # Header name length
            if len(line[0]) > 20:
                print('! Warning: header name too long: "%s". Cropped to 20 characters.' % (line[0]))
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
    print("Writing length",len(sl_variables))

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


####################################################################################################



def main():


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
        print(file," starting")
        country = ""
        if file not in stations:
            print(file," Coudn't be found in station list")
        else:
            for ii in range(len(stations)):
                if file == stations[ii]:
                    country = countries[ii]
                    #print(file, stations[ii], country)

            (sl_variables, Headers, order,datum_old)=open_slfiles(file)
            #print(type(Headers))
            process_file(file,sl_variables,Headers,order,country,datum_old)
            print(file,"finnished")







if __name__ == '__main__':
    main()