import hashlib;

#
# Copyright (c) by Patryk Jaworski
# Contact:
# -> E-mail: Patryk Jaworski <skorpion9312@gmail.com>
# -> XMPP/Jabber: skorpion9312@jabber.org
#

class StrategyInterface:
	"""
	Interface for all strategys
	"""
	def getHash(self, full_path):
		"""
		Get unique hash by full_path to file
		"""
		raise NotImplementedError;

class duplicatesDetector:
	__strategy = None;
	__duplicates = {};

	def __init__(self, strategy):
		self.__strategy = strategy;

	def feed(self, file):
		"""
		Add file to list of watching files
		Returns duplicate status (bool)
		"""
		duplicate = False;
		key = self.__strategy.getHash(file);
		if key not in self.__duplicates:
			self.__duplicates[key] = [];
		else:
			duplicate = True;
		if file not in self.__duplicates[key]:
			self.__duplicates[key].append(file);
		return duplicate;
	
	def reset(self):
		self.__duplicates = {};

	def debug(self):
		"""
		Just print internal dictionary
		"""
		print(self.__duplicates);

	def get(self, key):
		"""
		Get a list of files associated with key
		"""
		return self.__duplicates[self.__strategy.getHash(key)];

	def exists(self, key):
		return self.__strategy.getHash(key) in self.__duplicates;
		
class md5(StrategyInterface):
	def getHash(self, full_path):
		fp = open(full_path, 'rb');
		content = fp.read();
		fp.close();
		return hashlib.md5(content).hexdigest();

class sha1(StrategyInterface):
	def getHash(self, full_path):
		fp = open(full_path, 'rb');
		content = fp.read();
		fp.close();
		return hashlib.sha1(content).hexdigest();

class basic(StrategyInterface):
	def getHash(self, full_path):
		return full_path;
		
