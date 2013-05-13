'''
Created on 10.01.2013

@author: admin
'''
import logging, time
from GlobalObjects import executeShellCommand, APPLICATION_LOGGER_NAME, FILEPATH_BASH
from heating.HeatingStatusBean import EVENT_ERROR_TEMPERATURE 

I2C_ADDRESS_SENSORCUTTER = "0x3F"
I2C_SWITCH_OFF = "0x00"
I2C_SWITCH_ON = "0xFF"

class HeatingMonitorService(object):
    
    houseControl = None
    __heatingStatusBean = None
    __commandPath = FILEPATH_BASH + 'max6956_switchport.sh'
    __rebootPath = FILEPATH_BASH + 'reboot.sh'
    __allOffPath = FILEPATH_BASH + 'max6956_alloff.sh'
    
    #Alle 10sek wird die Temperatur aktualisiert
    __failsToReboot = 6
    __failCount = 0
     
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
        self.logger.info("HeatingMonitorService (" + self.__commandPath + ") initialized.")
    
    def update(self, eventtype):
        
        if(eventtype & EVENT_ERROR_TEMPERATURE):

            commandArgs = ['sudo',self.__allOffPath]
            self.logger.info("Switching all OFF: %s" % (commandArgs))
            executeShellCommand(commandArgs)
            time.sleep(1)
            
            #Temperatursensoren von der Versorgungsspannung trennen
            i2cMode = I2C_SWITCH_ON    
            commandArgs = [self.__commandPath, I2C_ADDRESS_SENSORCUTTER, i2cMode]
            self.logger.info("Switched TemperatureSensors: %s" % (commandArgs))
            executeShellCommand(commandArgs)
            
            #Warten und Restart
            time.sleep(2)
            commandArgs = ['sudo',self.__rebootPath]
            self.logger.info("Rebooting System: %s" % (commandArgs))
            executeShellCommand(commandArgs)
            self.logger.info("StartRebooting")
            
            #Start der HouseControl muss ueber initd laufen....
            
            
            