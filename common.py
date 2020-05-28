import os
import datetime


standard_strftime_format = '%Y-%m-%d (%a) %I:%M:%S %p' # 2020-05-27 (Wed) 12:43:16 PM

class message:
	def __init__(self, _sender, _timestamp, _message):
		self.sender = _sender
		self.message = _message
		self.timestamp = _timestamp
		self.timestamp_string = self.timestamp.strftime(self.timestamp, '%Y-%m-%d (%a) %I:%M:%S %p')
		
def print_and_log(message_to_log, log_file=None):
	print(message_to_log)
	current_year = datetime.datetime.now().strftime("%Y")
	if(current_year not in message_to_log):
		message_to_log  = datetime.datetime.now().strftime('%Y-%m-%d (%a) %I:%M:%S %p') + ", " + message_to_log 
	if(log_file):
		if(os.path.exists(log_file)):
			access_mode = 'a'
		else:
			access_mode = 'w'
		with open(log_file, access_mode) as file:  
			file.write(message_to_log + '\n')
