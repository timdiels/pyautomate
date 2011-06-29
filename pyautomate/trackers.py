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


from pyautomate.application import application

class Trackers(object):

    def __init__(self):
        self._trackers = {}

    def __setitem__(self, key, value_getter):
        self._trackers[key] = _Tracker(key, value_getter)

    def __getitem__(self, key):
        return self._trackers[key]

class _Tracker(object): 
    def __init__(self, key, value_getter):
        self.__key = key
        self._get_value = value_getter

    @property
    def _key(self):
        return '#tracker: ' + self.__key

    def make_current(self):
        application.persisted_data[self._key] = self._get_value()

    @property
    def has_changed(self):
        return has_changed(self._key, self._get_value()) 

trackers = Trackers()
del Trackers

def has_changed(key, value):
    return key not in application.persisted_data or \
        application.persisted_data[key] != value
