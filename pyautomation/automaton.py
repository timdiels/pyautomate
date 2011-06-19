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

from itertools import chain
from pyautomation.priodict import priorityDictionary

class EndUnreachableException(Exception): pass

class UnknownStateException(Exception):
    def __init__(self, state):
        Exception.__init__(self)
        self.state = state

class NFA(object):

    def __init__(self, transitions, start_states, end_states):
        # process raw transitions to something more usable
        self._transitions = {}
        for state, t in transitions.items():
            state = state[0].replace('_', ' ')
            self._transitions[state] = dict()
            for symbol, target_states in t.items():
                self._transitions[state][symbol] = frozenset(
                    s.replace('_', ' ') for s in target_states)

        _states = self._states
        for state in end_states:
            if state not in _states:
                raise UnknownStateException(state)

        self.alphabet = set(chain(*(t.keys() for t in self._transitions.values())))

        self.start_states = frozenset(start_states)
        self.end_states = frozenset(end_states)

    @property
    def _states(self):
        states = set()
        for state, t in self._transitions.items():
            states.add(state)
            for target_states in t.values():
                states |= target_states
        return states

    def transition(self, state, symbol):
        '''
        returns the states to which the NFA transitions when given symbol at 
        state

        state: a single state
        '''
        if state in  self._transitions and symbol in self._transitions[state]:
            return self._transitions[state][symbol]
        else:
            # Note: this is not normal NFA behaviour, but it happened to be
            # much handier than 'die', which would have been return empty set
            return frozenset((state,))
        
class NFAAsDFA(object):
    def __init__(self, nfa):
        self._nfa = nfa

    def transition(self, state, symbol):
        new_states = set()

        for nfa_state in state:
            new_states |= self._nfa.transition(nfa_state, symbol)

        return frozenset(new_states)

    def get_neighbours(self, state):
        '''returns iterable of (symbol, neighbour) of each neighbour of state
        
        Neighbours are all incident states, this includes state itself in case
        of loops.'''
        for symbol in self._nfa.alphabet:
            neighbour = self.transition(state, symbol)
            yield (symbol, neighbour) 

    @property
    def start_state(self):
        return self._nfa.start_states

    @property
    def end_state(self):
        return self._nfa.end_states

    def get_shortest_path(self, weights):
        '''returns shortest path from start to end as list of actions
        weights: {symbol : weight}
        '''
        if self.start_state == self.end_state:
            return ()

        # Adapted from:
        # David Eppstein, UC Irvine, 4 April 2002
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228

        final_distances = {}  # dictionary of final distances
        predecessors = {}  # dictionary of predecessors
        estimated_distances = priorityDictionary()  # est.dist. of non-final vert.
        estimated_distances[self.start_state] = 0

        for state in estimated_distances:
            final_distances[state] = estimated_distances[state]
            if state == self.end_state: break

            for symbol, neighbour in self.get_neighbours(state):
                if neighbour == state:
                    continue
                path_distance = final_distances[state] + weights[neighbour]
                if neighbour in final_distances:
                    if path_distance < final_distances[neighbour]:
                        raise ValueError("Dijkstra: found better path to already-final vertex")
                elif neighbour not in estimated_distances or path_distance < estimated_distances[neighbour]:
                    estimated_distances[neighbour] = path_distance
                    predecessors[neighbour] = (state, symbol)

        path = []
        end = self.end_state
        if end not in predecessors:
            # this means we never even found a path from start to end
            raise EndUnreachableException()

        while end != self.start_state:
            to = end
            (end, symbol) = predecessors[end]
            from_ = end
            path.append((from_, symbol, to))

        return reversed(path)

