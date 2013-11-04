#!/usr/bin/env python
import cgi
import cgitb
import logging 
import telnetlib
import os
import subprocess
import socket

class Logger:
 LOG_FILENAME = '/FIXME/logs/python.log'
 scriptname=None
 logger=None

 def debug(self,message):
  self.logger.debug(message)

 def __init__(self,scriptname):
  logging.basicConfig(filename=self.LOG_FILENAME,level=logging.DEBUG)
  self.scriptname=scriptname
  self.logger=logging.getLogger(scriptname)

class Vlc:
 """ Permite comunicar con VLC"""
 connected=False
 tn=telnetlib.Telnet()
 logger=None

 def __init__(self,logger):
  self.logger=logger

 def connect(self):
  l=self.logger
  if not self.connected:
   try:
    self.tn.open('127.0.0.1',6885)
    l.debug(self.tn.read_until("> ",2))
    self.connected=True
    l.debug('connect completado')
   except socket.error,e:
    print 'Cannot connect to vlc - '+str(e)+'<br>\n'
  else:
   l.debug('connect already connected')

 def sendcommand(self,command):
  result=self.sendcommand_raw(command).replace('\n','<br>\n')
  return result

 def sendcommand_raw(self,command):
  l=self.logger  
  if self.connected:
   self.tn.write(command+"\n")
   resultado=self.tn.read_until("> ",2)[:-2]
  else:
   resultado='Error: Not connected'
  l.debug(resultado)
  return resultado


 def disconnect(self):
  l=self.logger
  if self.connected:
   self.tn.write("quit\n")
   l.debug(self.tn.read_until("Bye-bye!",2))
   self.tn.close()
   self.connected=False
   l.debug('disconnect completed')
  else:
   l.debug('disconnect not connected')
  

