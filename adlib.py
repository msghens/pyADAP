#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  adlib.py
#  
#  Copyright 2015 Unknown <mghens@mgarch-vb>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.18133
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

# import sys is my friend!
import sys
import logging
import ldap
from person import Person
import netrc,base64,zlib
import ldap.modlist as modlist



#~ Create a AD connection with clean up. Must be called
#~ 'with' statement
#~ usage: with ADconnection as adc

# setting module logger

logger = logging.getLogger('pyADAP.adlib')



class ADconnection(object):
	
	
	def __enter__(self):
		
		#Initializaion  vars 
		HOST = 'testad.sbcc.local'
		ADurl ='ldaps://10.1.28.167'
		
		#this keeps the password out of the code and out of revision control
		secrets = netrc.netrc()
		username,account,password = secrets.authenticators( HOST )
		
		#LDAP Connection
		try:
			# Fix MS Issues
			ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
			ldap.set_option(ldap.OPT_REFERRALS,0)
			
			self.ldap_connection = ldap.initialize(ADurl)
			self.ldap_connection.simple_bind_s(username, password)
		except ldap.LDAPError, e:
			sys.stderr.write('Error connecting to LDAP server: ' + str(e) + '\n')
			# Needs to fail gracefully such as just dump to bit bucket
			sys.exit(1)
		
		logger.debug("Connected to AD")
		return self.ldap_connection 
	
	def __init__(self):
		return None
		
	def __exit__(self, type, value, traceback):
		self.close()
		
	def close(self):
		logger.debug("Disconnecting from AD")
		self.ldap_connection.unbind_s()
		


class adlib(object):
	
	def __init__(self,imsperson):
		self.perrec = imsperson
		
		#Base dn. Outside config????
		self.base_dn = 'dc=sbcc,dc=test'
		self.dn = None
		self.inADFlag = None
		
	def inAD(self,cn=None):
		if cn is None:
			cn=self.perrec.userid
		
		
		#instatiate class. Why? Who knows...
		ad = ADconnection()
		with ad as ldapconn:
			try:
				
				searchfilter = ('(&(objectCategory=person)(&(objectClass=user)(sAMAccountName=%s)))' % cn)
				
				user_results = ldapconn.search_s(self.base_dn, ldap.SCOPE_SUBTREE,searchfilter)
				
				#~ user_results = ldapconn.search_s(self.base_dn, ldap.SCOPE_SUBTREE,
                                              #~ '(&(sAMAccountName=' +
                                              #~ cn +
                                              #~ ')(objectClass=person))',
                                              #~ ['distinguishedName'])
                                              
				dn = user_results[0][0]
				if dn is None:
					return False
			except ldap.LDAPError, error_message:
				print "error finding username: %S" % error_message
				self.inADFlag = False
				return False
			except:
				self.inADFlag = False
				return False
		self.inADFlag = True
		return True
		
	
	def chgPwd(self,cn=None):
		if cn is None:
			cn=self.perrec.userid
			
		#instatiate class. Why? Who knows...
		ad = ADconnection()
		with ad as ldapconn:
			try:
				searchfilter = ('(&(objectCategory=person)(&(objectClass=user)(sAMAccountName=%s)))' % cn)
				logger.debug(searchfilter)
				user_results=ldapconn.search_s(self.base_dn,ldap.SCOPE_SUBTREE,searchfilter)
				logger.debug(user_results)
				dn = user_results[0][0]
				#~ print dn
				if dn <> None:
					#placeholder for logging
					#print 'updating ' + user['username'],time.ctime()
					adpass = ('"%s"' % self.perrec.password).encode("utf-16-le")
					# Update Password
					mod_attrs = [( ldap.MOD_REPLACE, 'unicodePwd', adpass ),( ldap.MOD_REPLACE, 'unicodePwd', adpass)]
					# Update Role
					mod_attrs.append( (ldap.MOD_REPLACE, 'employeeType', str(self.perrec.primaryRole)) )
					#Update Knumber
					mod_attrs.append( (ldap.MOD_REPLACE, 'employeeID', str(self.perrec.knumber)) )
					
					
					#~ #Reenable user
					#~ UC = int(results[0][1]['userAccountControl'][0])
					#~ if UC & (1<<1):
						 #~ UC = UC & ~(1 << 1)
						 #~ UCattrib = (ldap.MOD_REPLACE, 'userAccountControl', str(UC))
						 #~ mod_attrs.append(UCattrib)
					print mod_attrs
					ldapconn.modify_s( dn, mod_attrs )
					logger.info('Updated password for %s', str(cn))
					
					#work on logging

			except ldap.LDAPError, error_message:
				#~ print "error finding username: %s" % error_message
				return False
			
		
	def addUser(self):
		# Build User
		
		if self.perrec.ADContainer == 'noOU':
			logger.debug('User does not have container')
			logger.error('AD Account not created for: ', self.perrec.userid)
			raise ValueError('User not create')
			return False
		
		user_dn = 'cn=' + self.perrec.userid + ',' + self.perrec.ADContainer
		logger.debug('User DN for new user: %s', user_dn)
		
		user_attrs = {}
		user_attrs['objectClass'] = \
				['top', 'person', 'organizationalPerson', 'user']
		user_attrs['cn'] = str(self.perrec.userid)
		user_attrs['userPrincipalName'] = str(self.perrec.userid) + '@' + 'sbcc.test'
		user_attrs['sAMAccountName'] = str(self.perrec.userid)
		user_attrs['givenName'] = str(self.perrec.fname)
		user_attrs['sn'] = str(self.perrec.lname)
		user_attrs['displayName'] = str(self.perrec.displayName)
		user_attrs['userAccountControl'] = '514'
		user_attrs['mail'] = str(self.perrec.userid) + '@pipeline.sbcc.edu'
		user_attrs['employeeID'] = str(self.perrec.knumber)
		user_ldif = modlist.addModlist(user_attrs)
		
		ad = ADconnection()
		with ad as ldapconn:
			#~ logger.debug('LDIF' + user_ldif)
			ldapconn.add_s(user_dn,user_ldif)
			add_member = [(ldap.MOD_ADD, 'member', str(user_dn))]
			ldapconn.modify_s(self.perrec.ADMemberOf,add_member)
		self.chgPwd()
		logger.info('User added to AD: %s', user_dn)
	
			
