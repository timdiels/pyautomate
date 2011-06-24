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

from pyautomate.priodict import priorityDictionary
from pyautomate.verbosity import printd

from . import UnknownStatesException, EndUnreachableException
from .statename import StateNames

class NFA(object):

    def __init__(self, states, raw_start_states, raw_end_states):
        self._states = states

        self.alphabet = frozenset.union(frozenset(), *[state.symbols 
                                        for state in self._states.values()])

        self.start_states = StateNames(raw_start_states)
        self.end_states = StateNames(raw_end_states)

        unknown_states = self.end_states - self.state_names
        if unknown_states:
            raise UnknownStatesException(unknown_states)

    @property
    def state_names(self):
        return frozenset.union(frozenset(), *[state.state_names 
                               for state in self._states.values()])

    def transition(self, state_name, symbol, current_states):
        '''
        returns the state names to which the NFA transitions when given symbol
        at state
        '''
        return self._states[state_name].transition(symbol, current_states)

class NFAAsDFA(object):

    # Note: nfa state variables are named explicitly (e.g. nfa_state), dfa
    # states aren't (e.g. state)

    def __init__(self, nfa):
        self._nfa = nfa

    def transition(self, state, symbol):
        new_states = set()

        for nfa_state in state | frozenset(('',)):  # '' == the nameless state
            new_states |= self._nfa.transition(nfa_state, symbol, state)

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

    def get_shortest_path(self, exact, weights):
        '''returns shortest path from start to end as list of actions
        exact: whether the end state should be matched partially or exactly
        weights: {symbol : weight}
        '''
        printd('exact', exact)
        if exact:
            reached_destination = lambda: state == self.end_state
        else:
            reached_destination = lambda: self.end_state.issubset(state)

        if self.start_state == self.end_state:
            return ()

        # Adapted from:
        # David Eppstein, UC Irvine, 4 April 2002
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228

        final_distances = {}  # dictionary of final distances
        predecessors = {}  # dictionary of predecessors
        estimated_distances = priorityDictionary()  # est.dist. of non-final vert.
        estimated_distances[self.start_state] = 0

        end = None
        printd('contacting neighbours for path to', self.end_state)
        for state in estimated_distances:
            printd()
            printd(state)
            final_distances[state] = estimated_distances[state]
            if reached_destination(): 
                if exact: end = self.end_state
                else: end = state
                break

            for symbol, neighbour in self.get_neighbours(state):
                if neighbour == state:
                    continue
                printd('{0}: {1}'.format(symbol, neighbour))
                path_distance = final_distances[state] + weights[neighbour]
                if neighbour in final_distances:
                    if path_distance < final_distances[neighbour]:
                        raise ValueError("Dijkstra: found better path to already-final vertex")
                elif neighbour not in estimated_distances or path_distance < estimated_distances[neighbour]:
                    estimated_distances[neighbour] = path_distance
                    predecessors[neighbour] = (state, symbol)

        path = []
        if not end:
            # this means we found no path to our destination
            raise EndUnreachableException()

        while end != self.start_state:
            to = end
            (end, symbol) = predecessors[end]
            from_ = end
            path.append((from_, symbol, to))

        return reversed(path)

