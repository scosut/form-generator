import magic
import os
import re

class Validate:
	errors = []
	
	def __init__(self, data=None):
		if data is None:
			self.errors = []
		else:
			self.errors = data
	
	def isEmpty(self, val, msg):
		if val and val.strip():
			if msg in self.errors:
				self.errors.remove(msg)
				
			return False
		else:
			self.errors.append(msg)			
			return True
		
	def doMatch(self, val1, val2, msg):
		if val1.strip().lower() == val2.strip().lower():
			if msg in self.errors:
				self.errors.remove(msg)
				
			return True
		else:
			self.errors.append(msg)			
			return False
		
	def isEmail(self, val, msg):
		regex = '^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$'
		if re.search(regex, val):
			if msg in self.errors:
				self.errors.remove(msg)
				
			return True
		else:
			self.errors.append(msg)
			return False
		
	def isInteger(self, val, msg):
		regex = '^[0-9]+$'
		if re.search(regex, val):
			if msg in self.errors:
				self.errors.remove(msg)
				
			return True
		else:
			self.errors.append(msg)
			return False
	
	def isImage(self, file, el):
		if file:
			mime        = magic.from_buffer(file.read(), mime=True)
			image_types = ["image/jpeg", "image/png"]
			
			if mime not in image_types:
				self.errors.append(el+" must be jpeg or png.")
				return False
			else:				
				file.seek(0, os.SEEK_END)
				file_size = file.tell()
				
				if file_size > 1048576:
					self.errors.append(el+" file size must not exceed 1 MB.")
					return False
				else:
					return True
		else:
			self.errors.append("Please provide "+el+".")
			return False
	
	def isQuantity(self, val, msg):
		regex = '^[1-9][0-9]*$'
		if re.search(regex, val):
			if msg in self.errors:
				self.errors.remove(msg)
				
			return True
		else:
			self.errors.append(msg)
			return False
		
	def setError(self, msg):
		self.errors.append(msg)
		
	def getErrors(self):
		if (len(self.errors)) > 0:
			return self.errors
		else:
			return False