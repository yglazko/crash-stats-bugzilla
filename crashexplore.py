import requests
import base64
import json
import simplejson
import urllib
import csv
import sys


#CSV Code Set-Up
#CSV CODE
f = open('crashesLastWeek.csv', 'wt')


bugList = []

class Bug:
	def __init__(self, iD):
		self.iD = iD
		self.sigs = []

class Sig:
	def __init__(self, iD):
		self.iD = iD
		self.crashWeek = 0

#r = requests.get('https://bugzilla.mozilla.org/rest/login?login=fakebugzilla@gmail.com&password=Testtest1')
#print r.text

#Making a list to hold strings of crash signatures, it's empty right now.
crash_sigs = []
url_list = []
url_list.append([])
url_list.append([])

#specify which fields I want to send to the bugzilla API
url = 'https://bugzilla.mozilla.org/rest/bug?include_fields=id,cf_crash_signature,status&f1=cf_tracking_firefox39&f2=cf_crash_signature&o1=equals&o2=isnotempty&resolution=---&v1=%2B'

#I'm grabbing the URL and turning it into a JSON string, which I will parse in the next call.
search_results=requests.get(url)
json_string = json.loads(search_results.text)

#I'm parsing the JSON string and grabbing the crash signatures from the bugs, and I'm stripping out unneeded spaces and symbols.
#Also populating the list that I made earlier.
for i in json_string['bugs']:
	tempID = str(i['id'])
	tempBug = Bug(tempID)
	temp = str(i['cf_crash_signature'])

	if temp.count('[@') > 1:
		temps = temp.split('[@')
		for i in temps:
			i = i.translate(None, ']').lstrip().rstrip()
			i = i.translate(None, '\n')
			tempSig = Sig(i)
			tempBug.sigs.append(tempSig)
	elif temp.count('[@') == 1:
		temp = temp[2:]
		temp = temp.translate(None, ']').lstrip().rstrip()
		tempSig = Sig(temp)
		tempBug.sigs.append(tempSig)
	bugList.append(tempBug)



#This is where I convert my crash sigs into 'url friendly' format
for b in bugList:
	for s in b.sigs:
		t = urllib.quote_plus(str(s.iD))
		url_list[0].append(t)
		url_list[1].append(str(s.iD))


	#.translate(None, '[@]').lstrip()

#Going through the crash_sigs strings, sending them to the crash-stats API, and returning a JSON object of their crash frequencies. And it doesn't work!
for i in range (0, len(url_list[0])):
		r = requests.get('https://crash-stats.mozilla.com/api/CrashesCountByDay/?signature='+ (url_list[0][i]) + '&start_date=2015-06-03&end_date=2015-06-10')
		jsonStr = json.loads(r.text)
		if 'errors' not in jsonStr.keys():
			for b in bugList:
				for c in b.sigs:
					if url_list[1][i] == c.iD:
						c.crashWeek = c.crashWeek + ((jsonStr['hits']['2015-06-03'] + jsonStr['hits']['2015-06-04'] + jsonStr['hits']['2015-06-05'] + jsonStr['hits']['2015-06-06'] + jsonStr['hits']['2015-06-07'] + jsonStr['hits']['2015-06-08'] + jsonStr['hits']['2015-06-09']))




for b in bugList:
	for c in b.sigs:
		print c.iD + " has had " + str(c.crashWeek) + " crashes last week."
			

writer = csv.writer(f)
writer.writerow(('Bug Id', 'Crash Signature', '# of Crashes'))
for bugs in bugList:
	for m in range (1, len(bugs.sigs)):
		writer.writerow( (bugs.iD,bugs.sigs[m].iD, bugs.sigs[m].crashWeek) )

f.close()
