'''
Created on 12.12.2012

@author: admin
'''
import cgi,time
from json import JSONEncoder 
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from heating.HeatingStatusBean import MODE_ON, MODE_OFF, HEATING_STATUS_UPPERFLOOR, HEATING_STATUS_GROUNDFLOOR,\
    HEATING_STATUS_WATER, HEATING_STATUS_CIRCUITPUMP, HEATING_PRG_PRESENCE, HEATING_PRG_ABSENCE

class HouseControlHttpServer(HTTPServer):
    
    __houseControl = None
    __heatingStatusBean = None
    
    def setHouseControl(self, houseControl):
        self.__houseControl = houseControl
        self.__heatingStatusBean = houseControl.getHeatingStatusBean()
        
    def getHouseControl(self):
        return self.__houseControl
    
    def getHeatingStatusBean(self):
        return self.__heatingStatusBean
        

class HouseControlHttpRequestHandler(BaseHTTPRequestHandler):
           
    def do_GET(self):
        try:
            if self.path.endswith("status.html"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("<html><head><title>Heating-Dashboard</title>")
                self.wfile.write("<script src=\"//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js\"></script>")
                self.wfile.write("<script src=\"//ajax.googleapis.com/ajax/libs/jqueryui/1.9.2/jquery-ui.min.js\"></script>")
                self.wfile.write("<script>   $(function() {        $('#check' ).button();        $( '#format' ).buttonset();")
                self.wfile.write("    });    </script>")
                self.wfile.write("</head><body>")
                self.wfile.write(self.__getStatusHtml())
                self.wfile.write(self.__getFormHtml())
                self.wfile.write("</body></html>")
                return
            
            elif (".json" in self.path > 0):
                print(self.path)
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                self.wfile.write("getData(" + self.__getStatusJson() + ")")
                return

            elif self.path.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        if(form.has_key("action")):
            actionValue = str(form["action"].value)
            if(actionValue != ""):
                
                heatingStatusBean = self.server.getHeatingStatusBean()
                houseControl = self.server.getHouseControl()
                
                if(actionValue == HEATING_STATUS_UPPERFLOOR or actionValue == HEATING_STATUS_GROUNDFLOOR or
                   actionValue == HEATING_STATUS_WATER or actionValue == HEATING_STATUS_CIRCUITPUMP):
                    heatingStatusMap = heatingStatusBean.getHeatingStatusMap()

                    if(heatingStatusMap[actionValue] == MODE_ON):
                        newHeatingStatusMap = {actionValue: MODE_OFF}
                    else:
                        newHeatingStatusMap = {actionValue: MODE_ON}
                    heatingStatusBean.setHeatingStatusMap(newHeatingStatusMap)
                elif (actionValue == "reload"):
                    pass
                elif (actionValue == "toggleProgram"):
                    heatingProgram = HEATING_PRG_PRESENCE if(heatingStatusBean.getHeatingProgram() == HEATING_PRG_ABSENCE) else HEATING_PRG_ABSENCE
                    heatingStatusBean.setHeatingProgram(heatingProgram)
                    pass
                elif (actionValue == "removeUserSchedulerTasks"):
                    houseControl.removeUserSchedulerTasks()
                    pass
                elif (actionValue == "loadUserSchedulerTasks"):
                    houseControl.loadUserSchedulerTasks()
                    pass
                elif (actionValue == "reloadUserSchedulerTasks"):
                    houseControl.reloadUserSchedulerTasks()
                    pass
        '''
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                print('\tUploaded %s (%d bytes)' % (field, file_len))
            else:
                # Regular form value
                print('\t%s=%s' % (field, form[field].value))       
        '''
        self.do_GET()
        
    def __getStatusHtml(self):
        heatingStatusBean = self.server.getHeatingStatusBean()
        houseControl = self.server.getHouseControl()
        
        heatingString = "<ul><li>HeatingProgram: %s</li><li>HeatingMode: %s</li><li>MixerMode: %s</li></ul>" % (("anwensend" if(heatingStatusBean.getHeatingProgram() == 1) else "abwesend"),heatingStatusBean.getHeatingMode(), heatingStatusBean.getMixerMode()) 
        tmpString = "<table><tr>"
        tmpString += "<td>" + heatingString + self.__convertBeanStringToHtml(heatingStatusBean.getHeatingStatusString()) + "</td>"
        tmpString += "<td>" + self.__convertBeanStringToHtml(heatingStatusBean.getTemperatureString()) + "</td>"
        tmpString += "<td>" + self.__convertBeanStringToHtml(heatingStatusBean.getPumpStatusString()) + self.__convertBeanStringToHtml(heatingStatusBean.getMaxTemperatureString()) + "</td>"
        tmpString += ("<td><ul>")
        schedulerJobs = houseControl.getScheduler().get_jobs()
        for job in schedulerJobs:
            tmpString += ("<li>%s | %s</li>" % (job.name, job.next_run_time)) 
        tmpString += ("</ul></td>") 
        tmpString += "</tr></table>"
         
        return tmpString

    def __getStatusJson(self):
        heatingStatusBean = self.server.getHeatingStatusBean()
        return JSONEncoder().encode(heatingStatusBean.getTemperatureMap())

    def __getFormHtml(self):
        tmpString = "<form method='post'>"
        heatingStatusBean = self.server.getHeatingStatusBean()
        for heatingComponent, status in heatingStatusBean.getHeatingStatusMap().iteritems():
            tmpString += "<input type='submit' value='" + heatingComponent + "' name='action'>"
        tmpString += "<br /><br />"
        tmpString += "<input type='submit' value='removeUserSchedulerTasks' name='action'>"
        tmpString += "<input type='submit' value='loadUserSchedulerTasks' name='action'>"
        tmpString += "<input type='submit' value='reloadUserSchedulerTasks' name='action'>"
        tmpString += "<br /><br />"
        tmpString += "<input type='submit' value='reload' name='action'> | <input type='submit' value='toggleProgram' name='action'>"
        tmpString += "</form>"
        return tmpString
    
    def __convertBeanStringToHtml(self, beanString):
        tmpList = beanString.split(", ")
        tmpString = ""
        for entry in tmpList:
            tmpString += "<li>" + entry + "</li>"
        return "<ul>" + tmpString + "</ul>"