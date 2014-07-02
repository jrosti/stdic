
from sys import argv
from pairiterators.pairiterator import PairIteratorFactory
from imagefilters.imagefilter import ImageFilterFactory
from sequencefilters.sequencefilter import SequenceFilterFactory
from sequencefilters.imageorder import ImageOrderFactory
from configparser import ConfigParser
from imagelist import ImageList
from diccontroller import DICController
from exporters.exporter import ExporterClassFactory
from exporters.exporter import ExporterParameters
from outputtools import *

class Analyzer:
    
    def __init__(self, filelist, dfffolder, config):
        
        #--------------------------------------------------------
        # Generate image filters
        #--------------------------------------------------------
        
        try:
            filtconfig          = config["imagefilters"]
        except KeyError:
            filtconfig          = dict()
        
        imagefilters            = ImageFilterFactory().getImageFilters(filtconfig)
        
        #--------------------------------------------------------
        # Generate ordering
        #--------------------------------------------------------
        
        orderconfig             = config["order"]
        ordername               = orderconfig.pop('name')
        
        order                   = ImageOrderFactory().getImageOrder(ordername, orderconfig)

        #--------------------------------------------------------
        # Generate sequence with ordering
        #--------------------------------------------------------
        
        seqconfig               = config["sequence"]
        seqname                 = seqconfig.pop('name')
        
        sequencefilter          = SequenceFilterFactory().getSequenceFilter(seqname, order, seqconfig)
        
        #--------------------------------------------------------
        # Generate imagelist from filelist, imagefilters and sequence
        #--------------------------------------------------------
        
        if len(filelist) < 2:
            raise Exception("Filelist too short.")
        
        try:
            regexp              = config['imageformat']
        except KeyError:
            regexp              = None
        
        imagelist               = ImageList(filelist, sequencefilter, imagefilters, regexp)
         
        #--------------------------------------------------------
        # Generate pairiterator from imagelist
        #--------------------------------------------------------
        
        pairiteratorconfig      = config["pairiterator"]
        pairiteratorname        = pairiteratorconfig.pop('name')  
        
        self.pairiterator       = PairIteratorFactory().getPairIterator(pairiteratorname, imagelist, pairiteratorconfig)
        
        #--------------------------------------------------------
        # Generate DIC
        #--------------------------------------------------------
            
        try:
            dicconfig           = config["dic"]
        except KeyError:
            dicconfig           = dict()
            
        self.dic                = DICController(**dicconfig)
        
        #--------------------------------------------------------
        # Generate Exporter and analysis parameters
        #--------------------------------------------------------
                
        self.overwrite          = config["overwrite"]
        
        try:
            outputconfig        = config['output']
        except KeyError:
            outputconfig        = dict()
        try:
            outputformat        = outputconfig.pop('format')
        except KeyError:
            outputformat        = "dff-%s-%s.dff"
        try:
        	exportername        = outputconfig.pop('name')
        except KeyError:
            exportername    	= 'DffExporter'
            
        self.exporter           = ExporterClassFactory().getExporterClass(exportername)
        
        self.namegenerator      = PictureNumberNamer(dfffolder, outputformat)
        
        self.exporterparameters = ExporterParameters(dicconfig = dicconfig, **outputconfig)
        
        self.checker            = CheckExistence()
        
    def analyze(self):
        
        for (image1, image2) in self.pairiterator:
            dffname = self.namegenerator.generatename(image1, image2)
            if not self.overwrite:
                if self.checker.checkExistence(dffname):
                    continue
            try:
                print "Analyzing pictures number %s and %s." % (image1.picturenumber, image2.picturenumber)
            except AttributeError:
                pass
            try:
                self.dic.analyze(image1.getImage(), image2.getImage())
                exporterinstance = self.exporter(image1, image2, self.dic, self.exporterparameters, dffname)
                exporterinstance.export()
            except ValueError:
                print "ValueError"
