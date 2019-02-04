#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
import pandas as pd
from scipy import stats

path="/home/sanna/PycharmProjects/TGData_EVRF2007_txt/"
output_path = "/home/sanna/PycharmProjects/TGData_EVRF2007_txt_cleaned/"
#path="/home/sanna/PycharmProjects/Tests/"
#output_path="/home/sanna/PycharmProjects/Tests/Test/"
## Only works at the moment for non-gl header type


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
                        key ="Total observations"
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
                        key ="7 Nominal value"
                        value = splitline[3].strip()
                    elif splitline[0].strip() == "8":
                        key ="8 Interpolated"
                        value = splitline[2].strip()
                    elif splitline[0].strip() == "9":
                        key ="9 Missing value"
                        value = splitline[3].strip()
                    else:
                        print(splitline)
                #print(key,value)

            Headers[key] = value
            order.append(key)

    #print(Headers)
    #print(type(Headers))

    return Headers,order,datum

def prep_data(file,qual,headers,startd,endd):

    data_good = 0
    missing = 0
    no_qc = 0
    bad_data_pos = 0
    bad_data = 0
    prob_good = 0
    val_change = 0
    nominal = 0
    not_used = 0
    interpolated = 0
    #print(type(qual))

    #print(qual[0:20])

    for index in range(len(qual)):
        if qual[index]==1:
            data_good=data_good+1
        elif qual[index]==9:
            missing=missing+1
        elif qual[index] == 3:
            bad_data_pos = bad_data_pos + 1
        elif qual[index] == 4:
            bad_data = bad_data + 1
        elif qual[index] == 0:
            no_qc=no_qc+1
        elif qual[index] ==6:
            not_used = not_used + 1
        elif qual[index] == 2:
            prob_good= prob_good + 1
        elif qual[index] == 5:
            val_change= val_change + 1
        elif qual[index] == 7:
            nominal= nominal + 1
        elif qual[index] == 8:
            #print("haa")
            interpolated= interpolated + 1

        else:
            print("Weirdness in quality flag in  ", file, index, qual[index])

   # print(interpolated)

    headers["0 No QC performed"] = no_qc
    headers["1 Good"] = data_good
    headers["2 Probably good"] = prob_good
    headers["3 Bad pos. corr."] = bad_data_pos
    headers["4 Bad Data"] = bad_data
    headers["5 Value changed"] = val_change
    headers["6 Not used"] = not_used
    headers["7 Nominal value"] = nominal
    headers["8 Interpolated"] = interpolated
    headers["9 Missing value"] = missing
    headers["Total observations"] = len(qual)
    headers["Start time"] = startd
    headers["End time"] = endd

    #print("In file",file,":","Good data:", data_good," Missing Data:",missing," Bad Data:",bad_data," No QC:", no_qc, " Probably Good:",prob_good,
    #    " Value Changed:", val_change, " Nominal Value: ", nominal, " Interpolated:", interpolated)


    return headers




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
        # elif (len(new_date))>1:                                       # Wont work for first okey line since no other measurements exis
        #     if date[ind].strftime("%H") != new_date[-1].strftime("%H"):       # If no measurement from same hour allready exist
        #         if (clean_up_helper(date[ind])):  # If measurement is okey approksimation from at the hour measurement
        #             new_date.append(date[ind])
        #             new_slev.append(s_lev[ind])
        #             new_qual.append(q_label[ind])
        #         #else: # REMOVE THIS
        #         #    print("REMOVING bad approksimation from same hour as", new_date[-1], date[ind])
        #     elif date[ind].date() != new_date[-1].date() :           # If measurement allready from same hour, check if different date
        #         if (clean_up_helper(date[ind])):  # If measurement is okey approksimation from at the hour measurement
        #             new_date.append(date[ind])
        #             new_slev.append(s_lev[ind])
        #             new_qual.append(q_label[ind])
        #         #else: # REMOVE THIS
        #         #    print("REMOVING from same hour as", new_date[-1], date[ind])
        #     #else:  # REMOVE THIS
        #        # print("REMOVING from same hour as", new_date[-1],date[ind])
        # else:   # if first line case
        #     if (clean_up_helper(date[ind])):    # If measurement is okey approksimation from at the hour measurement
        #         new_date.append(date[ind])
        #         new_slev.append(s_lev[ind])
        #        new_qual.append(q_label[ind])
            #else:                # REMOVE THIS
                #print("REMOVING FIRST LINE",date[ind])

    #for ii in range(len(date)):


    print("Cleaned file now at length ",len(new_date))


    return new_date, new_slev, new_qual

def add_missing(date, s_lev, q_label, filename,inds_to_check,time_diff=3600):
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

        while date[(inds_to_check[ind])] - new_date[-1] >datetime.timedelta(seconds=time_diff):      # While difference is more than 1 hour put in  measurements
            new_date.append(new_date[-1]+datetime.timedelta(seconds=time_diff))
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
            if new_date[ind] - new_date[ind - 1] != datetime.timedelta(seconds=time_diff):
                bad.append(ind)
        print("Problems with lines ",bad," len of file ",len(new_date))
        for ii in range (len(bad)):
            print(new_date[bad[ii]-1],new_date[bad[ii]],new_date[bad[ii]+1])
        exit()                                                       # I want to exit this, since I need to fix this part if needed

    print("Added missing to file ",filename," new length of file ",len(new_date))

    return new_date, new_slev, new_qual


