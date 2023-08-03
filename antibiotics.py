import streamlit as st
import sys # For sys.exit()
import os
import pandas as pd
import numpy as np
import pickle
import re
import calendar
from itertools import compress 
import matplotlib.pyplot as plt
import io
import xlsxwriter
#********* Start importing modules for graphics
from plotnine import *
#********* End importing modules for graphics
#
#********** Start importing auxiliary code
exec(open("DDDmisc.py", encoding='utf-8').read())
# *********** End importing auxiliary code
#********* Start reading data and FHI-logo
exec(open("ReadData.py", encoding='utf-8').read())
#********* End reading data and FHI-logo
#
image_title = '<p style="font-family:sans-serif; color:Black; font-size: 42px;">Bruk av antibiotika i Norge</p>'
st.markdown(image_title, unsafe_allow_html=True)
st.image(image, channels="BGR")
# Using "with" notation
#
allMonthlyPeriods = getDistinctPeriods(monthly_data)
nonUniqueYears = [int(year) for year in  np.floor(np.array(allMonthlyPeriods)/100)]
# Create an empty container to store input from user (later forwarded to graph render)
#Initialize position with the default value 'stack'
graphInputDict = {'CountVar': CountVariable,'position': 'stack'}
updateButton = False
downloadButton = False
plotData = None
#
with st.sidebar:
    graphInputDict['Grouping'] = st.selectbox(label = "Velg gruppeinndeling",options = Groupings)
    dataResolution = st.radio(
        "Velg tidsoppdeling",
        ("månedlig", "årlig")
    )
    #
    startYearOptions = None
    if dataResolution == "årlig":
        startYearOptions = getDistinctPeriods(annual_data)
        graphInputDict['annual'] = True
        graphInputDict['allData'] = annual_data
    else:# Memo to self: Need to extract unique ("year parts")
        startYearOptions = sorted([int(elem) for elem in set(nonUniqueYears)],reverse = True)  
        graphInputDict['annual'] = False
        graphInputDict['allData'] = monthly_data     
    #
    graphInputDict['startYear'] = st.selectbox(label = "Velg startår",options = startYearOptions)
    #End year needs to be >= start year
    endYearOptions = sorted([elem for elem in startYearOptions if elem >= graphInputDict['startYear']],reverse = True)
    graphInputDict['endYear']  = st.selectbox(label = "Velg sluttår",options = endYearOptions)
    #
    #Memo to self: From https://stackoverflow.com/questions/2829528/whats-the-scope-of-a-variable-initialized-in-an-if-statement
    # Variables defined inside if are visible outside of the control statement
    #Memo to self: More info about compress  https://stackoverflow.com/questions/18665873/filtering-a-list-based-on-a-list-of-booleans
    if dataResolution == "månedlig":
        # Start choose "start month" and "end month"
        #Extract "month-parts" from months in "allMonthlyPeriods" where the "year-part" is equal to startYear
        equalsStartYear = [year == graphInputDict['startYear'] for year in  nonUniqueYears]
        equalsEndYear = [year == graphInputDict['endYear'] for year in  nonUniqueYears]
        startMonthOptions = sorted(list(compress(allMonthlyPeriods,equalsStartYear))) 
        #Memo to self: Indexes in Python start on 0
        startMonthNameOptions = [monthNames[(period % 100)-1] for period in startMonthOptions]
        startMonth = st.selectbox(label = "Velg startmåned",options =  startMonthNameOptions) 
        # Memo to self: startMonth as input to graph render needs to be on the format YYYYMM
        #Memo to self: We have to add 1 since indexes in Python begin on 0
        graphInputDict['startMonth'] =  (100 * graphInputDict['startYear']) + (monthNames.index(startMonth) + 1)
        # Memo to self: If "endYear" equals "startYear" then endMonth has to be greater than or equal to startMonth
        endMonthOptions = sorted(
            [period for period in list(compress(allMonthlyPeriods,equalsEndYear)) if period >= graphInputDict['startMonth']],
             reverse = True
             )
        #
        endMonthNameOptions = [monthNames[(period % 100)-1] for period in endMonthOptions]
        endMonth = st.selectbox(label = "Velg sluttmåned",options = endMonthNameOptions)
        #
        graphInputDict['endMonth'] =  (100 * graphInputDict['endYear']) + (monthNames.index(endMonth)  + 1)
        # End choose "start month" and "end month"
        #  Start choose graph type
        # Memo to self: The first option is selected
        graph_type_monthly = st.radio("Stablede kolonner",("Ja", "Nei"),index = 1)
        graphInputDict['curveType'] = "area" if graph_type_monthly == "Ja" else "line"
        #
        if graph_type_monthly == "Nei":
            graph_type_monthly = st.radio("Inkludér 12. mnd gjennomsnitt",("Ja", "Nei"),index = 0)
            graphInputDict['run_avg'] = (graph_type_monthly == "Ja")       
    # Memo to self: The "elif" covers annual (year-by-year) plots
    elif graphInputDict['Grouping'] != Groupings[0]:
        graph_type_annual = st.radio("Stablet eller side-ved-side",("stablet", "side-ved-side"),index = 0)
        if graph_type_annual == "side-ved-side":
            graphInputDict['position'] = 'dodge'
        #
    # 
    allVariableLevels = getAllLevels(graphInputDict['allData'],Grouping = graphInputDict['Grouping'])
    if graphInputDict['Grouping'] == Groupings[0]:
        graphInputDict['variables'] = allVariableLevels                
    else:
        variables = []
        for ind,var in enumerate(allVariableLevels):
            includeVar = st.checkbox(label = var,value = True,key = ind)
            if includeVar:
                variables.append(var)
        #
        graphInputDict['variables'] = variables          
#
    # Time to generate plot
    updateButton = st.button("Oppdater figur") 
    dataFormat = st.radio("Velg format for nedlasting:",("csv", "excel"),index = 0)
#More info on plotnine in Streamlit: https://discuss.streamlit.io/t/support-for-plotnines-ggplot/3535
st.cache_resource(ttl = 1000)
def calcPlotInfo(graphInputDict):
    # Create graph input dictionary
    plotObj = eval(classMapper(graphInputDict['Grouping']))(graphInputDict)
    return plotObj.gg2
#
st.cache_data(ttl = 1000)
def extractData(gg2):
    return gg2.data
#
if updateButton:    
    gg2 = calcPlotInfo(graphInputDict)
    plotData = extractData(gg2)
    st.pyplot(ggplot.draw(gg2))
#
#Ask user if he/she wants to download data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = False).encode('utf-8')
#from https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/26
def convert_df_to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer,index = False,sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()    
    #writer.close()
    return processed_data
#
if plotData is not None:
    with st.sidebar:
        fileExtension = "csv" if dataFormat == "csv" else "xlsx"
        fileName = f"{graphInputDict['Grouping']}.{fileExtension}"
        if dataFormat == "csv":   
            mime = 'text/csv'
            data = convert_df_to_csv(plotData)            
            #
            st.download_button(
                label = "Last ned data som kommaseparert fil",
                data = data,
                file_name = fileName,
                mime = mime        
                )
        #
        else:
            fileExtension = "xlsx" 
            mime="application/vnd.ms-excel"
            data = convert_df_to_excel(plotData)
            #
            st.download_button(
                label = "Last ned data som regneark",
                data = data,
                file_name = fileName,
                mime = mime        
                )            
        # 
    #
#
