'''
Created on 07.12.2012

@author: oliver
'''

import logging
from GlobalObjects import APPLICATION_LOGGER_NAME

HEATING_PRG_OFF = 0
HEATING_PRG_PRESENCE = 1
HEATING_PRG_ABSENCE = 2
HEATING_PRG_HOLIDAY = 4

SENSOR_TEMPERATURE_HEATING = "10-000801244d84"
SENSOR_TEMPERATURE_WATER = "10-00080119602a"
SENSOR_TEMPERATURE_INDOOR = "10-000801246971"
SENSOR_TEMPERATURE_OUTDOOR = "OutdoorWeb"
SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW = "10-00080123a0ff"
SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN = "10-00080123a848"
SENSOR_TEMPERATURE_UPPERFLOOR_FLOW = "10-00080123d4a1"
SENSOR_TEMPERATURE_UPPERFLOOR_RETURN = "10-000801248e98"

MIXER_MODE_OFF = 0
MIXER_MODE_DOWN = 1
MIXER_MODE_UP = 2

MODE_ON = 1
MODE_OFF = 0

PUMP_HOTWATER_CIRCUIT = "0x38"
PUMP_HOTWATER = "0x3B"
PUMP_GROUNDFLOOR = "0x39"
PUMP_UPPERFLOOR = "0x3C"

HEATING_STATUS_UPPERFLOOR = "Obergeschoss" 
HEATING_STATUS_GROUNDFLOOR = "Erdgeschoss" 
HEATING_STATUS_WATER = "Brauchwasser" 
HEATING_STATUS_CIRCUITPUMP = "Zirkulationspumpe" 

EVENT_CHANGED_TEMPERATURE = 1
EVENT_CHANGED_HEATINGSTATUS = 2
EVENT_CHANGED_PUMPMODE = 4
EVENT_CHANGED_HEATINGMODE = 8
EVENT_CHANGED_HEATINGPROGRAM = 16
EVENT_ERROR_TEMPERATURE = 32


EVENT_ALL = (EVENT_CHANGED_TEMPERATURE | 
             EVENT_CHANGED_HEATINGSTATUS |
             EVENT_CHANGED_PUMPMODE |
             EVENT_CHANGED_HEATINGMODE |
             EVENT_CHANGED_HEATINGPROGRAM | 
             EVENT_ERROR_TEMPERATURE)


