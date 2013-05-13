'''
Created on 07.12.2012
Job: Aktualisierung der heatingStatusBean
Auslesen der One-Wire-Sensoren (ueber die LinuxShell) und 
befuellen der heatingStatusBean

@author: Oliver
'''
import logging
from GlobalObjects import APPLICATION_LOGGER_NAME

from heating.HeatingStatusBean import MODE_ON, MODE_OFF, EVENT_CHANGED_HEATINGSTATUS, EVENT_CHANGED_TEMPERATURE, EVENT_CHANGED_HEATINGPROGRAM,SENSOR_TEMPERATURE_HEATING,\
    SENSOR_TEMPERATURE_WATER, SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW,\
    SENSOR_TEMPERATURE_UPPERFLOOR_FLOW, HEATING_PRG_PRESENCE, HEATING_PRG_ABSENCE
from heating.HeatingStatusBean import HEATING_STATUS_GROUNDFLOOR, HEATING_STATUS_UPPERFLOOR, HEATING_STATUS_WATER, HEATING_STATUS_CIRCUITPUMP
from heating.HeatingStatusBean import PUMP_HOTWATER_CIRCUIT, PUMP_HOTWATER, PUMP_GROUNDFLOOR, PUMP_UPPERFLOOR

PUMP_MODE_STANDARD = 1
PUMP_MODE_HOTWATER_PRIORITY = 2
PUMP_MODE_ABSENCE = 4

