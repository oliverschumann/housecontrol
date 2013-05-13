import os
import logging
import logging.handlers

from GlobalObjects import FILEPATH_LOG

class TemperatureLogService(object):

    __logPath = ""
    houseControl = None
    __heatingStatusBean = None
    
    
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.__logPath = os.getcwd() + FILEPATH_LOG
        
        self.__initializeLogger()
        
        
        
    def run(self):
        self.logger.info(self.__heatingStatusBean.getTemperatureLogString())

        
    def __initializeLogger(self):
        self.logger = logging.getLogger("TemperatureLogService")
        self.logger.setLevel(logging.INFO)
        
        # create file handler which logs even debug messages
        fh = logging.handlers.TimedRotatingFileHandler(self.__logPath + 'temperature.log', when="midnight", interval=1, backupCount=0, encoding='UTF-8', delay=False, utc=False)
        fh.setLevel(logging.INFO)
        
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s,%(message)s', datefmt='%Y%m%d%H%M%S')
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        
        