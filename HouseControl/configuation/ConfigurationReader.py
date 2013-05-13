'''
Created on 19.01.2013

@author: admin
'''
import logging
from json import JSONDecoder

class ConfigurationReader(object):

    applicationLogger = None
    
    configuration = {}
    temperatures = {}
    intervallSettings = {}
    heatingTasks = {}
    blindTasks = {}
    
    def __init__(self, logger=None, configurationFileName=None):
        self.applicationLogger = logger
        if(configurationFileName != None):
            self.readConfigFile(configurationFileName)
    
    def __logMsg(self, level, message):
        if(self.applicationLogger != None):
            self.applicationLogger.log(level, message)
    
    def readConfigFile(self, fileName):
        configurationFile = open(fileName, 'r')
        configuration = configurationFile.read()
        configurationFile.close()
        
        content = JSONDecoder().decode(configuration)
        
        self.configuration = content.get('configuration')
        self.__logMsg(logging.INFO, "Reading configuration...")
        
        self.temperatures = self.configuration.get('temperatures')
        self.__logMsg(logging.INFO, "Temperatures: %s" % (self.temperatures))
        
        self.intervallSettings = self.configuration.get('scheduler').get('baseTasks')
        self.__logMsg(logging.INFO, "IntervallSettings: %s" % (self.intervallSettings))
        
        self.heatingTasks = self.configuration.get('scheduler').get('heatingTasks').get("task")
        self.__logMsg(logging.INFO, "HeatingTasks: %s" % (len(self.heatingTasks)))
        
        return configuration
    
        