class HeatingControlService():
    
    houseControl = None
    __heatingStatusBean = None
    
    def __init__(self, houseControl):
        self.houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
        
    def update(self, eventtype):
        if(eventtype & EVENT_CHANGED_HEATINGSTATUS):
            self.logger.info("HeatingStatus changed! " + str(self.__heatingStatusBean.getHeatingStatusString()))
            self.controlHeatingStatus()
            
        elif(eventtype & EVENT_CHANGED_TEMPERATURE):
            self.logger.info("Temperature changed!")
            self.controlHeatingStatus()
            
        elif(eventtype & EVENT_CHANGED_HEATINGPROGRAM):
            self.logger.info("HeatingProgram changed!")
            self.controlHeatingStatus()
             
             
    def controlHeatingStatus(self):
        deltaTemperature = 5
        heatingProgram = self.__heatingStatusBean.getHeatingProgram()
        heatingStatusMap = self.__heatingStatusBean.getHeatingStatusMap()
        egvTemperature = self.__heatingStatusBean.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW)
        ogvTemperature = self.__heatingStatusBean.getTemperature(SENSOR_TEMPERATURE_UPPERFLOOR_FLOW)
        waterTemperature = self.__heatingStatusBean.getTemperature(SENSOR_TEMPERATURE_WATER)
        currentHeatingTemperature = self.__heatingStatusBean.getTemperature(SENSOR_TEMPERATURE_HEATING)
        
        #heatingTargetTemperature = self.__heatingStatusBean.getHeatingTargetTemperature()
        heatingTargetTemperature = 0
        
        if(heatingProgram == HEATING_PRG_PRESENCE):
            if(heatingStatusMap[HEATING_STATUS_WATER] == MODE_ON):
                if(waterTemperature < self.__heatingStatusBean.getWaterTargetTemperature() - deltaTemperature):
                    if(heatingTargetTemperature < self.__heatingStatusBean.getWaterTargetTemperature()):
                        heatingTargetTemperature = self.__heatingStatusBean.getWaterTargetTemperature()
            
            if(heatingStatusMap[HEATING_STATUS_UPPERFLOOR] == MODE_ON):
                if(ogvTemperature < self.__heatingStatusBean.getUpperFloorFlowTargetTemperature() - deltaTemperature):
                    if(heatingTargetTemperature < self.__heatingStatusBean.getUpperFloorFlowTargetTemperature()):
                        heatingTargetTemperature = self.__heatingStatusBean.getUpperFloorFlowTargetTemperature()
                    
        if(heatingStatusMap[HEATING_STATUS_GROUNDFLOOR] == MODE_ON):
            if(egvTemperature < self.__heatingStatusBean.getGroundFloorFlowTargetTemperature() - deltaTemperature):
                if(heatingTargetTemperature < self.__heatingStatusBean.getGroundFloorFlowTargetTemperature()):
                    heatingTargetTemperature = self.__heatingStatusBean.getGroundFloorFlowTargetTemperature()
                
        
        heatingMode = None
        self.logger.info("heatingTargetTemperature::" + str(heatingTargetTemperature) + " || currentHeatingTemperature::" +str(currentHeatingTemperature))
        if(heatingTargetTemperature > 0):
            
            if(heatingTargetTemperature < 35):
                heatingTargetTemperature = 35 
         
            #Kesseltemperatur kontrollieren, Brenner ein/ausschalten
            if(currentHeatingTemperature > heatingTargetTemperature):
                heatingMode = MODE_OFF
            elif(currentHeatingTemperature < heatingTargetTemperature - deltaTemperature):
                heatingMode = MODE_ON
            
        else:
            '''
            Bei ZielKesselTemperatur = 0 ist alles aus,
            ggf Pumpennachlauf, wenn kesselTemperatur > Brauchwasser | Fussbodenheizung 
            '''
            heatingMode = MODE_OFF
            pass
            
        #Aenderung uebertragen    
        if(heatingMode != None):
            self.__heatingStatusBean.setHeatingMode(heatingMode)
            
        #Pumpen steuern
        pumpModeMap = {}
        
        if(heatingProgram == HEATING_PRG_PRESENCE): 
            pumpMode = PUMP_MODE_STANDARD
                 
            if(heatingStatusMap[HEATING_STATUS_WATER] == MODE_ON):
                pumpModeMap.update({PUMP_HOTWATER: MODE_ON})
                
                if(heatingStatusMap[HEATING_STATUS_CIRCUITPUMP] == MODE_ON):
                    pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_ON})
                else:
                    pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_OFF})
                    
                if(waterTemperature < self.__heatingStatusBean.getWaterTargetTemperature() - deltaTemperature):
                    pumpModeMap.update({PUMP_GROUNDFLOOR: MODE_OFF})
                    pumpModeMap.update({PUMP_UPPERFLOOR: MODE_OFF})
                    #pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_OFF})
                    pumpMode = PUMP_MODE_HOTWATER_PRIORITY
                
            else:
                pumpModeMap.update({PUMP_HOTWATER: MODE_OFF})
    
                    
            if(pumpMode == PUMP_MODE_STANDARD):    
                if(heatingStatusMap[HEATING_STATUS_GROUNDFLOOR] == MODE_ON):
                    pumpModeMap.update({PUMP_GROUNDFLOOR: MODE_ON})
                else:
                    pumpModeMap.update({PUMP_GROUNDFLOOR: MODE_OFF})
                    
                if(heatingStatusMap[HEATING_STATUS_UPPERFLOOR] == MODE_ON):
                    pumpModeMap.update({PUMP_UPPERFLOOR: MODE_ON})
                else:
                    pumpModeMap.update({PUMP_UPPERFLOOR: MODE_OFF})
                     
                if(heatingStatusMap[HEATING_STATUS_CIRCUITPUMP] == MODE_ON):
                    pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_ON})
                else:
                    pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_OFF})
        
        elif(heatingProgram == HEATING_PRG_ABSENCE):
            if(heatingStatusMap[HEATING_STATUS_GROUNDFLOOR] == MODE_ON):
                pumpModeMap.update({PUMP_GROUNDFLOOR: MODE_ON})
            else:
                pumpModeMap.update({PUMP_GROUNDFLOOR: MODE_OFF})
                
            pumpModeMap.update({PUMP_UPPERFLOOR: MODE_OFF})
            pumpModeMap.update({PUMP_HOTWATER: MODE_OFF})
            pumpModeMap.update({PUMP_HOTWATER_CIRCUIT: MODE_OFF})
            
                
        #Aenderung uebertragen   
        self.__heatingStatusBean.setPumpModeMap(pumpModeMap)
