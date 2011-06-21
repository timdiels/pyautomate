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

class EndUnreachableException(Exception): pass

class UnknownStatesException(Exception):
    def __init__(self, states):
        Exception.__init__(self)
        self.states = states

class State(object):

    def __init__(self, transitions):
        self._transitions = dict()
        for symbol, target_states in transitions.items():
            self._transitions[symbol] = StateNames(target_states)

    def transition(self, symbol):
        '''
        returns the state names to which the NFA state transitions when given symbol
        '''
        if symbol in self._transitions:
            return self._transitions[symbol]
        else:
            return frozenset()

    @property
    def state_names(self):
        '''returns names of target states and itself'''
        return frozenset.union(frozenset(), *self._transitions.values())

    @property
    def alphabet(self):
        '''returns symbols known to this state'''
        return frozenset(self._transitions.keys())
        

def StateName(name):
    return name.replace('_', ' ')

def StateNames(names):
    return frozenset(StateName(s) for s in names)

class NFA(object):

    def __init__(self, transitions, start_states, end_states):
        # process raw transitions to something more usable
        self._states = {}
        for state_names, transitions in transitions.items():
            state_name = StateName(state_names[0])
            self._states[state_name] = State(transitions)

        self.alphabet = frozenset.union(frozenset(), *[state.alphabet 
                                        for state in self._states.values()])

        self.start_states = StateNames(start_states)
        self.end_states = StateNames(end_states)

        _state_names = self._state_names
        unknown_states = self.end_states - _state_names
        if unknown_states:
            raise UnknownStatesException(unknown_states)

    @property
    def _state_names(self):
        return frozenset.union(frozenset(), *[state.state_names 
                               for state in self._states.values()])

    def transition(self, state_name, symbol):
        '''
        returns the state names to which the NFA transitions when given symbol
        at state
        '''
        if state_name in self._states:
            target_state_names = self._states[state_name].transition(symbol)
        else:
            target_state_names = None

        # when no transition was specified for symbol, assume to transition
        # to itself (this is not normal behaviour for an NFA, normally it would
        # die, but that would just not be handy, in fact we'd have to fill it
        # up with lots of transitions to prevent exactly that)
        return target_state_names or StateNames((state_name,))

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

