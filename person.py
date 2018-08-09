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
		logger.debug('Userid: %s', self.userid)
		self.fname = self.getFname(imsxml)
		logger.debug('Firstname: %s', self.fname)
		self.lname = self.getLname(imsxml)
		logger.debug('Lastname: %s', self.lname)
		self.middle = self.getMiddle(imsxml)
		logger.debug('Middlename: %s', self.middle)
		self.displayName = self.getdisplayName(imsxml)
		logger.debug('DisplayName: %s', self.displayName)
		self.sisplayName2 = self.fname + ' ' + self.lname
		logger.debug('DisplayName2: %s', self.sisplayName2)
		self.primaryRole = self.getPrimaryRole(imsxml)
		logger.debug('Primary Role: %s', self.primaryRole)
		self.email = self.getEmail(imsxml)
		logger.debug('Email: %s', self.email)
		self.knumber = self.getKnumber(imsxml)
		logger.debug('Knumber: %s', self.knumber)
		self.password = self.getPasswd(imsxml)
		logger.debug('Password: %s', "XXXXXX")
		self.ADContainer = self.getADContainer(self.primaryRole)
		logger.debug('AD Container: %s', self.ADContainer)
		self.ADMemberOf = self.getMemberOf(self.primaryRole)
		logger.debug('AD Member: %s', self.ADMemberOf)
		logger.debug('Created person record for %s', self.userid)
		
		
		
	def getUserID(self,imsxml):
		for uid in imsxml['enterprise']['person']['userid']:
			if 'Logon ID' in uid['@useridtype']:
				return uid['#text']
		raise IndexError('SCTID not found')		 
		

	def getPrimaryRole(self,imsxml):
		try:
			if type(imsxml['enterprise']['person']['extension']['luminisperson']['customrole']) is unicode:
				role = imsxml['enterprise']['person']['extension']['luminisperson']['customrole']
				if role.startswith('Primary'):
					logger.debug('Primary Role: %s', role)
					return role
				else:
					logger.debug('Primary Role: none')
					return 'none'
		except:
			pass
		
		try:
			for role in imsxml['enterprise']['person']['extension']['luminisperson']['customrole']:
				if role.startswith('Primary'): 
					logger.debug('Primary Role: %s', role)
					return role
			
		except:
			pass
		logger.debug('Primary Role: none')
		return 'none'
		
	def getADContainer(self,role):
		return {
			'Primarystudent' : 'OU=Users,OU=Students,DC=sbcc,DC=local',
			'Primaryadjfac'  : 'OU=Users,OU=Adjunct Faculty,DC=sbcc,DC=local',
			'Primarystaff'   : 'OU=Users,OU=Staff,DC=sbcc,DC=local',
			'Primaryfaculty' : 'OU=Users,OU=Faculty,DC=sbcc,DC=local',
			'Primaryretiree'   : 'OU=Users,OU=Staff,DC=sbcc,DC=local',
			}.get(role, 'OU=Users,OU=Students,DC=sbcc,DC=local') #Used to be noOU. change to student as default
	
	def getMemberOf(self,role):
		return {
			'Primarystudent' : 'CN=Students,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local',
			'Primaryadjfac'  : 'CN=AdjunctFaculty,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local',
			'Primarystaff'   : 'CN=Staff,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local',
			'Primaryfaculty' : 'CN=FullTimeFaculty,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local',
			'Primaryretiree'   : 'CN=Staff,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local',
			}.get(role, 'CN=Students,CN=ForeignSecurityPrincipals,DC=sbcc,DC=local') #Used to be noOU. change to student as default
	
	def getFname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['given']
		
	def getLname(self,imsxml):
		return imsxml['enterprise']['person']['name']['n']['family']
		
	def getMiddle(self,imsxml):
		try:
			return imsxml['enterprise']['person']['name']['n']['partname']['#text']
		except:
			return ' '
		
	def getdisplayName(self,imsxml):
		return imsxml['enterprise']['person']['name']['fn']
	
	def getEmail(self,imsxml):
		try:
			return imsxml['enterprise']['person']['email']
		except LookupError:
			logger.info('Email address not found, creating pipeline address')
			return self.userid + '@pipeline.sbcc.edu'
			return
		except:
			logger.info('Email Runtime error')
			return 'noemailaddress' 
	
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
	


