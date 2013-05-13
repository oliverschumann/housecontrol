'''
Created on 07.12.2012

@author: admin
'''
import time
from GlobalObjects import executeShellCommand, APPLICATION_LOGGER_NAME, FILEPATH_BASH
import re, logging, os
from heating.HeatingStatusBean import SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW, SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN,SENSOR_TEMPERATURE_HEATING, SENSOR_TEMPERATURE_WATER,SENSOR_TEMPERATURE_INDOOR, SENSOR_TEMPERATURE_UPPERFLOOR_FLOW, SENSOR_TEMPERATURE_UPPERFLOOR_RETURN, SENSOR_TEMPERATURE_OUTDOOR
from busservice.BusWorker import BusJob, Max6956BusJob
'''
Job: Aktualisierung der heatingStatusBean

Auslesen der One-Wire-Sensoren und Webanfrage fuer die Aussentemperatur
(ueber die LinuxShell) und befuellen der heatingStatusBean
'''

TEMPERATURE_FILEPATH = "/home/pi/housecontrol/settings/currenttemps.txt"

class TemperatureFeedService(BusJob):
    
    __sensorDataPath = ""
    houseControl = None
    __heatingStatusBean = None
    __delayCounter = 0
    __isRunning = False
    __workingDirectory = os.getcwd() + FILEPATH_BASH
    __hfSensors = [SENSOR_TEMPERATURE_HEATING, SENSOR_TEMPERATURE_WATER, SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW]
    
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    
    
    def run(self):
        measuring = False
        self.__delayCounter += 1
        if(self.__heatingStatusBean.getHeatingTargetTemperature() == 0):
            if(self.__delayCounter >= 4):
                measuring = True
        else:
            if(self.__delayCounter >= 1):
                measuring = True
        
        if(measuring == True):
            if(self.__isRunning == False):
                #Messung erfolgt im QueueJob
                self.houseControl.busJobsQueue.put(Max6956BusJob("0x3f", "0x00"))
                self.houseControl.busJobsQueue.put(self)
                self.houseControl.busJobsQueue.put(Max6956BusJob("0x3f", "0xff"))
                self.__delayCounter = 0
            
            
    def runQueueJob(self):
        self.__isRunning = True
        time.sleep(1)
        sensorsDataSet = self.__heatingStatusBean.getSensors()
        sensorTemperatureMap = self.measureTemperatures(sensorsDataSet.keys())

        #Messungen uebertragen, Log
        self.__heatingStatusBean.setSensorTemperatureMap(sensorTemperatureMap)
        
        self.__isRunning = False
        self.logger.info("TemperatureMeasuring: " + self.__heatingStatusBean.getTemperatureString())
        

        
    def measureTemperaturesOLD(self, sensorIds):
        #neu -> auslesen aus einer Datei
        sensorTemperatureMap = {}
        sensorArr = [SENSOR_TEMPERATURE_HEATING , SENSOR_TEMPERATURE_WATER, SENSOR_TEMPERATURE_INDOOR,
                     SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW, SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN ,
                     SENSOR_TEMPERATURE_UPPERFLOOR_FLOW, SENSOR_TEMPERATURE_UPPERFLOOR_RETURN,
                     SENSOR_TEMPERATURE_OUTDOOR]
        
        tempFile = open(TEMPERATURE_FILEPATH, 'r')
        temperatureString = tempFile.read()
        tempFile.close()
        
        temperatureString = re.sub("\s", "", temperatureString)
        
        temperatureArr = temperatureString.split(",")
        temperatureArr.pop(0)
        
        for i in range(len(sensorArr)):
            sensorTemperatureMap[sensorArr[i]] = round(float(temperatureArr[i]), 1)
        
        return sensorTemperatureMap
        
    def measureTemperatures(self, sensorIds):
        sensorTemperatureMap = {}
        for sensorId in sensorIds:
            if(sensorId.startswith("10-")):
                commandArgs = [self.__workingDirectory + 'getSensorTemperature.sh', sensorId]
            else:
                commandArgs = [self.__workingDirectory + 'getOutdoorTemperature.sh']

            
            #WhiteSpace entfernen!    
            temperatureString = re.sub("\s", "", str(executeShellCommand(commandArgs)))
            if(len(temperatureString) > 0):
                temperature = round(float(temperatureString), 1)
                sensorTemperatureMap[sensorId] = temperature
                
        return sensorTemperatureMap
    