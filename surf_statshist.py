#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import numpy as np
import os, glob
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt



path="/home/sanna/PycharmProjects/Surfaces/TG/2007/01/"
#outputpath="/home/sanna/PycharmProjects/Hists/TG/"

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



    data=pd.read_csv(filename,skiprows=6,sep="\t",header=None,na_values="nan")

    print(data.shape)








def main():
    os.chdir(path)
    for file in glob.glob("*00.txt"):
        process_file(file)


if __name__ == '__main__':
    main()
