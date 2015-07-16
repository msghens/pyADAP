# -*- coding: utf-8 -*-
#~ Representation of the Ellucian Person Class. Class will be used
#~ to make it easier to pass information between defs and processes.
#~ 
#~ Unlike the google provisioning that uses dictionary to represent a the user

import logging
import xmltodict


# setting module logger

logger = logging.getLogger('pyADAP.PersonRec')


class Person(object):
	#~ primaryRole = 'norole'

	def __init__(self,imsxml):
		self.userid = self.getUserID(imsxml)
		self.fname = self.getFname(imsxml)
		self.lname = self.getLname(imsxml)
		self.middle = self.getMiddle(imsxml)
		self.displayName = self.getdisplayName(imsxml)
		self.sisplayName2 = self.fname + ' ' + self.lname
		self.primaryRole = self.getPrimaryRole(imsxml)
		self.email = self.getEmail(imsxml)
		self.knumber = self.getKnumber(imsxml)
		self.password = self.getPasswd(imsxml)
		self.ADContainer = self.getADContainer(self.primaryRole)
		self.ADMemberOf = self.getMemberOf(self.primaryRole)
		logger.debug('Created person record for %s', self.userid)
		
		
		
	def getUserID(self,imsxml):
		for uid in imsxml['enterprise']['person']['userid']:
			if 'Logon ID' in uid['@useridtype']:
				return uid['#text']
		raise IndexError('SCTID not found')		 
		

	def getPrimaryRole(self,imsxml):
		for role in imsxml['enterprise']['person']['extension']['luminisperson']['customrole']:
			if role.startswith('Primary'): 
				 return role
		return 'none'
		
	def getADContainer(self,role):
		return {
			'Primarystudent' : 'OU=Users,OU=Students,DC=sbcc,DC=test',
			'Primaryadjfac'  : 'OU=Users,OU=Adjunct Faculty,DC=sbcc,DC=test',
			'Primarystaff'   : 'OU=Users,OU=Staff,DC=sbcc,DC=test',
			'Primaryfaculty' : 'OU=Users,OU=Faculty,DC=sbcc,DC=test',
			}.get(role, 'noOU')
	
	def getMemberOf(self,role):
		return {
			'Primarystudent' : 'CN=Students,CN=ForeignSecurityPrincipals,DC=sbcc,DC=test',
			'Primaryadjfac'  : 'CN=AdjunctFaculty,CN=ForeignSecurityPrincipals,DC=sbcc,DC=test',
			'Primarystaff'   : 'CN=Staff,CN=ForeignSecurityPrincipals,DC=sbcc,DC=test',
			'Primaryfaculty' : 'CN=FullTimeFaculty,CN=ForeignSecurityPrincipals,DC=sbcc,DC=test',
			}.get(role, 'noOU')
	
	def getFname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['given']
		
	def getLname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['family']
		
	def getMiddle(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['partname']['#text']
		
	def getdisplayName(self,imsxml):
		return imsxml['enterprise']['person']['name']['fn']
	
	def getEmail(self,imsxml):
		return imsxml['enterprise']['person']['email']	
	
	def getKnumber(self,imsxml):
		for knumber in imsxml['enterprise']['person']['userid']:
			if 'SCTID' in knumber['@useridtype']:
				return knumber['#text']
		raise IndexError('SCTID not found')
		 
	def getPasswd(self,imsxml):
		for passwd in imsxml['enterprise']['person']['userid']:
			if 'SCTID' in passwd['@useridtype']:
				return passwd['@password']
		raise IndexError('SCTID not found')		 
	


