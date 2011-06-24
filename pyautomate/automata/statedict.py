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

from .statename import StateNames
from collections import defaultdict

class _DummyState(object):

    def __init__(self, name):
        self._name = name

    def transition(self, symbol, current_states):
        return StateNames((self._name,)) if self._name else frozenset()

class StateDict(defaultdict):

    def __init__(self):
        defaultdict.__init__(self)

    def __missing__(self, state_name):
        return _DummyState(state_name)

