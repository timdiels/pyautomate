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
from .state import State

class _GuardDict(defaultdict):

    def __init__(self):
        defaultdict.__init__(self)

    def __missing__(self, key):
        return frozenset()

 
class GuardedState(State):

    def __init__(self, raw):
        State.__init__(self, raw)
        self._guards = _GuardDict()
        for raw_transition in raw['transitions']:
            if 'guard' not in raw_transition:
                continue

            required_states = StateNames(raw_transition['guard']['state contains'])
            self._guards[raw_transition['action']] = required_states

    def transition(self, symbol, current_states):
        if self._guards[symbol].issubset(current_states):
            return State.transition(self, symbol, current_states)
        else:
            return frozenset()
