print('Er inne i PlotGenerator.py')
#
import pandas as pd
import numpy as np
import os
import time
import sys# For sys.exit()
import datetime as dt
import math
#
# ********** Start importing modules for graphics
import matplotlib
import colorbrewer
# ********** End importing modules for graphics

#********** Start reading auxiliary code
#********** End reading auxiliary code
# Class for creating a "ggplot2"-object that can be plotted
class PlotGenerator:
    def __init__(self,graphInputDict):
        self.allData = graphInputDict['allData']
        self.annual = graphInputDict['annual']
        self.CountVar = graphInputDict['CountVar']
        self.Grouping = graphInputDict['Grouping']
        self.startYear = graphInputDict['startYear']
        self.endYear = graphInputDict['endYear']
        self.variables = graphInputDict['variables']
        # Memo to self: Initialize with default values
        self.runAverage = False
        self.firstPeriod = self.startYear
        self.lastPeriod = self.endYear 
        # Memo to self: "Total counts don't have a paramete"
        if self.annual:
            self.position = graphInputDict['position']                   
        else:
            self.startMonth = graphInputDict['startMonth']
            self.endMonth = graphInputDict['endMonth']           
            self.curveType = graphInputDict['curveType']            
            self.firstPeriod = self.startMonth
            self.lastPeriod = self.endMonth
            # Memo to self: Running average not implemented for stacked plots
            if self.curveType == "line":
                self.runAverage = graphInputDict['run_avg']                           
        #    
        self.UnfilteredSummations = self.createUnfilteredSummations()
        self.levelRanks = self.createLevelRanks()
        self.Summations = self.createSummations() 
        self.plotData = self.createPlotData()
        self.title = self.getTitle()
        self.ylab = self.getYlab()
        # Create "gg2"- object that can be used to create plots
        if self.annual:
            self.gg2 = self.createAnnualPlot() 
        else:
            self.gg2 = self.createMonthlyPlot()                        
    #
    # Some categories of antibiotics are not delivered every month. For practical reasons we 
    # need to have every combination of every time period and category in our dataset. 
    # replaceUnobserved replaces the value 0 for those months when there are not deliveries
    # of 
    @staticmethod
    def replaceUnobserved(df,replaceVal = 0):
        vars = list(df.columns)[0:2]
        # Create dataframe with all combinations of time period and category (cross join)
         # Replace na in the other(s) columns of expandedFrame with replaceVal
        expandedFrame = (pd.DataFrame({vars[0] : df[vars[0]].unique()}).
                         merge(pd.DataFrame({vars[1] : df[vars[1]].unique()}), how='cross').
                         merge(df,how='left',on = vars).fillna(replaceVal)
                         )
        #
        return expandedFrame
    #   
    def createUnfilteredSummations(self):
        timeCol = list(self.allData.columns)[0]
        # Memo to self: Useful info about "why reset_index" at 
        # https://stackoverflow.com/questions/20122521/is-there-an-ungroup-by-operation-opposite-to-groupby-in-pandas
        df = self.allData[[timeCol,self.Grouping,self.CountVar]].groupby([timeCol,self.Grouping]).sum().reset_index()
        df = PlotGenerator.replaceUnobserved(df,replaceVal = 0)
        return df
    # Ranks in descending order each "level" depending on the median value
    def createLevelRanks(self):
        df = self.UnfilteredSummations
        #Memo to self: Need parenthesi around each "bitwise and" condition
        # https://stackoverflow.com/questions/36921951/truth-value-of-a-series-is-ambiguous-use-a-empty-a-bool-a-item-a-any-o
        # Memo: Create "row number" 
        levelRanks = (df[(df.iloc[:,0] >=self.firstPeriod) & (df.iloc[:,0] <= self.lastPeriod)].groupby(self.Grouping).
                      median().sort_values(self.CountVar,ascending = False)
        )
        levelRanks =  levelRanks.assign(row_number=range(len(levelRanks)))
        return levelRanks
    #
    def createSummations(self):
        df = self.UnfilteredSummations
        summations = df[(df.iloc[:,0] >=self.firstPeriod) & (df.iloc[:,0] <= self.lastPeriod) & df.iloc[:,1].isin(self.variables)].copy()
        return summations
    #
    def createGroupFactor(self,df):
        # Memo to self: Must exclude factors that are not among the selected variables
        groupFactor = pd.Categorical(
            df[self.Grouping],
            categories = [self.levelRanks.index[i] for i in range(len(self.levelRanks.index)) 
                          if self.levelRanks.index[i] in self.variables],
            ordered=True)
        return groupFactor
    #
    #Memo to self: More info on "Python factors": https://byuidatascience.github.io/python4ds/factors.html
    # Mmemo to self: Need to make copy before subsetting and assigning
    def createAnnualPlotData(self):            
        annualDDD = self.Summations[(self.Summations.iloc[:,0] >= self.startYear) & (self.Summations.iloc[:,0] <= self.endYear)].copy()
        annualDDD['yearFactor'] = pd.Categorical(annualDDD.iloc[:,0],ordered=True)
        annualDDD['groupFactor'] = self.createGroupFactor(annualDDD)
        annualDDD['firstDayOfYear'] = annualDDD.iloc[:,0].map(lambda x : dt.date(x,1,1))                      
        return annualDDD
    #
    @staticmethod # Memo to be self: Must be called group-wise
    def LagRollMean(series,window,lag = 1):
        lag_roll_mean = ([np.nan] * lag) + list(series.rolling(window).mean())[:-lag]
        return lag_roll_mean
    #
    def createMonthlyPlotData(self):
        # Need one year more (earlier) data in order to create running average
        startMonth = self.startMonth
        plotStart = startMonth
        if self.runAverage :
            startMonth = startMonth - 100
        ##Memo to self: Will later find it practical to have 
        df = self.UnfilteredSummations.copy() 
        monthlyDDD = df[(df.iloc[:,0] >= startMonth) & ((df.iloc[:,0] <=self.endMonth))  & df.iloc[:,1].isin(self.variables)].copy()
        #Create moving average (12 months)
        #More info: https://www.geeksforgeeks.org/how-to-calculate-moving-averages-in-python/
        # and https://itecnote.com/tecnote/python-pandas-how-to-assign-groupby-operation-results-back-to-columns-in-parent-dataframe/
        if self.runAverage:
            #Memo to self: Much easier to change the index of pandas Dataframe than a pandas Series
            # Memo to self: Want rolling mean of previous 12 months (not include the current want)
            # Memo to self  [:-1] Remove the last element of a list
            #Memo to self: For grouped transformations we need to call "transformation function" indirectly
            # via "tranform"
            smoothSeries = monthlyDDD.groupby(self.Grouping)[self.CountVar].transform(
                func = PlotGenerator.LagRollMean,
                window = 12,
                lag = 1
            )
            #
            monthlyDDD = monthlyDDD.join(pd.DataFrame({'smoothDDD' : smoothSeries},index = smoothSeries.index))
            monthlyDDD = monthlyDDD[(monthlyDDD.iloc[:,0] >= plotStart)]            
        # Memo to self: Since the module plotnine doesn't support scale_x_date, only scale_x_datetime
        # 'firstMonthDay' needs to be a datetime, note a date
        monthlyDDD['firstMonthDay'] = monthlyDDD.iloc[:,0].map(
            lambda x : dt.datetime(year = math.floor(x/100),month = x % 100, day = 1)
            )
        #
        monthlyDDD['groupFactor'] = self.createGroupFactor(monthlyDDD)
        # ********* Fortsette her med å lage faktorer!!!!!!
        return monthlyDDD 
    #
    def createPlotData(self):
        data = self.createAnnualPlotData() if self.annual else self.createMonthlyPlotData()
        return data
    #
    #Needs to be implemented by inherenting classes
    def getTitle(self):
        pass
    #    
    @staticmethod
    def getYlab():
        ylab = "DDD/1000 innbyggere/døgn"
        return ylab 
    #
    @staticmethod
    #From https://www.codespeedy.com/convert-rgb-to-hex-color-code-in-python/
    def rgb_to_hex(rgb,hashTag = True):
        hexCol =  '%02x%02x%02x' % rgb
        if hashTag:
            hexCol = "#" + hexCol            
        return hexCol
    #Memo to self: Need to return a dictionary that should be fed into scale_fill_manual
    def customizeBrewer(self,palette):
        # More info https://www.geeksforgeeks.org/python-convert-two-lists-into-a-dictionary/ and (especially
        # https://www.codespeedy.com/convert-rgb-to-hex-color-code-in-python/) and
        #https://stackoverflow.com/questions/1167398/python-access-class-property-from-string
        # using dictionary comprehension  to convert lists to dictionary
        colorValues = getattr(colorbrewer,palette)[self.levelRanks.shape[0]]
        #Memo: Nee to 
        colorDict = {self.levelRanks.index[i]: self.rgb_to_hex(colorValues[i],hashTag = True) 
                     for i in range(len(colorValues)) if self.levelRanks.index[i] in self.variables } 
        return colorDict
    #   Needs to be implemented by inherenting classes
    def getColors(self):
        pass
    # 
    def createAnnualPlot(self):
        customColors = self.getColors()
        #
        annual_plot =  (ggplot(self.plotData, aes(x="yearFactor",y = self.CountVar, fill = "groupFactor")) 
            + geom_bar(stat="identity",position = self.position)
            + scale_fill_manual(name = self.Grouping, values = customColors,drop=False)  
            + ggtitle(self.title) 
            + labs(x= "",y = self.ylab)          
            #+ labs(x= element_blank(),y = self.ylab)
            + theme(
                plot_title= element_text(ha="center"),
                #Memo to self: More info at https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
                axis_text_x = element_text(rotation = "vertical", va="top", ha="left"),
                legend_title = element_blank()
                ) 
            + labs(fill = self.Grouping)
            + ylim(0,np.nan)   
        )
        #
        return annual_plot
    #
    def createMonthlyPlot(self):
        customColors = self.getColors() 
        plotBasis = None
        #
        startTime = self.plotData['firstMonthDay'].min()
        endTime = self.plotData['firstMonthDay'].max()
        if self.curveType == "line":
            plotBasis = (ggplot(data = self.plotData,mapping = aes(x='firstMonthDay',y=self.CountVar,color='groupFactor')) 
                         +  geom_line(linetype = "solid")    
                         + scale_color_manual(name = self.Grouping, values = customColors,drop=False)                        
                        )
        elif self.curveType == "area":
            plotBasis = (ggplot(data = self.plotData,mapping = aes(x='firstMonthDay',y=self.CountVar,fill='groupFactor')) 
                        + geom_area(color = None, alpha = 0.4) 
                        + geom_line(position = "stack", size = 0.2)
                        + scale_fill_manual(name = self.Grouping, values = customColors,drop=False)                          
                        )
        #Memo to self: More info at https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
        month_plot = (plotBasis 
                      + scale_x_datetime(date_labels = "%b-%Y",breaks = pd.date_range(startTime,endTime, freq='6M'))
                      + ggtitle(self.title)                       
                      + labs(x= "",y = self.ylab)  #Memo to self: x = element_blank() doesn't give the desired effect
                      + theme(
                          plot_title= element_text(ha="center"),
                          axis_text_x = element_text(rotation = "vertical", va="top", ha="left"),
                          legend_title = element_blank()
                          )
                      + ylim(0,np.nan)  
                      + labs(color =  self.Grouping)   
                    )
        #Memo til self:  12 monts moving average is difficult to make if the plot is not "stacked"
        if self.curveType == "line" and self.runAverage:
            month_plot = month_plot + geom_line(aes(y='smoothDDD'),linetype="dotted")
        #
        return month_plot
              
    #
# 

        