def write_output(sl_variables,Headers ,order, outputfile):
    # print(type(Headers))
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
    date = []
    time = []
    slev = []
    qual = []
    print("Writing length", len(sl_variables))

    for ii in range(len(sl_variables)):
        date.append((sl_variables[ii][0]).strftime("%Y-%m-%d"))
        time.append((sl_variables[ii][0]).strftime("%H:%M"))
        slev.append(str(sl_variables[ii][1]))
        qual.append(sl_variables[ii][2])
    prints = []
    for ind in range(len(date)):
        prints.append("{}\t{}\t{:6.4}\t{:3}\n".format(date[ind], time[ind], slev[ind], qual[ind]))

    for ind in range(len(sl_variables)):
        file.write(prints[ind])
    file.close()



def non_timely_inds(date,time_diff=3600):
    non_hour_ind = []
    for ind in range(1, len(date)):
        if date[ind] - date[ind - 1] != datetime.timedelta(seconds=time_diff):
            non_hour_ind.append(ind)

    return non_hour_ind

def roundTime(dt=None, roundTo=60):
    # From  Stack Overflow aswer by Le Droid (copied 23.1.2019)
    # https://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python/10854034#10854034

    """Round a datetime object to any time lapse in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None :
        dt = datetime.datetime.now()

    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)




def add_interp(dates,slevs,labels,interp_limit):
    print("Interpolating")

    my_pd=pd.DataFrame(slevs,index=dates)

    #print(slevs[0:30])
    my_intepolated = my_pd.interpolate(method="linear",axis=0,limit_direction="both",limit=interp_limit)              # linear interpolation, only interpolates value if 1 measurement/hour

    slevs_interp=list(my_intepolated.values.flatten())
    for ind in range(len(slevs)):
        if slevs[ind] != slevs_interp[ind]:
            if np.isnan(slevs[ind]) and np.isnan(slevs_interp[ind]) : # Don't regognise nan!=nan without a trick
                a=1
            else:
                #print("changed",slevs[ind], slevs_interp[ind], labels[ind])
                labels[ind]=8




   # print(slevs[0].type)
   # print(slevs[0:30])

    return slevs_interp,labels
###########################################3

def main():
    os.chdir(path)
    for filename in glob.glob("Porvoo_test_file.txt"):
        file = open (filename,"r")
        data = file.readlines()
        file.close()


        date=[]
        s_lev=[]
        q_label=[]

        (Headers, order, datum_old) = get_headers(data[0:22])
        if datum_old == "msl" or datum_old == "MSL" :
            print("Warning - Datum MSL in file ", filename)


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
        min_interval_10 = False
        min_interval_15 = False
        min_interval_5  = False
        really_not_good = False

        for ind in range(len(date)):
            if date[ind].strftime("%M") !="00":
                problematic_file = True
                if date[ind].strftime("%M") in ("15","30","45"):
                    min_interval_15 = True
                elif date[ind].strftime("%M") in ("10","20","30","40","50"):
                    min_interval_10 = True
                elif date[ind].strftime("%M") in ("05","10","15","20","25","30","35","40","45","50","55"):
                    min_interval_5 = True
                else:
                    really_not_good =True


        if not really_not_good:
            if min_interval_5:
                non_5inds=non_timely_inds(date,time_diff=300)
                (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename, non_5inds, 300)
                (s_lev, q_label) = add_interp(date, s_lev, q_label, 10)
            elif min_interval_10 :
                non_10inds=non_timely_inds(date,time_diff=600)
                (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename, non_10inds, 600)
                (s_lev, q_label) = add_interp(date, s_lev, q_label,5)
            elif min_interval_15 :
                non_15inds = non_timely_inds(date, time_diff=900)
                (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename, non_15inds, 900)
                (s_lev, q_label) = add_interp(date, s_lev, q_label,3)

            if problematic_file:
                print("Problematic file with interval 5/10/15 ",min_interval_5,min_interval_10,min_interval_15)

        else:
            print("File has strange timestamps, rounding to nearest 5 min interval ", filename)
            for tt in range(len(date)):
                date[tt]=roundTime(date[tt],300)    # Rounding time to nearest 5 min
            non_5inds = non_timely_inds(date, time_diff=300)
            (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename, non_5inds, 300)
            (s_lev, q_label) = add_interp(date, s_lev, q_label,10)


       # print(date[0:20])


        #print("1:",len(date))

        if problematic_file:
            print("Problematic file, timeinterval not 1 hour ", filename)       #Clearing up multiples of same hour
            #print(date[0:10])
            (date,s_lev,q_label)=clean_up(date,s_lev,q_label,filename)

        #print("2",len(date))

        non_hour_ind=non_timely_inds(date,time_diff=3600)



        if len(non_hour_ind)!=0:
            print("Missing measurements ",filename)                             # Adding missing measurements as nan imputs
            (date, s_lev, q_label) = add_missing(date, s_lev, q_label, filename,non_hour_ind,3600)

        #print("3", date[0:3], len(date))


        if ((not problematic_file) and non_hour_ind == []):
            print("Good file",filename)

        output_file = output_path + filename.replace(" ", "")

        if not os.path.exists(output_path):  # Making the output folder if needed
            os.makedirs(output_path, exist_ok=True)


        tg_data=[]

        #print(date.shape)
        Headers=prep_data(filename,q_label,Headers,date[0],date[-1])

        for ind in range(len(date)):
            tg_data.append([date[ind],s_lev[ind],q_label[ind]])


        write_output(tg_data,Headers,order,output_file)





if __name__ == '__main__':
    main()