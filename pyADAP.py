#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyADAP.py
#  
#  Copyright 2015 Michael Ghens <mghens@sbcc.edu>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  



#~ Python ADAP replacement. This uses Glassfish STOMP for connections

import sys
import logging
import logging.handlers
from stompy.simple import Client
import xmltodict
from pprint import pprint
from person import Person
from adlib import adlib
import base64,zlib
#import netrc,base64,zlib
from secure import stompusername,stomppw,stomphost,stompport,stompclientid


pool = None
			

def isPersonRecord(imsxml):
	if 'person' in imsxml['enterprise']:
		return True
	else:
		return False

def run_stomp():
	#initialize

	#~ Does connection and loops the stomp connection
	stomp = Client(host=stomphost, port=int(stompport))
	try:
		stomp.connect(username=stompusername,password=stomppw, clientid=stompclientid  )
	except Exception,e:
		print str(e)
		sys.exit("Cannot connect to STOMP Server")
	
	stomp.subscribe('/topic/com_sct_ldi_sis_Sync')

#Bad Users
	disuserset = set()
	disuserset.add('cemitchum')

	while True:
		try:
			message = stomp.get()
			imsrecord = xmltodict.parse(message.body)
			
			if isPersonRecord(imsrecord):
				try:
					imsperson = Person(imsrecord)
				except:
					logger.info('Person Error: %s', sys.exc_info()[0])
					continue
					

				ad = adlib(imsperson)

				try:
                                        if imsperson.userid in disuserset:
                                                continue
					if ad.inAD():
						logger.debug('Changing password for %s', imsperson.userid)
						ad.chgPwd()
					else:
						logger.debug('Adding user to AD %s', imsperson.userid)
						ad.addUser()
				except Exception, err:
					logger.info('Error processing user to AD %s', imsperson.userid)
					logger.info('ERROR: %s', str(err))
					continue
		except KeyboardInterrupt:
			print "Shutting Down"
			logger.info('Keyboard Interupt: Shutting down pyADAP')
			stomp.unsubscribe('/topic/com_sct_ldi_sis_Sync')
			stomp.disconnect()
			sys.exit(0)
			return

def initLogging():
	global logger
	#Initialize logging
	LOG_FILENAME = 'logs/pyADAP.log'
	logger = logging.getLogger('pyADAP')
	logger.setLevel(logging.INFO)
	
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	#Log file handler
	handler = logging.handlers.RotatingFileHandler(
					LOG_FILENAME, maxBytes=1024*1024, backupCount=10)

						
	#Console gets debug
	#~ console = logging.StreamHandler()
	#~ console.setFormatter(formatter)
	# create formatter and add it to the handlers
	#~ formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)				
	logger.addHandler(handler)
	#~ logger.addHandler(console)


def main():
	
	initLogging()
	
	logger.info('Starting pyAD')
	run_stomp()
	logger.info('Stopping pyAD')
	pool.terminate()
	return 0

if __name__ == '__main__':
	main()

