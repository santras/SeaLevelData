#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import numpy as np
import os, glob
from scipy import stats
from PIL import Image
from dateutil.rrule import rrule, HOURLY


outputpath="/home/sanna/PycharmProjects/PLOTS/Combined_Maps/2016/"
inputfolder1="/home/sanna/PycharmProjects/Surfaces/Model/2016/"
inputfolder2="/home/sanna/PycharmProjects/Surfaces/TG/2016_cut/all/Plots/"

start_time=datetime.datetime(2016,1,1,0)
end_time=datetime.datetime(2016,1,31,23)





def main():

    if not os.path.exists(outputpath):  # Making the output folder if needed
        os.makedirs(outputpath, exist_ok=True)

    hourly_list=(list(rrule(HOURLY,dtstart = start_time,until=end_time)))

    for timestep in hourly_list:


        # creating image names
        new_file = outputpath+"surf_pic_test_"+timestep.strftime("%Y%m%d_%H") +".png"
        old_file_1 = inputfolder2+"tg_surf_"+timestep.strftime("%Y%m%d_%H")+".png"
        old_file_2 = inputfolder1 + "model_surf_"+timestep.strftime("%Y%m%d_%H") + ".png"
        #print (new_file,old_file_1,old_file_2)


        # opening the images
        new_image = Image.new("RGB",(1280,480))
        image_1 = Image.open(old_file_1)
        image_2 = Image.open(old_file_2)

        # pasting to new_image
        new_image.paste(image_1,(0,0))
        new_image.paste(image_2,(640,0))

        # saving
        new_image.save(new_file)



    return







if __name__ == '__main__':
    main()