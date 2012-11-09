#!/usr/bin/python

import pexpect
import base64
from threading import Thread
from Queue import Queue

class connectOA(Thread):

	def __init__(self, queue):
		self.queue = queue
		Thread.__init__(self)

	def run (self):

		while 1:
                        item = self.queue.get()
                        if item is None:
                                break
		
			#Transpose old, passed varilables, to ones now passed by
			#Queue don't want to have to change them in the code below 
			#(Yes, I am that lazy)

			oaname = item[0]
			user = item[1]
			password = item[2]
	
			#Get the shortname from the FQDN of the OA
			shname = oaname.split(".")[0]
				
			fp = open(shname.lower() + ".txt","w")

			#Add ">" to end of shname to match the prompt
			#Also create a expect vaiable for OA's that are using the failover OA 
			#   ie. shname-1
			shname_fo = shname + "-1>"
			shname = shname + ">"	
			connoa = pexpect.spawn("ssh " + user + "@"+ oaname)
			rc=connoa.expect(["password:", '\)\?', pexpect.EOF])

			if rc == 1: 
				connoa.sendline("yes")
				connoa.expect("password:")
			if rc == 2:
				fp.write("Unable to connect to OA")
				fp.close()	
				return
			
			connoa.sendline(password)
			rc=connoa.expect([shname.upper(), shname.lower(), "password:", shname_fo.upper(), shname_fo.lower()])
			if rc == 2:
				fp.write("Incorrect Password for OA")
				fp.close()
				return	
			connoa.logfile = fp
			connoa.sendline("show all")
			connoa.expect([shname.upper(), shname.lower(), shname_fo.upper(), shname_fo.lower()], timeout=400)
			connoa.sendline("exit")
			fp.close()


if __name__ == "__main__":

	
	#Create the Queue Object.
	queue = Queue(0)


	oafp = open ("oanames.txt", "r")
	oas = oafp.read()
	oas = oas.split("\n")
	#Get rid of the last blank entry in the array because of the split
	oas.pop()

	oafp.close()
	
	infofp = open (".datafile","r")
	linfo=infofp.read()
	linfo=linfo.split("\n")

	
	#Fill the Queue with all of the oainfo		
	for oaname in oas:
		queue.put([oaname,base64.b64decode(linfo[0]),base64.b64decode(linfo[1])]) 			
	
	#Fill in the Queue with the 'None' item to stop/kill the threads
	for i in range(10):
		queue.put(None)		

	for i in range(10):
		connectOA(queue).start()
	
		
