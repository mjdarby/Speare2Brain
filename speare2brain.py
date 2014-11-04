#!/usr/bin/python3

########################################################################
#
#  Speare2Brain, the Shakespeare -> Brainfuck transpiler
#
#  Copyright (C) 2014 Matthew Darby
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or (at
#  your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
#  USA.
#
########################################################################
import sys, os
from subprocess import call

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./speare2brain.py input.spl > output.bf")
        sys.exit(2)
    filename = sys.argv[1]
    path_to_this = os.path.realpath(__file__)
    basepath = os.path.dirname(path_to_this)
    path_to_spl2nspl = basepath + '/spl2nspl'
    command = "{1} < {0} > {0}.nspl".format(filename, path_to_spl2nspl)
    call(command, shell = True)
    path_to_nspl2bf = basepath + '/nspl2bf.py'
    command = "{1} {0}.nspl".format(filename, path_to_nspl2bf)
    call(command, shell = True)
