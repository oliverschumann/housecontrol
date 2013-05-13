'''
Created on 07.12.2012

@author: admin
'''
import logging, time, Queue, os
from apscheduler.scheduler import Scheduler, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from GlobalObjects import APPLICATION_LOGGER_NAME, initializeApplicationLogger, FILEPATH_CONFIGURATION

from heating import HeatingStatusBean
from heating.changelistener import HeatingControlService, HeatingMonitorService, HeatingSwitchService
from heating.scheduler import MixerControlService, TemperatureFeedService, TemperatureLogService

from http.HouseControlHttp import HouseControlHttpServer, HouseControlHttpRequestHandler
from configuation.ConfigurationReader import ConfigurationReader
from busservice.BusWorker import BusWorker

INTERVALL_UPDATE_TEMPERATURE = 15
INTERVALL_LOG_TEMPERATURE = 60*5
INTERVALL_UPDATE_MIXER = 30


SCHEDULE_SERVICE_TEMPERATURE_UPDATER = "TemperatureFeedService"
SCHEDULE_SERVICE_TEMPERATURE_LOGGER = "TemperatureLogService"
SCHEDULE_SERVICE_TEMPERATURE_MIXERCONTROL = "MixerControlService"

#Alle Jobs, die die Heizung schalten bekommen das prefix!
SERVICE_HEATING_ACTION_PREFIX = "HA_"
#Alle Jobs, die die Rollos schalten bekommen auch etwas ab!
SERVICE_BLIND_ACTION_PREFIX = "BA_"


def schedulerListener(event):
    jobName = event.job.name
    if event.exception:
        logger = logging.getLogger(APPLICATION_LOGGER_NAME)
        logger.critical('Job crashed [' + jobName + ']')
        
    else:
        #print('The job worked :)[' + jobName + ']')
        pass


