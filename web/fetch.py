# Runs commands on one or more connected machines (RasPis) to collect login info for teams
#
# Merges the info into the file activity.jsonp for consumption by an HTML5 page - see burn_down.html/.js
# activity.jsonp has the form:
#	x={
#		"session": {
#			"end": "2013-06-21 18:00",		(end of the session)
#			"session-factor": 100,			(multiplier for number of runs)
#			"seconds-factor": 200,			(multiplier for cumulative run-time)
#			"bar-duration": 5.5				(bar duration in hours for scaling)
#		},
#		"remotes": [
#			["raspberry", "pi@raspberrypi.local"],	(list of remotes to interrogate)
#			["raspberry", "pi@raspberrypi2.local"]
#		],
#		"login": {
#			'tomato': (36, 1.6200000000000008),	(teamname: (number of runs, cumulative time of runs) )
#			'green': (3, 0.44000000000000006),
#			'red': (4, 1.92)
#		},
#		finished: {
#			"unknown": "2013-06-21 12:00",	(team named and wall time team finished)
#			"erac": "2013-06-21 13:00"
#		}
#	}
# where:
#	only teams (effectively branch names) that have runon the RasPis are counted with cumulative logged-in time,
#	together with session & finished info from session.json
#
#	See team-stats file in home of remote user. This file is populated by cgi-bin/run-script.py

import os
import re
import json
import time
import datetime

def unsafeShell(remotehost, password, cmd, tmpFile='delme.tmp'):
	# Using plink as it's tricky getting ssh to work without keys...
	# Resulting lines end with \n
	cmd = '"C:\Program Files (x86)\putty\plink" -pw %s %s %s >%s' % (password, remotehost, cmd, tmpFile)
	os.system(cmd)
	f = open('delme.tmp', 'r')
	result = f.readlines()
	f.close()
	return result

def parseLineOfLast(line):
	fields = line.split(',')
	team = fields[0]
	delta = float(fields[2][0:-1])
	return (team,delta)

def fetchRemoteInfo(remotehost, password):
	# Command gets necessary info (teams, number of runs & cumulative run-time) from 'server'
	print remotehost,
	lines = unsafeShell(remotehost, password, 'cat team-stats')
	if len(lines) == 0:
		return {}

	results = {}

	# Accumulate number of times each team has remote run in count & time - ignore users not in teams
	for line in lines:
		a = parseLineOfLast(line)
		name = a[0]
		if not(name in results):
			results[name] = (0,0.0)

		count = results[name][0] + 1
		seconds = results[name][1] + a[1]
		results[name] = (count, seconds)
	print results
	return results

while True:
	time.sleep(2)

	try:
		fp = open('session.json', 'r')
		data = json.load(fp)
		fp.close()
	except (ValueError, IOError) as e:
		if type(e) != IOError:
			fp.close()
		print ">>>> Failing to read session.json <<<<<", e
		data = {}

	remotes = data['remotes']
	data['login'] = {}

	# Fetch all the machines' activity info & merge it
	for remote in remotes:
		aMachine = fetchRemoteInfo(remote[1], remote[0])
		for team in aMachine.keys():
			if team in data['login']:
				seconds  = data['login'][team][0] + aMachine[team][0]
				loggedIn = data['login'][team][1] | aMachine[team][1]
				data['login'][team] = (seconds, loggedIn)
			else:
				data['login'][team] = aMachine[team]

	print data

	# Write activity.jsonp
	fp = open('activity.jsonp', 'w')
	fp.write('x=')
	json.dump(data, fp)
	fp.close()
