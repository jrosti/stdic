from formatters import FormatterFactory

class ConfigParser:
    
    def __init__(self):
        self.formatterfactory = FormatterFactory()
        
    def parseFile(self,filename):
        
        configfile = open(filename, 'r')
        lines = configfile.readlines()
        
        return self.parse(lines)
        
    def parse(self, lines):
        
        config = dict()
        
        for line in lines:
            line = line.split('#', 1)[0].strip()
            if line == '':
                continue
            configline, value = line.split('=', 1)
            configtree = configline.strip().split('.')
            configkey = configtree.pop(-1)
            dictionary = config
            for subconfig in configtree:
                if subconfig not in dictionary:
                    dictionary[subconfig] = dict()
                dictionary = dictionary[subconfig]
            dictionary[configkey] = self.formatterfactory.getFormatted(value.strip())
            
        return config
