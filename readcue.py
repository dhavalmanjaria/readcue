#!/usr/bin/python

##   Readcue.py
##	 
##	 This script reads the cue file from a folder, reads the name of the
##   FLAC file from that and separates it into it's individial songs.
##
##	 <OWNER> = Dhaval Anjaria
##	 <YEAR> = 2014
##
##	 In the original BSD license, the occurrence of "copyright holder"
##	 in the 3rd clause read "ORGANIZATION", placeholder for
##	 "University of California". In the original BSD license, both
##	 occurrences of the phrase "COPYRIGHT HOLDERS AND CONTRIBUTORS" in
##	 the disclaimer read "REGENTS AND CONTRIBUTORS".
##
##	 Here is the license template:
##
##	 Copyright (c) 2014, Dhaval Anjaria
##	 All rights reserved.
##
##	 Redistribution and use in source and binary forms, with or
##	 without modification, are permitted provided that the following
##	 conditions are met:
##
##	 1. Redistributions of source code must retain the above copyright
##	 notice, this list of conditions and the following disclaimer.
##
##	 2. Redistributions in binary form must reproduce the above
##	 copyright notice, this list of conditions and the following
##	 disclaimer in the documentation and/or other materials provided
##	 with the distribution.
##
##	 3. Neither the name of the copyright holder nor the names of its
##	 contributors may be used to endorse or promote products derived
##	 from this software without specific prior written permission.
##
##	 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
##	 CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
##	 INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
##	 MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##	 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
##	 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
##	 SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
##	 LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
##	 USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
##	 AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
##	 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
##	 ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
##	 POSSIBILITY OF SUCH DAMAGE.
##
##


import os, subprocess

# This is the initial definition of metadata_dict. We initialize it
# here so that we can reinitialize it later.

metadata_dict_init = {"title":'',"index":0,"offset":[], "duration":'',\
	"start_offset":'', "performer":''} 

metadata_dict = metadata_dict_init

metadata_list = []

line = '-' # initialize it to non empty character

album_title = ''
album_file = ''

# Get name of cuefile

if (len(os.sys.argv) < 4):
	print "Usage: readcue --alac [y|n] <cuefile>"
	os.sys.exit(1)

f = open(os.sys.argv[3], "r")
# album_file = os.sys.argv[2]

# Initialize to yes because that was what it was originally intended
# for.
alac_option = 'y'
if (os.sys.argv[2] == 'n'):
	alac_option = 'n'

# We count the number of lines. This makes things a lot simpler
line_count = 0
while (line != ''):
	line = f.readline()
	line_count += 1

f.close()

f = open(os.sys.argv[3], "r")
	
i = 0 # loop count, starting at line 8
title = ''
field_count = 0

################
# Begin loop
################
while (i < line_count - 1):
	# loop till we get to the data and extract the album data
	line = f.readline()
	row = line.split()

	while (i < 6):	
		line = f.readline()
		row = line.split()
		if (row[0] == "TITLE"):
			album_title = ' '.join(row[1:])
			album_title = album_title.replace("\"","")
		if (row[0] == "FILE"):
			album_file = ' '.join(row[1:-1])
			album_file = album_file.replace("\"","")
		i += 1


	# The issue here is that the file is not uniform. What we have is
	# the first word of each line which is the property.
	
	# This line will be common between all

	# TRACK gives us track no.
	# INDEX gives us the offset
	# TITLE gives us the title
	# PERFORMER gives us the artiste
	# field_count will give us the count of how many fields we have.
	# Once we have enough, we append to the metadata_list

	line = line.strip() # remove leading and trailing whitespaces
	row = line.split()

	if (i > 24 and i < 28):
		print str(i) +  line

	if (row[0] == "TRACK"):	
		metadata_dict["index"] = row[1]
		field_count += 1
	
	if (row[0] == "TITLE"):
		title = " ".join(row[1:])
		title = title.replace("\"","")
		metadata_dict["title"] = title
		field_count += 1

	if (row[0] == "INDEX" and row[1] == "01"):
		if (i == 10):
			print 'Reading index of Overture'
			print row[2]
		metadata_dict["offset"].append(row[2])
		field_count += 1

	if (row[0] == "PERFORMER"):
		metadata_dict["performer"] = ' '.join(row[1:])
		field_count += 1

	if (field_count == 4):
		# push to stack
		metadata_list.append(metadata_dict)
		# Reinitialize metadata_dict
		metadata_dict = {"title":'',"index":0,"offset":[], "duration":'',\
		"start_offset":'', "performer":''} 
		field_count = 0
	
	i += 1


