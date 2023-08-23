import pandas as pd
import numpy as np
import os
import time
import sys# For sys.exit()
#********* Start  graphics-related imports
from plotnine import *
#********* End  graphics-related imports
from statistics import median
#
#********** Start read auxiliary code
from  PlotGeneratorTools import PlotGenerator
# *********** End read auxiliary code
#Memo to self: A class that inherits another class doesn't need to have an init-function
class Total(PlotGenerator):
    def getTitle(self):
        main_title = "NORGE; grossiststat J01, excl metenamin"
        return main_title
    
    def createAnnualPlot(self):
        annual_plot =  (ggplot(self.plotData, aes(x="yearFactor",y = self.CountVar, fill = self.CountVar)) 
            + geom_bar(stat="identity",position = self.position,color = "black")
            + scale_fill_gradient2(
                low = "green",mid = "yellow",high = "red",
                midpoint = median(self.plotData[self.CountVar])
                )      
            + ggtitle(self.title) 
            + labs(x= "",y = self.ylab)          
            #+ labs(x= element_blank(),y = self.ylab)
            + theme(
                plot_title= element_text(ha="center"),
                #Memo to self: More info at https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
                axis_text_x = element_text(rotation = "vertical", va="top", ha="left"),
                legend_title = element_blank()
                ) 
            + ylim(0,np.nan)   
        )
        #
        return annual_plot
    #Memo : 
    def createMonthlyPlot(self):
        startTime = self.plotData['firstMonthDay'].min()
        endTime = self.plotData['firstMonthDay'].max()
        month_plot =  (ggplot(self.plotData, aes(x="firstMonthDay",y=self.CountVar)) 
            + scale_x_datetime(date_labels = "%b-%Y",breaks = pd.date_range(startTime,endTime, freq='6M')
                )
            + ggtitle(self.title) 
            + labs(x= "",y = self.ylab)          
            #+ labs(x= element_blank(),y = self.ylab)
            + theme(
                plot_title= element_text(ha="center"),
                #Memo to self: More info at https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
                axis_text_x = element_text(rotation = "vertical", va="top", ha="left"),
                legend_title = element_blank()
                ) 
            + ylim(0,np.nan)   
        )
        #Memo to self: Have to write "color", not just "col"
        if self.curveType == "line":
            month_plot = month_plot + geom_line(color="#4271c4",linetype = "solid")
            if self.runAverage:
                month_plot = month_plot + geom_line(aes(y="smoothDDD"),linetype="dotted")
            #                      
        else:
            month_plot = month_plot  +  geom_area(color = np.nan, alpha = 0.4) + geom_line(position = "stack", linewidth = 0.2)                                
        return month_plot
    #        
#   
    
    