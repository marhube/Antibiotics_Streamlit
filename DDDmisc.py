print('Er inne i DDDmisc.py')
#
import pandas as pd
import numpy as np
import os
import pyodbc
import time
import sys# For sys.exit()
import pickle
import re # For regex
from functools import partial
#
#********** Start laster inn hjelpekode
exec(open("TotalTools.py", encoding='utf-8').read())
exec(open("ATC_Tools.py", encoding='utf-8').read())
exec(open("IndicationGroupTools.py", encoding='utf-8').read())
exec(open("NarrowBroadTools.py", encoding='utf-8').read())
# *********** Endfirst read sql code
#Note: By default sort in descending order
#More info at https://stackoverflow.com/questions/3940128/how-do-i-reverse-a-list-or-loop-over-it-backwards
def getDistinctPeriods(df,desc = True):
    print(f'Er nå inne i getDistinctPeriods')
    periods = sorted(list(set(df.iloc[:, 0].tolist())),reverse = desc)
    #
    return periods
#
def getAllLevels(df,Grouping):
    allLevels = sorted(df[Grouping].unique().tolist())
    return(allLevels)
#
def classMapper(uiName):
    #Extract last 4 columns
    className = None
    if  uiName.upper() in ["TOTAL","ATC3"]:
        className = uiName
    elif uiName.lower().startswith('indi'):
        className = "IndicationGroup"
    elif uiName.lower().startswith('bred'):
        className = "NarrowBroad"
    #
    return className
#