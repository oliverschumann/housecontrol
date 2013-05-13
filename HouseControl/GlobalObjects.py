'''
Created on 07.12.2012

@author: Oliver Schumann

Files to check for raspberryPi!

HouseControl.py              -> Check intervalls
HeatingSwitchService.py      -> Remove comments on Executes!
TemperatureFeedService.py    -> Adjust Execute, commandArgs

'''
import subprocess, os, logging

APPLICATION_LOGGER_NAME = "HouseControlLogger"
FILEPATH_SECURITY = "/config/security.json"
FILEPATH_CONFIGURATION = "/config/configuration.json"
FILEPATH_BASH = "/bash/"
FILEPATH_LOG = "/log/"

def executeShellCommand(commandArgs):
    pipe = ""
    try:
        pipe = (subprocess.Popen(commandArgs, stdout=subprocess.PIPE)).stdout.read()
    except Exception as inst:
        print(inst)
    return pipe


def initializeApplicationLogger():
    logPath = os.getcwd() + "/log/"
    
    logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    
    # create file handler which logs even debug messages
    fh = logging.handlers.TimedRotatingFileHandler(logPath + 'housecontrol.log', when="midnight", interval=1, backupCount=31, encoding='UTF-8', delay=False, utc=False)
    fh.setLevel(logging.INFO)
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)    