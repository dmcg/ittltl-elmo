# Runs commands on one or more connected machines (RasPis) to collect login info for teams
#
# Merges the info into the file activity.jsonp for consumption by an HTML5 page - see analogue_clock.html/.js
# activity.jsonp has the form:
#	{"red": 2580.0, "green": 131940.0, "blue": 4500.0}
# where:
#	all possible team names (i.e. all users except as listed in IGNORE) on the RasPis are
#	listed with cumulative logged-in time for each.
#
# 'last' output is formatted thus...
#          1         2         3         4         5         6         7         8         9
#0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
#reboot   system boot  3.2.27+          Sun Feb 10 23:36:42 2013 - Tue Feb 12 22:53:44 2013 (1+23:17)
#b_ark    pts/2        192.168.2.3      Mon Feb  4 22:55:15 2013 - Tue Feb  5 12:03:23 2013  (13:08)
#pi       pts/1        192.168.2.3      Tue Feb 12 17:04:26 2013   still logged in
#---------                                  --------------------                            ---------
#[0:9]                                      [43:63]                                         [91:-1]
#		time.strptime(line[43:63], "%b %d %H:%M:%S %Y")		re.split("((\d+)\+)?(\d{2}):(\d{2})", line[91:-1])

import os
import re
import json
import time
import datetime

# password!		user@host
remotes = [\
('raspberry', 'pi@raspberrypi.local'),
('raspberry', 'pi@raspberrypi2.local')]

IGNORE = ("Desktop", "pi", "reboot", "root")

def unsafeShell(remotehost, password, cmd, tmpFile='delme.tmp'):
	# Using plink as it's tricky getting ssh to work without keys...
	# Resulting lines end with \n
	cmd = '"C:\Program Files (x86)\putty\plink" -pw %s %s %s >%s' % (password, remotehost, cmd, tmpFile)
	os.system(cmd)
	f = open('delme.tmp', 'r')
	result = f.readlines()
	f.close()
	return result

def parseLineOfLast(now, line):
    if len(line.strip()) == 0:
        return None
    if line.startswith("wtmp"):
        return None
    user = line[0:9].strip()
    try:
        deltas = re.split("((\d+)\+)?(\d{2}):(\d{2})", line[91:-1])
        days = deltas[2]
        deltaT = datetime.timedelta(hours=int(deltas[3]), minutes=int(deltas[4]), days=0 if days is None else int(days)).total_seconds()
    except IndexError:
        end = now
        start = time.strptime(line[43:63], "%b %d %H:%M:%S %Y")
        deltaT = time.mktime(end) - time.mktime(start)
    return (user, deltaT)

def fetchRemoteInfo(remotehost, password):
	# Command gets necessary info (date-time, list of users, last info) from 'server'
	print remotehost,
	lines = unsafeShell(remotehost, password, 'date; ls /home; echo ===; last -F')
	if len(lines) == 0:
		return {}

	# Known team names on server (all with zero time spent initially)
	ix = lines.index('===\n')

	teams = [name[:-1] for name in lines[1:ix] if name[:-1] not in IGNORE]
	results = {team: 0 for team in teams}

	# Now on 'server'
	now = time.strptime(lines[0][4:], "%b %d %H:%M:%S UTC %Y\n")

	# Accumulate logged in time - ignore users not in teams
	for line in lines[ix+1:]:
		a = parseLineOfLast(now, line)
		if a is None:
			continue
		if a[0] in results:
			results[a[0]] = results[a[0]] + a[1]
	return results

while True:
	time.sleep(2)
	activities = dict()

	# Fetch all the machines' activity info & merge it
	for remote in remotes:
		aMachine = fetchRemoteInfo(remote[1], remote[0])
		for team in aMachine.keys():
			if team in activities:
				activities[team] = activities[team] + aMachine[team]
			else:
				activities[team] = aMachine[team]

	print activities

	# Write activity.jsonp
	fp = open('activity.jsonp', 'w')
	fp.write('activities=')
	json.dump(activities, fp)
	fp.close()


