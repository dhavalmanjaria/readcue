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

        cue_file = 'readcue.txt'
        if args.file != None:
                cue_file = args.file