####################
# End loop
####################

#### IMPORTANT: CLOSING THE FILE
f.close()

# Now for the extraction and conversion
# First we fix the offsets.
# We add the offset of song after the song we are currently on

###############
# Begin Loop
###############
for x in range(len(metadata_list) -1):
	end_offset = metadata_list[x+1]["offset"][0]
	metadata_list[x]["offset"].append(end_offset)
	end_offset = None
###############
# End Loop
###############


# The end offset of the last song is None
metadata_list[len(metadata_list) - 1]["offset"].append('')

# Before we build the ffmpeg command, we need to fix the offsets and
# set it to ffmpeg's format

# We have to calculate a duration...

for x in metadata_list:
	start_time = x["offset"][0].split(':')
	end_time = x["offset"][1].split(':')

	start_time_seconds = int(start_time[0]) * 60 +\
	int(start_time[1]) + (float(start_time[2]) / 100)

	if(end_time[0] != ''):
		end_time_seconds = int(end_time[0]) * 60 + 	int(end_time[1]) + (float(end_time[2]) / 100)

	duration = end_time_seconds - start_time_seconds

	# Upload the fixed offsets in the format start time and duration
	x["start_offset"] = start_time_seconds
	x["duration"] = duration

######################
## DEBUGGING PURPOSES
######################
#os.sys.exit(1)

# Now we make the ffmpeg command

# For the purposes of this file, we set the artist variable and album for
# every song ourself 

# for x in metadata_list:
# 	title = x["title"]
# 	performer = x["performer"]
# 	trackno = x["index"]
# 	start = x["offset"][0]
# 	end = x["offset"][1]
# 
# 	command = "ffmpeg -ss " + str(x["start_offset"]) + ""+\
# 	" -i "+album+" -ac 2 -ar 44100 -b:a 320k -acodec alac "
# 	
# 	command += " -metadata title=\""+ title +\
# 	"\" -metadata track=\""+trackno+"\" -metadata album=\""+album+\
# 	"\" -metadata author="+performer+""  
# 
# 	# If we're at the last song, exclude this option
# 	if (end != ''):
# 		command += " -t " + str(x["duration"])
# 
# 	command += " \"" + title + ".m4a\""
# 
# 
# 	print command
# 	print '\n'
# 
# 	# And now, for the final act!
# 	subprocess.call(command.split())
# 
# 	# Note: We don't use subprocess because the quotes in the command
# 	# cause problems and the command string becomes somewhat
# 	# ridiculous in the metadata section. So we use this.
# 
# 	#os.system(command)

# We're going to try to create a command that subprocess can use. Why?
# I don't know.

for x in metadata_list:
	command = []

 	title = x["title"]
 	performer = x["performer"].replace("\"","")
 	trackno = x["index"]
 	start = x["offset"][0]
 	end = x["offset"][1]

	# command name
	command.append("ffmpeg") 

	#### Initial Parameter section ####

	# Starting offset for a song
	command.append("-ss")
	command.append(str(x["start_offset"]))
	
	# Input file
	command.append("-i")
	command.append(album_file)

	# Channels
	command.append("-ac")
	command.append("2")

	# Frequency
	command.append("-ar")
	command.append("44100")

	# Bitrate
	command.append("-b:a")
	command.append("320k")

	# Codec

	if (alac_option == 'y'):
		command.append("-acodec")
		command.append("alac")
	else:
		command.append("-acodec")
		command.append("flac")

	#### Metadata Section ####
	
	# Track No.
	command.append("-metadata")
	command.append("track=\"" + trackno + "\"")

	# Album name
	command.append("-metadata")
	command.append("album="+album_title)

	# Artist
	command.append("-metadata")
	command.append("artist="+performer)

	# Title
	command.append("-metadata")
	command.append("title="+title)

	#### Output song name section ####

	if (end != ''):
		command.append("-t")
		command.append(str(x["duration"]))

	if (alac_option == 'y'):
		title += ".m4a"
	else:
		title += ".flac"

	command.append(title)

	print command
	#print '\n\n'
	subprocess.call(command)
	
os.sys.exit(1)


