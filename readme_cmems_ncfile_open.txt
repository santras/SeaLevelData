cmems_nc_file_open.py
The purpose of this code is to change Copernicus CMEMS Tide Gauge Sea Level Data from NetCDF files into txt-files.
Makes header from a file that contains the header titles and the order, location of the file header.txt / header_cmems.txt can be
changed from the beginning of this file.

About the script.
The beginning of the script contains some global variables for the scrip. Main function is last function in the list.

TOP:
Have two different options for output style, "GL"-styled output that is used in FGI (Paikkatietokeskus) and another txt file style.
The main difference between the styles is the quality flags used with each type. The "Gl"-style has it's own quality flags that are
changed from the original CMEMS data quality flags as follows bellow. On the other type of outputfile, CMEMS quality flags are used.
Change between the types of output can be defined with boolean variable called GLstyle that can be changed from the beginning of the
script. The style of output is defined in a textfile. Name (and location) of the text file is also defined in the beginning of the
script with variables called headerfilename and headerfilename2. Beginning of the file also includes path and outputpath variables.
Should be noted that file goes through all nc files in the path folder.

The output is in cm.
At the moment there is no function to deal if time differece between measurements is not what is expected.
At the moment there is no function for sorting data is the order of measurements is wrong.

Quality flag change between cmems and gl-style
Copernicus tide gauge data quality flags        GL style quality flags
0= No QC performed                              3 = Unknown / source does not specify
1= Good data                                    1 = Known to be good
2 = Probably good data                          3 = Unknown / source does not specify
3 = Bad data that are potentially correctable   9 = Gap in data
4 = Bad data                                    9 = Gap in data
5 = Value changed                               3 = Unknown / source does not specify
6 = Not used                                    3 = Unknown / source does not specify
7 = Nominal value                               9 = Gap in data
8 = Interpolated value                          2 = Interpolated data
9 = Missing value                               9 = Gap in data