class HouseControl(object):
    
    __scheduler = None
    __heatingStatusBean = None
    
    busJobsQueue = Queue.Queue()
    busWorkerThread = BusWorker(busJobsQueue)
    
    def __init__(self):
        self.logger = logging.getLogger(APPLICATION_LOGGER_NAME)
        self.logger.info("HouseControl starting...")

        configurationReader = ConfigurationReader(self.logger, os.getcwd() + FILEPATH_CONFIGURATION)
        
        #Initialize HeatingStatusBean
        self.__initalizeHeatingStatusBean(configurationReader)
        
        #Initialize Scheduler
        self.__initializeScheduler(configurationReader)
        
        #Initialize BusQueueWorker
        self.busWorkerThread.setDaemon(True)        
        self.busWorkerThread.start() 
        
        self.logger.info("HouseControl started.")
        
        
    def __initalizeHeatingStatusBean(self, configurationReader):
        #HeatingStatusBean       
        self.__heatingStatusBean = HeatingStatusBean.HeatingStatusBean()
        
        #Configure Bean
        self.updateHeatingStatusBeanConfiguration(configurationReader)
        
        #Add ChangeListener
        self.__heatingStatusBean.addChangeListener(HeatingControlService.HeatingControlService(self))
        self.__heatingStatusBean.addChangeListener(HeatingSwitchService.HeatingSwitchService(self))
        ##self.__heatingStatusBean.addChangeListener(HeatingMonitorService.HeatingMonitorService(self))
        self.logger.info("HeatingStatusBean configured.")
            
            
    def __initializeScheduler(self, configurationReader):
        #Scheduler
        self.__scheduler = Scheduler()
        self.__scheduler.configure(standalone=True)
        self.__scheduler.add_listener(schedulerListener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        #SchedulerTasks
        #TemperaturFeedService, TemperatureLogService, MixerControlService
        self.__loadBaseSchedulerTasks()
        
        self.__scheduler.start()
        
        #Benutzerdefinierte Schaltzeiten
        self.loadUserSchedulerTasks(configurationReader)
        
        self.logger.info("Scheduler started.")
        
    
    def getHeatingStatusBean(self):
        return self.__heatingStatusBean
    
    def getScheduler(self):
        return self.__scheduler
    
        
    def __loadBaseSchedulerTasks(self):
        temperatureFeedService = TemperatureFeedService.TemperatureFeedService(self)
        temperatureLogService = TemperatureLogService.TemperatureLogService(self)
        mixerControlService = MixerControlService.MixerControlService(self)
        
        #TemperaturFeedService
        job = self.__scheduler.add_interval_job(temperatureFeedService.run, seconds=INTERVALL_UPDATE_TEMPERATURE)
        job.name = SCHEDULE_SERVICE_TEMPERATURE_UPDATER
        self.logger.info("Scheduler-Job [" + job.name + "] loaded.")

        #TemperatureLogService
        job = self.__scheduler.add_interval_job(temperatureLogService.run, seconds=INTERVALL_LOG_TEMPERATURE)
        job.name = SCHEDULE_SERVICE_TEMPERATURE_LOGGER
        self.logger.info("Scheduler-Job [" + job.name + "] loaded.")
        
        #MixerControlService
        job = self.__scheduler.add_interval_job(mixerControlService.run, seconds=INTERVALL_UPDATE_MIXER)
        job.name = SCHEDULE_SERVICE_TEMPERATURE_MIXERCONTROL
        self.logger.info("Scheduler-Job [" + job.name + "] loaded.")
        
        
    def updateHeatingStatusBeanConfiguration(self, configurationReader):
        temperatures = configurationReader.temperatures
        self.__heatingStatusBean.setUpperFloorFlowTargetTemperature(float(temperatures.get('ogv')))
        self.__heatingStatusBean.setGroundFloorFlowTargetTemperature(float(temperatures.get('egv')))
        self.__heatingStatusBean.setWaterTargetTemperature(float(temperatures.get('hotwater')))
    
    
    def reloadUserSchedulerTasks(self):
        self.removeUserSchedulerTasks()
        
        configurationReader = ConfigurationReader(self.logger, os.getcwd() + FILEPATH_CONFIGURATION)
        self.updateHeatingStatusBeanConfiguration(configurationReader)
        
        self.loadUserSchedulerTasks(configurationReader)
        
        
    def removeUserSchedulerTasks(self):
        prefixLen = len(SERVICE_HEATING_ACTION_PREFIX) 
        jobList = self.__scheduler.get_jobs()
        for job in jobList:
            jobName = job.name
            if(jobName[:prefixLen] == SERVICE_HEATING_ACTION_PREFIX):
                self.logger.info("Scheduler-Job [" + job.name + "] removed.")
                self.__scheduler.unschedule_job(job)


    def loadUserSchedulerTasks(self, configurationReader):
        baseCronSched = {'year':None, 'month':None, 'day':None, 'week':None, 'day_of_week':None, 'hour':None, 'minute':None, 'second':None, 'start_date':None}
        for task in configurationReader.heatingTasks:
            
            schedType = task.get('schedule').get('type') 
            if(schedType == 'cron'):
                cronSched = baseCronSched.copy()
                cronSched.update(task.get('schedule'))
                cronSched.pop('type')
                if(task.get('type') == 'changeHeatingStatus'):
                    taskFunction = self.__heatingStatusBean.setHeatingStatusMap
                    job = self.__scheduler.add_cron_job(taskFunction,
                                                        year=cronSched['year'], month=cronSched['month'], day=cronSched['day'],
                                                        week=cronSched['week'], day_of_week=cronSched['day_of_week'], 
                                                        hour=cronSched['hour'], minute=cronSched['minute'], second=cronSched['second'], 
                                                        start_date=cronSched['start_date'],
                                                        args=[task.get('status')])
                    n = SERVICE_HEATING_ACTION_PREFIX + str(task.get('name'))
                    job.name = n
        
        prefixLen = len(SERVICE_HEATING_ACTION_PREFIX) 
        jobList = self.__scheduler.get_jobs()
        for job in jobList:
            jobName = job.name
            if(jobName[:prefixLen] == SERVICE_HEATING_ACTION_PREFIX):
                self.logger.info("Scheduler-Job [" + jobName + "] loaded.")
        
    
    
if __name__ == '__main__':
    
    initializeApplicationLogger()
    logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    
    houseControl = HouseControl()
    
    try:
        httpServer = HouseControlHttpServer(('', 81), HouseControlHttpRequestHandler)
        httpServer.setHouseControl(houseControl)
        
        logger.info("Http-Server started.")
        httpServer.serve_forever()
        
    except Exception:
        print(Exception)
    
    while 1:
        time.sleep(60)