class HeatingStatusBean(object):
    '''
    classdocs
    '''
    __heatingProgram = HEATING_PRG_PRESENCE
    
    __heatingMode = MODE_OFF
    
    __heatingStatus = {
                       HEATING_STATUS_UPPERFLOOR: MODE_OFF,
                       HEATING_STATUS_GROUNDFLOOR: MODE_OFF,
                       HEATING_STATUS_WATER: MODE_OFF,
                       HEATING_STATUS_CIRCUITPUMP: MODE_OFF,
                       }
    
    __sensors = {
                 SENSOR_TEMPERATURE_HEATING : 0, 
                 SENSOR_TEMPERATURE_WATER : 0,
                 SENSOR_TEMPERATURE_INDOOR : 0,
                 SENSOR_TEMPERATURE_OUTDOOR : 0,
                 SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW : 0,
                 SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN : 0,
                 SENSOR_TEMPERATURE_UPPERFLOOR_FLOW : 0,
                 SENSOR_TEMPERATURE_UPPERFLOOR_RETURN : 0
                 }
    
    __mixerMode = MIXER_MODE_OFF
    
    __pumps = {
               PUMP_HOTWATER_CIRCUIT: MODE_OFF,
               PUMP_HOTWATER: MODE_OFF,
               PUMP_GROUNDFLOOR: MODE_OFF,
               PUMP_UPPERFLOOR: MODE_OFF
               }
    
    
    __waterTargetTemperature = 48
    __heatingMaxTemperature = 60
    __groundFloorFlowTargetTemperature = 32
    __upperFloorFlowTargetTemperature = 40 
    
    __changeListener = []
    __changed = False
    __raiseEvent = 0
    
    
    def __init__(self):
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    
    #HeatingProgram
    def getHeatingProgram(self):
        return self.__heatingProgram
    
    def setHeatingProgram(self, heatingProgram):
        if(self.__heatingProgram != heatingProgram):
            self.__heatingProgram = heatingProgram
            self.__changed = True
            self.__raiseEvent = EVENT_CHANGED_HEATINGPROGRAM
        self.notifyChangeListener()

    
    #HeatingStatusMap
    def setHeatingStatusMap(self, heatingStatusMap):
        for heatingComponent, status in heatingStatusMap.iteritems():
            if(self.__heatingStatus.has_key(heatingComponent)):
                statusValue = None
                try:
                    statusValue = int(status)
                    if(statusValue != MODE_ON):
                        statusValue = MODE_OFF
                except ValueError:
                    self.logger.error("WrongMode: %s=%s [set to MODE_OFF]" % (heatingComponent, status))
                    statusValue = None
                    
                if(statusValue != None):     
                    oldStatus = self.__heatingStatus[heatingComponent]
                    if(oldStatus != statusValue):
                        self.__heatingStatus[heatingComponent] = statusValue
                        self.__changed = True
                        self.__raiseEvent = EVENT_CHANGED_HEATINGSTATUS 
        self.notifyChangeListener()
    
    def getHeatingStatusMap(self):
        return self.__heatingStatus
        
    #Sensors
    def getSensors(self):
        return self.__sensors
    
    #MixerMode
    def getMixerMode(self):
        return self.__mixerMode
    
    def setMixerMode(self, mixerMode):
        if(mixerMode in range(3)):
            self.__mixerMode = mixerMode
    
    #Water
    def getWaterTargetTemperature(self):
        return self.__waterTargetTemperature
    
    def setWaterTargetTemperature(self, temperature):
        if(temperature > 10):
            if(temperature < 80):
                self.__waterTargetTemperature = temperature
    
    
    #Upperfloor
    def getUpperFloorFlowTargetTemperature(self):
        return self.__upperFloorFlowTargetTemperature
    
    def setUpperFloorFlowTargetTemperature(self, temperature):
        if(temperature > 10):
            if(temperature < 40):
                self.__upperFloorFlowTargetTemperature = temperature
    
    
    #groundfloor
    def getGroundFloorFlowTargetTemperature(self):
        return self.__groundFloorFlowTargetTemperature  
    
    def setGroundFloorFlowTargetTemperature(self, temperature):
        if(temperature > 10):
            if(temperature < 40):
                self.__groundFloorFlowTargetTemperature = temperature
    
    
    #heating
    def getHeatingMaxTemperature(self):
        return self.__heatingMaxTemperature
    
    def setHeatingMaxTemperature(self, temperature):
        if(temperature > 10):
            if(temperature < 80):
                self.__heatingMaxTemperature = temperature
    

    #Sensors
    def setTemperature(self, sensor, temperature):
        if(self.__sensors.has_key(sensor)):
            currentTemperature = self.__sensors[sensor]
            if(currentTemperature != temperature): 
                self.__sensors[sensor] = temperature
                self.__changed = True
                self.__raiseEvent = EVENT_CHANGED_TEMPERATURE
        self.notifyChangeListener()
       
    def setSensorTemperatureMap(self, sensorTemperatureMap):
        for sensor, temperature in sensorTemperatureMap.iteritems():
            if(self.__sensors.has_key(sensor)):
                
                #Die inneren Werte sollten auf jedenfall ueber 0Grad liegen
                if(sensor != SENSOR_TEMPERATURE_OUTDOOR):
                    if(temperature == 0):
                        self.logger.error("WrongTemperature: %s" % (sensor))
                        self.__raiseEvent = self.__raiseEvent | EVENT_ERROR_TEMPERATURE
                
                currentTemperature = self.__sensors[sensor]
                if(currentTemperature != temperature): 
                    self.__sensors[sensor] = temperature
                    self.__changed = True
                    self.__raiseEvent = self.__raiseEvent | EVENT_CHANGED_TEMPERATURE
        self.notifyChangeListener()

    def getTemperature(self, sensor):
        temperature = 0
        if(self.__sensors.has_key(sensor)):
            temperature = self.__sensors[sensor]
        return temperature
    
    
    def getHeatingTargetTemperature(self):
        targetTemperature = 0
        if(self.__heatingStatus[HEATING_STATUS_GROUNDFLOOR] == MODE_ON):
            if(self.getGroundFloorFlowTargetTemperature() > targetTemperature):
                targetTemperature = self.getGroundFloorFlowTargetTemperature()
                
        if(self.__heatingStatus[HEATING_STATUS_UPPERFLOOR]== MODE_ON):
            if(self.getUpperFloorFlowTargetTemperature() > targetTemperature):
                targetTemperature = self.getUpperFloorFlowTargetTemperature()
                
        if(self.__heatingStatus[HEATING_STATUS_WATER]== MODE_ON):
            if(self.getWaterTargetTemperature() > targetTemperature):
                targetTemperature = self.getWaterTargetTemperature()
                
        return targetTemperature
    
    #HeatingMode
    def setHeatingMode(self, mode):
        if(self.__heatingMode != mode):
                self.__heatingMode = mode 
                self.__changed = True
                self.__raiseEvent = EVENT_CHANGED_HEATINGMODE
        self.notifyChangeListener()
        
    def getHeatingMode(self):
        return self.__heatingMode
    
    
    #PumpMode
    def setPumpModeMap(self, pumpModeMap):
        for pump, mode in pumpModeMap.iteritems():
            if(self.__pumps.has_key(pump)):
                currentMode = self.__pumps[pump]
                if(currentMode != mode): 
                    self.__pumps[pump] = mode
                    self.__changed = True
                    self.__raiseEvent = EVENT_CHANGED_PUMPMODE
        self.notifyChangeListener()
    
    def getPumpModeMap(self):
        return self.__pumps
    
    def setPumpMode(self, pump, mode):
        if(self.__pumps.has_key(pump)):
            currentPumpMpde = self.__pumps[pump] 
            if(currentPumpMpde != mode):
                self.__pumps[pump] = mode 
                self.__changed = True
                self.__raiseEvent = EVENT_CHANGED_PUMPMODE
        self.notifyChangeListener()
    
    def getPumpMode(self, pump):
        pumpMode = MODE_OFF
        if(self.__pumps.has_key(pump)):
            pumpMode = self.__pumps[pump]
        return pumpMode 
    
    #changeListener
    def addChangeListener(self, changeListener):
        self.__changeListener.append(changeListener)
        
    def notifyChangeListener(self):
        if(self.__changed == True):
            self.__changed = False
            for listener in (self.__changeListener):
                listener.update(self.__raiseEvent)
            self.__raiseEvent = 0
    
    
    #StringOutput
    def getMaxTemperatureString(self):
        statusString = ("Kessel: %s" % self.getHeatingMaxTemperature())
        statusString += (", Brauchwasser: %s" % self.getWaterTargetTemperature())
        statusString += (", EGVorlauf: %s" % self.getGroundFloorFlowTargetTemperature())
        statusString += (", OGVorlauf: %s" % self.getUpperFloorFlowTargetTemperature())
                
        return statusString
    
    def getTemperatureMap(self):
        temperatureMap = {}
        temperatureMap['Kesselzieltemperatur'] = self.getHeatingTargetTemperature()
        temperatureMap['Kessel'] = self.getTemperature(SENSOR_TEMPERATURE_HEATING)
        temperatureMap['Brauchwasser'] = self.getTemperature(SENSOR_TEMPERATURE_WATER)
        temperatureMap['Innen'] = self.getTemperature(SENSOR_TEMPERATURE_INDOOR)
        temperatureMap['Aussen'] = self.getTemperature(SENSOR_TEMPERATURE_OUTDOOR)
        temperatureMap['EGV'] = self.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW)
        temperatureMap['EGR'] = self.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN)
        temperatureMap['OGV'] = self.getTemperature(SENSOR_TEMPERATURE_UPPERFLOOR_FLOW)
        temperatureMap['OGR'] = self.getTemperature(SENSOR_TEMPERATURE_UPPERFLOOR_RETURN)
        
        return temperatureMap
    
    def getTemperatureString(self):
        statusString = "" 
        for sensor, temperature in self.getTemperatureMap().iteritems():
            statusString += ", " + sensor + (": %s" % (temperature)) 
        return statusString[2:]
    
    def getTemperatureLogString(self):
        return '%s,%s,%s,%s,%s,%s,%s,%s' % (self.getTemperature(SENSOR_TEMPERATURE_UPPERFLOOR_FLOW), 
                                            self.getTemperature(SENSOR_TEMPERATURE_UPPERFLOOR_RETURN),
                                            self.getTemperature(SENSOR_TEMPERATURE_WATER),
                                            self.getTemperature(SENSOR_TEMPERATURE_HEATING),
                                            self.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW),
                                            self.getTemperature(SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN),
                                            self.getTemperature(SENSOR_TEMPERATURE_INDOOR),
                                            self.getTemperature(SENSOR_TEMPERATURE_OUTDOOR))
        
    def getPumpStatusString(self):
        statusString = ("Zirkulationspumpe: %s" % self.getPumpMode(PUMP_HOTWATER_CIRCUIT))
        statusString += (", Brauchwasserpumpe: %s" % self.getPumpMode(PUMP_HOTWATER))
        statusString += (", Fussbodenpumpe: %s" % self.getPumpMode(PUMP_GROUNDFLOOR))
        statusString += (", OG-Pumpe: %s" % self.getPumpMode(PUMP_UPPERFLOOR))
        
        return statusString
    
    def getHeatingStatusString(self):
        statusString = ""
        for heatingComponent, status in self.__heatingStatus.iteritems():
            statusString += (", " + heatingComponent + ": %s" % status)
        if(len(statusString) > 0):
            statusString = statusString[2:]
        return statusString
        
    def toString(self):
        return self.getMaxHeatingTemperature() + "\n" + self.getTemperatureString() + "\n" + self.getPumpStatusString()