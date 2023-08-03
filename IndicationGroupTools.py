print('Er inne i IndicationGroupTools5.py')
#
import pandas as pd
import numpy as np
import os
import time
import sys# For sys.exit()
#********* Start  graphics-related imports
from plotnine import *
#********* End  graphics-related imports
#********** Start read auxiliary code
exec(open("PlotGenerator.py", encoding='utf-8').read())
# *********** End read auxiliary code
class IndicationGroup(PlotGenerator):
    def getTitle(self):
        main_title = "Totalt salg pr. indikasjonsgruppe"
        return main_title
    # Defines the color palette for this grouping of antibiotics
    #    
    def getColors(self):
        customBrewer = self.customizeBrewer("RdYlGn")
        return customBrewer
    #
#