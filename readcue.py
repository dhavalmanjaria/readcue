#!/usr/bin/env python3

#############################################################################
## readcue.py
## This file is part of readcue
## Copyright (C) 2014 Dhaval Anjaria
## Copyright (C) 2014 Darcy Bras da Silva
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/
#############################################################################
## this script reads the cue file from a folder, reads the name of the
## flac file and from that separates it into it's individual songs
#############################################################################

import argparse

def ReadTrack(filepath):
        """
        Lazy function (generator) to read a list of tracks
        from a given file which contains each track information
        Reads one Track at the time
        """
        ## some tracks don't have 00 and 01 index.
        ## keep track of the previous index to use as start
        previous = None
        ## keep track if we are in a track collecting metadata ?
        inTrack =  False
        ## which part of the collection are we ?
        stage = None
        ## track metadata
        album = ""
        title = ""
        performer = ""
        track_no = 0
        s_index = 0
        e_index = 0


        p_album = ""
        p_title = ""
        p_performer = ""
        p_track_no = 0
        p_s_index = 0
        p_e_index = 0

        loopCount = 0

#        with open(filepath, 'r') as f:
        if filepath != None:
                f = filepath
                for line in f:
                        loopCount += 1
                        ## check if we are currently collecting
                        if inTrack == False:
                                if stage == None:
                                         ## first read ,get album
                                         if 'TITLE' in line:
                                                s = line.find('"')+1
                                                e = line.rfind('"')
                                                album = line[s:e]
                                                continue
                                         # Q: If stage specifies which stage of track metadata we're in
                                         # Why are we setting the stage when we find the album
                                         # and not when we see 'TRACK'
                                ## we are not collecting
                                ## see if we need to be

                                ## Copies the current variables into previous variables regardless of whether or not its
                                ## there. Once it reads the next set of variables, it yeilds them in the INDEX section

                                p_track_no = track_no
                                p_album = album
                                p_title = title
                                p_performer = performer
                                p_s_index = p_e_index
                                p_e_index = s_index
                                if 'TRACK' in line:
#                                        if 0 != track_no:

                                        stage = 0
                                        inTrack = True
                                        ## get track number
                                        #track_no = line.split()[1]
                                        # We can get by with using find and rfind since for a filed that 
                                        # contains 'TRACK' the track number will always be between 2 
                                        # spaces
                                        s = line.find('K')+2
                                        e = line.rfind(' ')
                                        track_no = line[s:e]

                                        continue

                        ## we are currently collecting
                        if 'TITLE' in line:
                                s = line.find('"')+1
                                e = line.rfind('"')
                                title = line[s:e]
                                stage = stage + 1
                                continue
                        if 'PERFORMER' in line and stage != None:
                                s = line.find('"')+1
                                e = line.rfind('"')
                                performer = line[s:e]
                                stage = stage + 1
                                continue
                                # The file has two 'PERFORMER' fields.
                                # If they are different, which could be the case if you have 
                                # a compilation album or if a track has more than one artist associated
                                # with it, then we need to accomodate for that. But ffmpeg doesn't 
                                # support that.
                        if 'INDEX' in line:
                                if '01 ' in line:
                                        ## we don't have 2 indexes
                                        t = line.find('01 ')+3
                                        e_index = line[t:].strip()
                                        inTrack = False
#                                        if previous == None:
#                                                s_index = '00:00:00'
#                                                previous = e_index
#                                        else:
#                                                s_index = previous
#                                                previous = e_index
                                        
                                        p_e_index = e_index # Regardless
                                        
                                       
                                        ## 
                                        ## This yields the previous vars but since it only yeilds if p_track_no is not
                                        ## 0, it does it after the first track is fixed. This method works, however the
                                        ## last track is not yeilded. This code requires a bunch of cleanup.

                                        if 0 != p_track_no: # Meaning p_vars are set
                                                yield p_album,p_track_no,p_title,p_performer,p_s_index,p_e_index
                                        
                                        if '01' in track_no:
                                                p_s_index = '00:00:00'
                                                continue
                                        else:
                                                p_s_index = p_e_index
                                                continue
                                        
                                ## we have two indexes
#                                elif '00 ' in line and 3 == stage + 1:
#                                        ## we have 2 indexes
#                                        t = line.find('00 ')+3
#                                        s_index = line[t:].strip()
#                                        stage = stage + 1
#                                        ## read second index
#                                        line = f.readline()
#                                        if '01 ' in line and 4 == stage + 1:
#                                                t = line.find('01 ')+3
#                                                e_index = line[t:].strip()
#                                                stage = 0
#                                                inTrack = False
#                                                yield album,track_no,title,performer,s_index,e_index


                # If we still have data left in the current track variables
                if '' != album and '' != p_album:
                        yield album,track_no,title,performer,e_index,None

def create_argparser():
        """
        This function creates and configures
        the application/script argument parser
        returning it ready for usage
        """
        #  configure the argument parser
        parser = argparse.ArgumentParser(
                description=
                """
                Converts the tracks listed in a cue file
                to individual ['alac','flac'] files
                if no arguments are provided it will attempt to
                use 'readcue.txt' file with codec configured to alac
                """
        )

        parser.add_argument('-f', '--file',
                            help="takes a cue file as extra argument")

        # don't allow verbose with quiet at the same time

        group_vq = parser.add_mutually_exclusive_group()

        group_vq.add_argument('-v','--verbose', action='store_true',
                              help='increase output verbosity')

        group_vq.add_argument('-q', '--quiet', action='store_true',
                              help='no output messages will be displayed')

        parser.add_argument('-c', '--codec',
                            choices=['alac','flac'],
                            help='enables conversion to alac or flac file format')

        return parser

if __name__ == '__main__':
        parser = create_argparser()
        # parse the arguments
        args = parser.parse_args()

        cue_fpath = 'readcue.txt'
        if args.file != None:
                cue_fpath = args.file

        ## open the file for ReadTrack
        try:
                cue_file = open(cue_fpath, 'r')
        except FileNotFoundError as ferr:
                print("could not find '{}'\n"
                      "please use -f filename ."
                      "check -h or --help for usage".
                      format(cue_fpath))
                exit(1)

        for _album,_track_no,_title,_performer,_idx,__idx in ReadTrack(cue_file):
                print("Album   : \"{}\"\n"
                      "Track   : \"{}\"\n"
                      "Title   : \"{}\"\n"
                      "Artist  : \"{}\"\n"
                      "Duration: [\"{}\" , \"{}\"]\n"
                      .format(_album,_track_no,_title,_performer,_idx,__idx))


