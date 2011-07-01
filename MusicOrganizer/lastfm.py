
#
# Copyright (c) by Patryk Jaworski
# Contact:
# -> E-mail: Patryk Jaworski <skorpion9312@gmail.com>
# -> XMPP/Jabber: skorpion9312@jabber.org
#

import urllib;
import urllib.request;
import json;

class Main:
	# LastFM Authentication
	API_KEY = '50f6d00e55216448a307c023f2781061';
	API_SECRET = '77a2ab67a44af263bf2b4d53cba6b789';
	__token = None;
	__available = False;

	def __init__(self):
		response = self.execMethod('auth.gettoken', {'api_key': self.API_KEY, 'api_sig': self.API_SECRET}, False);
		try:
			self.__token = json.loads(response)['token'];
			self.__available = True;
		except:
			self.__available = False;
	
	def isAvailable():
		return self.__available;

	def execMethod(self, methodName, parameters, joinKey = True):
		URL = 'http://ws.audioscrobbler.com/2.0/?method=%s%s&format=json';
		params = '';
		for p in parameters:
			params += '&%s=%s' % (p, parameters[p]);
		if joinKey:
			URL += '&api_key=%s' % self.API_KEY;
		URL = URL % (methodName, params);
		print(URL);
		request = urllib.request.Request(URL);
		try:
			response = urllib.request.urlopen(request);
			content = response.read().decode('utf-8');
			return content;
		except:
			pass;
		return False;	
	
