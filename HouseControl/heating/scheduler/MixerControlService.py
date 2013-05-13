'''
Created on 19.12.2012

@author: admin
'''
import os, time
from GlobalObjects import executeShellCommand, FILEPATH_BASH
from heating.HeatingStatusBean import SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW, PUMP_GROUNDFLOOR, MODE_ON
from busservice.BusWorker import BusJob

class MixerControlService(BusJob):
    
    __targetTemperature = 28
    
    __commandPath = os.getcwd() + FILEPATH_BASH
    __commandMixerUp = "mischerh.sh"
    __commandMixerDown = "mischerr.sh"
    __MixerRunTime = 2
    __MixerRunTimeLong = 5
    __MixerMode = 0
    __lastTemperature = 0
    
    houseControl = None
    __heatingStatusBean = None
    
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.__MixerMode = 0
    
    
    def run(self):
        if(self.__heatingStatusBean.getPumpMode(PUMP_GROUNDFLOOR) == MODE_ON):
            #Regelung erfolgt im QueueJob
            self.houseControl.busJobsQueue.put(self)
        else:
            print("MixerOff")
            
        
    def runQueueJob(self):
        deltaTemperature = 1
        self.__targetTemperature = self.__heatingStatusBean.getGroundFloorFlowTargetTemperature()
        currentTemperature = self.__heatingStatusBean.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW)
        if(self.__lastTemperature == 0):
            self.__lastTemperature == currentTemperature
            
        #print("EGV: %s" % (currentTemperature))
        
        runTime = self.__MixerRunTime
        
        commandArgs = []
        if(currentTemperature < (self.__targetTemperature - deltaTemperature)):
            
            if(self.__MixerMode == 2):
                runTime = self.__MixerRunTimeLong
                
            if(currentTemperature > self.__lastTemperature):
                runTime = self.__MixerRunTime
                
            self.__MixerMode = 2
            commandArgs = [self.__commandPath + self.__commandMixerUp, str(runTime)]
            
        elif (currentTemperature > (self.__targetTemperature + deltaTemperature)):
            
            if(self.__MixerMode == 1):
                runTime = self.__MixerRunTimeLong
                
            if(currentTemperature < self.__lastTemperature):
                runTime = self.__MixerRunTime
                
            self.__MixerMode = 1
            commandArgs = [self.__commandPath + self.__commandMixerDown, str(runTime)]
        
        else:
            if(self.__MixerMode == 2):
                commandArgs = [self.__commandPath + self.__commandMixerDown, str(self.__MixerRunTimeLong)]

            elif(self.__MixerMode == 1):
                commandArgs = [self.__commandPath + self.__commandMixerUp, str(self.__MixerRunTimeLong)]

            runTime = self.__MixerRunTime
            self.__MixerMode = 0
            
        if(len(commandArgs) > 0):
            result = str(executeShellCommand(commandArgs))
            #print(commandArgs)
