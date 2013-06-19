#!/usr/bin/python
import requests
import hashlib
import os
import subprocess as sub
import sys
from time import sleep
from datetime import datetime
def flush():
	sys.stdout.flush()
	sys.stderr.flush()
logfile = open("message.log","w")
sys.stdout = logfile
sys.stderr = logfile
rest_time = 10
urlbase="http://home.oddtoast.com:27277"
os.system("midori -a file:///home/swag/index.html &")
#sub.call(["midori","-a","file:///home/alex/home.html","&"])
prefix="/home/swag" #ABSOLUTE directory
if prefix != '' and prefix[-1:] != '/':
	prefix = prefix+'/'
if prefix != '' and prefix[:1] != '/':
	print(prefix + " is not an absolute path, exiting")
	sys.exit(-1)

master_location = prefix+"master.md5"
sums_location=prefix+"md5sums"

def exists(filename):
	return os.path.exists(filename)

if not exists(prefix) and prefix != '':
	os.makedirs(prefix)

def checkStatus(r,fatal=True):
	if r.status_code!=200:
		print(r.url + " lead to " + code)
		if fatal:
			sys.exit(-1)
def refreshBrowser():
	print("refreshing browser (midori)")
	os.system("DISPLAY=:0 xdotool key F5 &")
def downloadFile(url,filename,file_hash=""):
	filename=prefix+filename
	r = requests.get(url)
	checkStatus(r,fatal=False)
	dir = os.path.dirname(filename)
	if dir != "" and not os.path.exists(dir):
		os.makedirs(os.path.dirname(filename))
		#if r.headers["content-type"] == "text/html":
		#	f = open(filename,'w')	
		#	f.write(r.text)
		#	f.close()
		#else:

	#else:
	#	print("didnt download {0}", filename)
	#print(filename)
	f = open(filename,'wb')
	f.write(r.content)
	f.close()
	if file_hash != "":
		current_hash = hashlib.md5(r.text.encode("UTF-8")).hexdigest()
		if current_hash != file_hash:
			print("hash check failed on {0} from {1}, purported hash {2} does not equal actual hash {3}, redownloading", filename,url,file_hash,current_hash)
			downloadFile(url,filename,file_hash)
while True:
	if os.path.exists(master_location):
		r = requests.get(urlbase+"/master.md5")
		f=open(master_location)
		oldhash = f.read().split()[0]
		newhash = r.text.split()[0]
		if oldhash == newhash:
			print("master hashes are the same")
		else:
			print("master hashes different, checking individuals...")
			r = requests.get(urlbase+"/md5sums")
			checkStatus(r)
			hashes = r.text.split("\n")
			existing_hashes = {}
			#create dictionaries instead for key comparisons
			if(not exists(sums_location)):
				downloadFile(urlbase+"/md5sums","md5sums")
			sums = open(sums_location).read()
			lines = sums.split('\n')
			for i in lines:
				pair=i.split()
				if len(pair)>0:
					existing_hashes[pair[1][2:]] = pair[0]				
			for i in hashes:
				pair = i.split()
				if len(pair)>0:
					h = pair[0]
					filename=pair[1][2:]
					url = urlbase+pair[1][1:]
					if filename in existing_hashes:
						if existing_hashes[filename] == h: #check for hash equality
							print(filename + " is the same, skipping")
						else:
							print(filename + " is different, downloading")
							downloadFile(url,filename)
						del existing_hashes[filename] #del pair from dictionary, then check leftover and delete
					else:
						print(filename + " doesn't exist, downloading")
						downloadFile(url,filename)
			for i in existing_hashes:			
				os.remove(prefix+i)
				print("deleting file {0}, unused".format(prefix+i))
			downloadFile(urlbase+"/md5sums", "md5sums") #download new sums to override old one
			downloadFile(urlbase+"/master.md5", "master.md5") #download new master hash
			refreshBrowser()
	else:
		downloadFile(urlbase+"/master.md5", "master.md5")
		print("master.md5 doesn't exist, downloading all files")
		print("Downloading master.md5 to {0}".format(master_location))
		r = requests.get(urlbase+"/md5sums")
		checkStatus(r)
		hashes = r.text.split("\n")
		#create dictionaries instead for key comparisons
		for i in hashes:
			pair = i.split()
			if len(pair)>0:
				filename=pair[1][2:]
				url = urlbase+pair[1][1:]
				print("downloading " + filename)
				downloadFile(url,filename)
		downloadFile(urlbase+"/md5sums","md5sums")
		refreshBrowser()
	print(datetime.now())
	flush()
	sleep(rest_time)
