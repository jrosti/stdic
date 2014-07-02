#!/usr/bin/python
"""

    Simo Tuomisto, 2011

"""


from lib.analyzer import Analyzer
from lib.configparser import ConfigParser
from lib.folderscan import FolderScan
import sys

class Register:
    
    def __init__(self, folder, dfffolder, configurationfile):
        
        #--------------------------------------------------------
        # Configuration parsing
        #--------------------------------------------------------
        
        configurationparser     = ConfigParser()
        config                  = configurationparser.parseFile(configurationfile)
        
        imageformat = config['imageformat']

        folder = FolderScan(folder)
        filelist = folder.findWithExpression(imageformat)
                
        self.analyzer = Analyzer(filelist, dfffolder, config)

    def run(self):
        self.analyzer.analyze()

if __name__ == "__main__":
    
    if len(sys.argv[1:]) != 3:
        print "Usage: imagefolder dfffolder configfile"
    else:
        folder = sys.argv[1]
        dfffolder = sys.argv[2]
        configurationfile = sys.argv[3]
        register = Register(folder, dfffolder, configurationfile)
        register.run()
