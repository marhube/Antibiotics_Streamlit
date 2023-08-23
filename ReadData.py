import pandas as pd
import numpy as np
import os
import pyodbc
import time
import sys# For sys.exit()
import re
import pickle
import cv2 # Memo to self: Install with pip install opencv-python
import locale # For month names
import calendar
#
#********** Start read auxiliary code
import SQL_Tools
# *********** End read auxiliary code

#******* Start fetch data and image/FHI-logo
#
#* create locale month names
def get_month_names():
    locale.setlocale(locale.LC_ALL, '')
    monthNames = list(calendar.month_name)[1:]
    return monthNames
#
def get_image(filename = "./Image/FHI_Logo.PNG"):
    img = cv2.imread(filename, 1)
    image = np.array([img])
    return image
#

