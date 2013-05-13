'''
Created on 11.12.2012
Job: Event gesteuerte Komponente 
zum Schalten der Pumpen und Heizung (ueber die LinuxShell)

@author: Oliver
'''
import logging
from busservice.BusWorker import Max6956BusJob
from GlobalObjects import APPLICATION_LOGGER_NAME, FILEPATH_BASH
from heating.HeatingStatusBean import EVENT_CHANGED_HEATINGMODE, EVENT_CHANGED_PUMPMODE, MODE_ON


I2C_ADDRESS_HEATING = "0x3A"
I2C_SWITCH_OFF = "0x00"
I2C_SWITCH_ON = "0xFF"


class HeatingSwitchService(object):
    houseControl = None
    __heatingStatusBean = None
    __commandPath = FILEPATH_BASH + 'max6956_switchport.sh'
    
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
        self.logger.info("HeatingSwitchService (" + self.__commandPath + ") initialized.")
        
        
    def update(self, eventtype):
        
        if(eventtype & EVENT_CHANGED_HEATINGMODE):
            i2cMode = I2C_SWITCH_OFF
            if(self.__heatingStatusBean.getHeatingMode() == MODE_ON):
                i2cMode = I2C_SWITCH_ON
                
            commandArgs = [self.__commandPath, I2C_ADDRESS_HEATING, i2cMode]
            #result = str(executeShellCommand(commandArgs))
            
            self.logger.info("Switched Heating: %s" % (commandArgs))
            
            self.houseControl.busJobsQueue.put(Max6956BusJob(I2C_ADDRESS_HEATING, i2cMode))
            
        
        if(eventtype & EVENT_CHANGED_PUMPMODE):
            pumpModeMap = self.__heatingStatusBean.getPumpModeMap()
            for pump, mode in pumpModeMap.iteritems():
                i2cMode = I2C_SWITCH_OFF
                if(mode == MODE_ON):
                    i2cMode = I2C_SWITCH_ON
                
                commandArgs = [self.__commandPath, pump, i2cMode]
                #result = str(executeShellCommand(commandArgs))
                
                self.logger.info("Switched Pump: %s" % (commandArgs))
                
                self.houseControl.busJobsQueue.put(Max6956BusJob(pump, i2cMode))
                
