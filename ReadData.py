print('Er inne i ReadData.py')
#
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
exec(open("SQL_Tools.py", encoding='utf-8').read())
# *********** End read auxiliary code

#******* Start fetch data and image/FHI-logo
#
monthly_data = get_table_from_db(annual=False)
annual_data = get_table_from_db(annual = True)
#
#locale.setlocale(locale.LC_ALL, '')
#monthNames = list(calendar.month_name)[1:]
#with open(month_name_file,'wb') as file:
#    pickle.dump(monthNames, file)  
#
month_name_file = "../Data/month_name.pickle"
with open(month_name_file,'rb') as file:
    monthNames = pickle.load(file)  
# End create locale month names

Groupings = list(monthly_data.columns)[-4:]
CountVariable = [col for col in list(annual_data.columns) if re.search("^DDD.*1000",col) is not None][0]
#******* End fetch data
#Memo to self: Useful info from https://discuss.streamlit.io/t/change-font-size-and-font-color/12377/3
#******** Start fetch FHI logo
filename = "./Image/FHI_Logo.PNG"
img = cv2.imread(filename, 1)
image = np.array([img])
#*********  End fetch FHI logo


#* End create locale month names