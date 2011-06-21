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

from collections import defaultdict
from .statename import StateNames

class _TransitionDict(defaultdict):

    def __init__(self, default_factory):
        defaultdict.__init__(self, default_factory)

    def __missing__(self, key):
        return self.default_factory()

class State(object):

    def __init__(self, state_name, transitions):
        self._transitions = _TransitionDict(lambda: frozenset(state_name))
        for symbol, target_states in transitions.items():
            self._transitions[symbol] = StateNames(target_states)

    def transition(self, symbol):
        '''
        returns the state names to which the NFA state transitions when given symbol
        '''
        return self._transitions[symbol]

    @property
    def state_names(self):
        '''returns names of target states and itself'''
        return frozenset.union(frozenset(), *self._transitions.values())

    @property
    def alphabet(self):
        '''returns symbols known to this state'''
        return frozenset(self._transitions.keys())
 
