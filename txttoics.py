import random
from datetime import datetime

def trim(input):
	while input.find("\t\t") + 1 or input.find("  ") + 1:
		input = input.replace("\t\t","\t")
		input = input.replace("  "," ")
	return input

def whichmonth(input):
	months = {
		"Jan" : 1,"Feb" : 2,"Mar" : 3,"Apr" : 4,"May" : 5,"Jun" : 6,
		"Jul" : 7,"Aug" : 8,"Sep" : 9,"Oct" : 10,"Nov" : 11,"Dec" : 12}
	return months.get(input[:3])

def cleanstring(input):
	output = ""
	for x in input:
		if 47 < ord(x) < 58:
			output += x
	return output

transition = False

def isdate(input,year=2021,hour=12,minute=0,second=0):
	a = input.split(" ")
	global transition
	for x in range(len(a) - 1):
		month = whichmonth(a[x])
		b = cleanstring(a[x+1])
		day = int(b[:2]) if b != "" else None
		if(month and day):
			transition = True
			return([year,month,day,hour,minute,second])
	transition = False
	return input

def parsesyllabus(input,hour=12,minute=0,year=2021):
	with open(input + ".txt","r") as f:
		lines = []
		buffer = []
		recording = False
		for x in f:
			if not recording:
				if 0 < x.find("chedule") < 50:
					recording = True
			elif 1 < len(x):
				for y in trim(x).split("\t"):
					buffer.append(isdate(y,year,hour,minute))
					if transition:
						lines.append(buffer)
						buffer = [buffer[-1]]
		lines.append(buffer)
		lines.pop(0)
	return lines

def daysinmonth(month,year=1):
	if month == 4 or month == 6 or month == 9 or month == 11:
		return 30
	elif month == 2:
		return 28 if year % 4 else 29
	else:
		return 31

def safestring(input,digits=2):
	a = len(str(input))
	a = str(input)
	for x in range(digits - len(a)):
		a = "0" + a
	return a

def wrapdate(year,month,day,hour,minute,second):
	input = [year,month,day,hour,minute,second]
	output = ""
	for x in range(len(input)):
		if not x:
			output += safestring(input[x],4)
		else:
			output += safestring(input[x])
		if x == 2:
			output += "T"
	return output

def moveforward(start,elapsed):
	year = int(start[:4])
	month = int(start[4:6])
	day = int(start[6:8])
	hour = int(start[9:11])
	minute = int(start[11:13])
	second = int(start[13:15])
	second += elapsed
	if second >= 60:
		minute += second // 60
		second %= 60
		if minute >= 60:
			hour += minute // 60
			minute %= 60
			if(hour >= 24):
				day += hour // 24
				hour %= 24
				a = daysinmonth(month)
				if(day >= a):
					month += day // a
					day %= a
					if(month >= 12):
						year += month // 12
						month %= 12
	return wrapdate(year,month,day,hour,minute,second)

def generateuid():
	uid = ""
	for x in range(8):
		uid += hex(random.randrange(4096,65535))[2:].upper()
		if 0 < x < 5:
			uid += "-"
	return uid

def timezones(timezone,aspect):
	zones = {6 : ["America\Chicago","CDT","-0600","-0500"]}
	return zones.get(timezone)[aspect]

def classtimes(course,aspect):
	classes = {
		"compsci" : [3000,13,30,2021],"bio" : [3000,14,30,2021],
		"econ" : [4800,12,30,2021],"ir" : [4800,14,0,2021]}
	return classes.get(course)[aspect]

def calendarheader(output,color="0E61B9",zone=6):
	contents = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:"
	contents += output
	contents += "\nX-APPLE-CALENDAR-COLOR:#" + color
	contents += "\nX-WR-TIMEZONE:" + timezones(zone,0)
	contents +="\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:" + timezones(zone,0)
	contents += "\nBEGIN:DAYLIGHT\nTZOFFSETFROM:" + timezones(zone,2)
	contents += "\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\nDTSTART:20070311T020000\nTZNAME:"
	contents += timezones(zone,1)
	contents += "\nTZOFFSETTO:" + timezones(zone,3)
	contents += "\nEND:DAYLIGHT\nBEGIN:STANDARD\nTZOFFSETFROM:" + timezones(zone,3)
	contents += "\nRRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\nDTSTART:20071104T020000\nTZNAME"
	contents += timezones(zone,1)
	contents += "\nTZOFFSETTO:" + timezones(zone,2)
	contents += "\nEND:STANDARD\nEND:VTIMEZONE\n"
	return contents

def writecalendar(input,output=-1,zone=6,description="",url="",color=-1):
	if output == -1:
		output = input
	if color == -1:
		color = hex(random.randrange(1048576,16777215))[2:].upper()
	alarmuid = generateuid()
	duration = classtimes(input,0)
	a = datetime.now()
	datecreated = None
	datestamp = None
	lastmodified = wrapdate(a.year,a.month,a.day,a.hour,a.minute,a.second)
	contents = calendarheader(output,color,zone)
	for x in parsesyllabus(input,classtimes(input,1),classtimes(input,2),classtimes(input,3)):
		datecreated = moveforward(lastmodified,1)
		datestamp = moveforward(datecreated,1)
		lastmodified = moveforward(datestamp,1)
		uid = generateuid()
		datestart = wrapdate(x[0][0],x[0][1],x[0][2],x[0][3],x[0][4],x[0][5])
		dateend = moveforward(datestart,duration)
		x[0] = ""
		x[-1] = ""
		summary = "".join(x).replace("\n"," ")
		contents += "BEGIN:VEVENT\nTRANSP:OPAQUE\nDTEND;TZID=" + timezones(zone,0)
		contents += ":" + dateend
		contents += "\nUID:" + uid
		contents += "\nDTSTAMP:" + datestamp
		contents += "Z\nDESCRIPTION:" + description
		contents += "\nURL;VALUE=URI:" + url
		contents += "\nSEQUENCE:1\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:"
		contents += summary
		contents += "\nLAST-MODIFIED:" + lastmodified
		contents += "Z\nCREATED:" + datecreated
		contents += "Z\nDTSTART;TZID=" + timezones(zone,0)
		contents += ":" + datestart
		contents += "\nBEGIN:VALARM\nX-WR-ALARMUID:" + alarmuid
		contents += "\nUID:" + alarmuid
		contents += "\nTRIGGER:-PT10M\nX-APPLE-DEFAULT-ALARM:TRUE\nATTACH;VALUE=URI:Basso\nACTION:AUDIO\nEND:VALARM\nEND:VEVENT\n"
	contents += "END:VCALENDAR"
	with open(output + ".ics","w") as f:
		f.write(contents)

writecalendar("bio")
writecalendar("econ")
writecalendar("ir")