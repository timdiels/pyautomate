# Copyright 2011 Tim Diels <limyreth@gmail.com>
#
# This file is part of pyautomate.
# 
# pyautomate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyautomate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pyautomate.  If not, see <http://www.gnu.org/licenses/>.

'''
Provides print functions which print depending on the verboseness set

Provided print functions are of format print n [e], e.g. print1e. n is the
verbosity, e suffix means exact verbosity match, no e means greater or equal.

'''

def init(verbosity):
    noop = lambda *args, **kwargs: None

    global print1
    print1 = print if verbosity >= 1 else noop

    global print1e
    print1e = print if verbosity == 1 else noop

    global print2
    print2 = print if verbosity >= 2 else noop

    global print2e
    print2e = print if verbosity == 2 else noop

    # for debug
    global printd
    printd = print if verbosity >= 3 else noop

    global level
    level = verbosity

