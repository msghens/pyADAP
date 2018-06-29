import ConfigParser, os
from cryptography.fernet import Fernet

def dcrypt(key,ct):
	f = Fernet(key)
	return f.decrypt(ct)
	

# Password file
config = ConfigParser.ConfigParser()
config.read(os.path.expanduser('~/.plconfig.ini'))
key = config.get('key','key')


#Stomp glassfish gateway Credentials
stompusername = dcrypt(key,config.get('pyadap','stompusername'))
stomppw = dcrypt(key,config.get('pyadap','stomppw'))
stomphost = dcrypt(key,config.get('pyadap','stomphost'))
stompport = dcrypt(key,config.get('pyadap','stompport'))
#Needs to be uniq
stompclientid = dcrypt(key,config.get('pyadap','stompclientid'))

#Active Directory Credentials
ADurl = dcrypt(key,config.get('pyadap','ADurl'))
adusername =  dcrypt(key,config.get('pyadap','adusername'))
adpassword = dcrypt(key,config.get('pyadap','adpassword'))