class Main:
 vlc=None
 extensions=set (['avi','divx','flv','mp4','mp3','mkv','ogg','wav'])
 logger=None

 def getPrintableTime(self,secs):
  l=self.logger
  l.debug('secs = '+str(secs))
  if isinstance(secs,int):
   l.debug('secs is int')
   l.debug(str(secs / 60)) 
   result='{0:0>2}:{1:0>2}'.format((secs / 60),(secs % 60))
  else:
   l.debug('secs is not int')
   result='00:00'
  return result

 def add_action(self,command,path='/my/videos/hollywood'):
  l=self.logger
  l.debug('add_action path='+path)
  dirtoshow=os.listdir(path)
  indexuppath=path.rfind('/')
  if indexuppath== -1: uppath=None
  else: uppath=path[:indexuppath]
  print '<p>\n'
  if uppath is not None: print '<a href="vlc.py?action=add&path='+uppath+'">up</a><br>\n'
  for subdir in dirtoshow:
   if os.path.isdir(os.path.join(path,subdir)):
    print '<a href="vlc.py?action=add&path='+path+'/'+subdir+'">'+subdir+'</a><br>\n'
  for fil in dirtoshow:
   indexpoint=fil.rfind('.')
   if indexpoint != -1:
    ext=fil[indexpoint+1:].lower()
    if ext in self.extensions:
     print '<a href="vlc.py?action=add&path='+path+'&command=file://'+path+'/'+fil+'">'+fil+'</a><br>\n'
  print '</p>\n'
  if command is not None:
   self.vlc.sendcommand("add "+command)
   print "add "+command+" - done<br>\n"
 
 def control_action(self,command):
  l=self.logger
  v=self.vlc
  if command is None: l.debug('inside control_action no command')
  else: l.debug('inside control_action '+command)

  get_time=v.sendcommand_raw("get_time")
  if get_time.find('Error') != -1: 
   l.debug('Error found')
   get_time = -1
  else: 
   l.debug('Error not found')
   get_time = int(get_time)
  get_length=v.sendcommand_raw("get_length")
  if get_length.find('Error') != -1: get_length = -1
  else: get_length=int(get_length)
 
  print '<p>\n\
  <a href="vlc.py?action=control&command=play">play</a><br>\n\
  <a href="vlc.py?action=control&command=pause">pause</a><br>\n\
  <a href="vlc.py?action=control&command=stop">stop</a><br>\n\
  <a href="vlc.py?action=control&command=seek0">go0</a><br>\n\
  <a href="vlc.py?action=control&command=seek-1800">-30min</a><br>\n\
  <a href="vlc.py?action=control&command=seek-300">-5min</a><br>\n\
  <a href="vlc.py?action=control&command=seek-60">-1min</a><br>\n\
  <a href="vlc.py?action=control&command=seek-10">-10sec</a><br>\n\
  <a href="vlc.py?action=control&command=seek+10">+10sec</a><br>\n\
  <a href="vlc.py?action=control&command=seek+60">+1min</a><br>\n\
  <a href="vlc.py?action=control&command=seek+300">+5min</a><br>\n\
  <a href="vlc.py?action=control&command=seek+1800">+30min</a><br>\n\
  </p>\n'
  print 'status='+self.vlc.sendcommand("status")+'<br>\n'
  if get_time != -1: print 'Current '+self.getPrintableTime(get_time)+'<br>\n'
  if get_length != -1:  print 'Total '+self.getPrintableTime(get_length)+'<br>\n'

  if command is not None:
   if command == "play": v.sendcommand("play")
   if command == "pause": v.sendcommand("pause")
   if command == "stop": v.sendcommand("stop")
   if command.startswith('seek') and get_time != -1: 
    if command[4] == '0':
     value=0
    else:
     value=int(command[5:])
     l.debug('value '+str(value))
     # urls or python converts '+' in ' ' (very weird)
     if command[4] == ' ': 
	value=get_time+value
	l.debug('signal +')
     elif command[4] == '-': 
        value=get_time-value
	l.debug('signal +')
     else:
        value=-1
	l.debug('Invalid signal='+command[4])
        print 'Invalid signal='+command[4]+'<br>\n'
    if value >= 0:
     l.debug ('seek '+str(value))
     v.sendcommand('seek '+str(value))
    else:
     l.debug('Invalid seek value '+str(value))
     print 'Invalid seek value '+str(value)+'<br>\n'
   print command+" - done<br>\n"

 def babyeinstein_action(self,command):
  l=self.logger
  v=self.vlc
  v.sendcommand("clear")
  v.sendcommand("random")
  v.sendcommand("add /my/videos/kids/BabyEinstein")
  #TODO: write pause
  v.sendcommand("f")

 def fullscreen_action(self,command):
  self.vlc.sendcommand("f")

 def playlist_action(self,command):
  l=self.logger
  print '<p>\n\
   <a href="vlc.py?action=add">add</a><br>\n\
   <a href="vlc.py?action=playlist&command=clear">clear</a><br>\n\
  </p>\n'
  if command == "clear": self.vlc.sendcommand("clear")
  if command is not None: print command+" - done<br>\n"
  print self.vlc.sendcommand("playlist")+'<br>\n'

 def process_action(self,command):
  l=self.logger
  print '<p>\n\
  <a href="vlc.py?action=process&command=restart">restart</a><br>\n\
  <a href="vlc.py?action=process&command=shutdown">shutdown</a><br>\n\
  </p>\n'
  if command == "restart":
   output=subprocess.Popen(["sudo", "/opt/scripts/controlservices.sh", "vlcrestart"],stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
   print output[0]
   print output[1]
  if command == "shutdown": self.vlc.sendcommand("shutdown")
  if command is not None: print command+" - done<br>\n"

 def volume_action(self,command):
  l=self.logger
  v=self.vlc
  print '<p>\n\
  <a href="vlc.py?action=volume&command=down">down</a><br>\n\
  <a href="vlc.py?action=volume&command=downabit">downabit</a><br>\n\
  <a href="vlc.py?action=volume&command=full">full</a><br>\n\
  <a href="vlc.py?action=volume&command=half">half</a><br>\n\
  <a href="vlc.py?action=volume&command=mute">mute</a><br>\n\
  <a href="vlc.py?action=volume&command=up">up</a><br>\n\
  <a href="vlc.py?action=volume&command=upabit">upabit</a><br>\n\
  </p>\n'
  if command == "down": v.sendcommand("voldown")
  if command == "downabit": v.sendcommand("volume -1")
  if command == "full": v.sendcommand("volume 100")
  if command == "half": v.sendcommand("volume 50")
  if command == "mute": v.sendcommand("volume 0")
  if command == "up": v.sendcommand("volup")
  if command == "upabit": v.sendcommand("volume +1")
  print v.sendcommand("volume")+'<br>\n'
  if command is not None:
   print command+" - done<br>\n"

 def vratio_action(self,command):
  l=self.logger
  v=self.vlc
  print '<p>\n\
  <a href="vlc.py?action=vratio&command=1610">16:10</a><br>\n\
  <a href="vlc.py?action=vratio&command=43">4:3</a><br>\n\
  </p>\n'
  if command == "1610": v.sendcommand("vratio 16:10")
  if command == "43": v.sendcommand("vratio 4:3")
  print v.sendcommand("vratio")+'<br>\n'
  if command is not None: print command+" - done<br>\n"

 def __init__(self):
  action=None
  command=None
  path=None
  print 'Content-type: text/html\n'
  print '<!DOCTYPE HTML>\n\
  <html>\n\
  <head>\n\
   <link rel="stylesheet" type="text/css" href="/css/my.css" />\n\
   <meta name="HandheldFriendly" content="true" />\n\
   <meta name="viewport" content="width=device-width, height=device-height, user-scalable=no" />\n\
   <title>vlc</title>\n\
  </head>\n\
  <body>\n\
   <p><div class="header">VLC</div></p>\n\
   <p>\n\
   <a href="vlc.py?action=babyeinstein">babyeinstein</a><br>\n\
   <a href="vlc.py?action=control">control</a><br>\n\
   <a href="vlc.py?action=fullscreen">fullscreen</a><br>\n\
   <a href="vlc.py?action=playlist">playlist</a><br>\n\
   <a href="vlc.py?action=process">process</a><br>\n\
   <a href="vlc.py?action=volume">volume</a><br>\n\
   <a href="vlc.py?action=vratio">vratio</a><br>\n\
  </p>\n\
  <p><a href="..">up</a></p>\n\
  <div class="result">\n'
  try:
   self.logger=Logger(os.environ['SCRIPT_NAME'])
   l=self.logger
   l.debug('main - gettingFields')
   form = cgi.FieldStorage() # parse query
   if form.has_key("action") and form["action"] != "":
    self.vlc=Vlc(self.logger)
    v=self.vlc
    v.connect()
    action=form["action"].value
    l.debug('Executing action '+action)
    if form.has_key("command") and form["command"] != "": 
     command=form["command"].value
     l.debug('command '+command)
    if form.has_key("path") and form["path"] != "": 
     path=form["path"].value
     l.debug('path='+path)
    if action == "add": 
     if path is None: self.add_action(command)
     else: self.add_action(command,path)
    else:
     try:
      f=getattr(self,action+'_action')
      f(command)
     #except AttributeError:
     # print 'Invalid action<br>\n'
     finally:
      pass
    print action+' - done<br>\n' 
   else:
    print 'Select an action'
  except:
   print 'Oops. An error ocurred.<br>\n'
   cgi.print_exception() # Print traceback,safely
  finally:
   if self.vlc is not None:
    self.vlc.disconnect()
  print '</div></body>\n</html>'

cgitb.enable()
Main()

