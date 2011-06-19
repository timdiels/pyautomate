# Copyright 2011 Tim Diels <limyreth@gmail.com>
#
# This file is part of pyautomation.
# 
# pyautomation is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyautomation is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pyautomation.  If not, see <http://www.gnu.org/licenses/>.

'''Provides print functions which print depending on the verboseness set'''

def init(verbosity):
    noop = lambda *args, **kwargs: None
    global print0
    print0 = print if verbosity >= 0 else noop
    global print1 
    print1 = print if verbosity >= 1 else noop
    global print2 
    print2 = print if verbosity >= 2 else noop

