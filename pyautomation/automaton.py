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

class NFA(object):

    def __init__(self, transitions, start_states, end_states):
        # process raw transitions to something more usable
        self._transitions = {}
        for state, t in transitions.items():
            self._transitions[state[0]] = dict(((symbol, frozenset(result)) 
                                             for symbol, result 
                                             in t.items()))
        print('self.transitions')
        print(self._transitions)

        self.alphabet = set(chain(*(t.keys() for t in self._transitions.values())))
        print('self.alphabet')
        print(self.alphabet)

        self.start_states = frozenset(start_states)
        self.end_states = frozenset(end_states)

    def transition(self, states, symbol):
        new_states = set()

        for state in states:
            if state in  self._transitions and symbol in self._transitions[state]:
                new_states |= self._transitions[state][symbol]
            else:
                new_states.add(state)

        return frozenset(new_states)

    def get_neighbours(self, states):
        '''returns iterable of (symbol, neighbour) of each neighbour of states'''
        for symbol in self.alphabet:
            neighbour = self.transition(states, symbol)
            if neighbour != states:
                yield (symbol, neighbour) 

class NFAAsDFA(object):
    def __init__(self, nfa):
        self._nfa = nfa

    def transition(self, state, symbol):
        return self._nfa.transition(state, symbol)

    def get_neighbours(self, state):
        return self._nfa.get_neighbours(state)

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
                print('==' * 10)
                print(state)
                print(' v' * 10)
                print('%s * %s' % (symbol, weights[neighbour]))
                print(' v' * 10)
                print(neighbour)
                path_distance = final_distances[state] + weights[neighbour]
                if neighbour in final_distances:
                    if path_distance < final_distances[neighbour]:
                        raise ValueError("Dijkstra: found better path to already-final vertex")
                elif neighbour not in estimated_distances or path_distance < estimated_distances[neighbour]:
                    estimated_distances[neighbour] = path_distance
                    predecessors[neighbour] = (state, symbol)

        path = []
        end = self.end_state
        while end != self.start_state:
            (end, symbol) = predecessors[end]
            path.append(symbol)
        return reversed(path)

