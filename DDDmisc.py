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
# *********** Endfirst read sql code
#Note: By default sort in descending order
#More info at https://stackoverflow.com/questions/3940128/how-do-i-reverse-a-list-or-loop-over-it-backwards
def getDistinctPeriods(df,desc = True):
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