import pandas as pd
import numpy as np
import os
import time
import sys# For sys.exit()
#********* Start  graphics-related imports
from plotnine import *
#********* End  graphics-related imports
#********** Start read auxiliary code
from  PlotGeneratorTools import PlotGenerator
# *********** End read auxiliary code
class ATC3(PlotGenerator):
    def getTitle(self):
        main_title = "Totalt salg pr. ATC3-gruppe"
        return main_title
    # Defines the color palette for this grouping of antibiotics
    #    
    def getColors(self):
        customBrewer = self.customizeBrewer("Spectral")            
        return customBrewer
    #
#