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

import os.path
import pyautomate.verbosity
import sys
import yaml

from argparse import ArgumentParser
from importlib import import_module
from collections import defaultdict

from .data import Data

class Application(object):

    def __init__(self):
        self.version = '0.1-post'

    def run(self):
        options = self._parse_args()
        self._init_verbosity(options.verbosity)
        self._load_files(options.auto_path)
        dfa = self._make_dfa(options.desired_state)
        self._execute_path(dfa, options.exact)

    @property
    def persisted_data(self):
        '''Keys starting with '#' are reserved and should not be used'''
        return self._data['last_state']

    def _init_verbosity(self, level):
        pyautomate.verbosity.init(level)

    def _parse_args(self):
        self.parser = ArgumentParser(description='Automation tool', prog='auto',
                    epilog='For more information see TODO github link readme')
        self.parser.add_argument('desired_state', metavar='S', nargs='+', 
                        help='a state to reach')
        self.parser.add_argument('--file', '-f', dest='auto_path', default='auto.py',
                        help='the pyautomate config file (default: ./auto.py)')
        self.parser.add_argument('--exact', '-e', default=False, action='store_true',
                        help='when specified desired state must be matched ' + \
                        'exactly (default: partial match)')
        self.parser.add_argument('--verbosity', '-v', metavar='V', default=1, type=int,
                        help='verbosity of output. 0 for no output, 1 for ' + \
                        'listing actions, 2 for listing state switches and ' + \
                        'actions (default: 1)')
        self.parser.add_argument('--version', action='version', 
                        version='%(prog)s ' + self.version)
        return self.parser.parse_args()

    def _load_files(self, auto_path):
        auto_path = os.path.abspath(auto_path)
        auto_dir, auto_file = os.path.split(auto_path)
        if not os.path.exists(auto_path):
            self.parser.error('Could not find auto file at: %s' % auto_path)
        os.chdir(auto_dir)

        self._data = Data()
        self._config = self._load_auto_file(auto_dir, auto_file)

    def _load_auto_file(self, auto_dir, auto_file):
        sys.path.insert(0, auto_dir)  # allow importing

        auto_module_name = os.path.splitext(auto_file)[0]
        try:
            config = import_module(auto_module_name)
        except ImportError as ex:
            self.parser.error('Failed to import auto file: %s' % ex)

        weights = defaultdict(lambda: 1000)
        if hasattr(config, 'weights'):
            weights.update(config.weights)
        config.weights = weights

        return config

    def _make_dfa(self, desired_state):
        from pyautomate.automata import (
            GuardedState, StateDict, NFA, NFAAsDFA, UnknownStatesException
        )

        raw_states = yaml.load(self._config.states)
        if not raw_states:
            raw_states = {}

        states = StateDict()
        for raw_state in raw_states:
            state = GuardedState(raw_state)
            states[state.name] = state

        start_state = self._config.get_initial_state()
        self._data.commit()
        if isinstance(start_state, str):
            start_state = (start_state,)
        elif not isinstance(start_state, tuple):
            self.parser.error('get_initial_state must return a str or a tuple of ' + \
                         'states, got: {0}'.format(start_state))

        try:
            nfa = NFA(states=states,
                      raw_start_states=start_state,
                      raw_end_states=desired_state)
        except UnknownStatesException as ex:
            self.parser.error('Unknown state(s) in desired state: {0}'.format(
                            ', '.join(ex.states)))
        return NFAAsDFA(nfa)

    def _execute_path(self, dfa, exact):
        from pyautomate.automata import EndUnreachableException
        from pyautomate.verbosity import (
            print1, print1e, print2, print2e, level as verbosity_level
        )

        try:
            for from_, action, to in dfa.get_shortest_path(exact, self._config.weights):

                print1e(action)

                if verbosity_level == 2:

                    for i, right in enumerate(to):

                        if i==0:
                            fill = '-'
                            right = '> ' + right
                            center = action
                        else:
                            fill = ' '
                            center = ''
                        center_len = 79 - len(right)

                        print('{0:{1}^{3}}{2}'.format(center, fill, right, center_len))

                    print()

                try:
                    eval(action, vars(self._config))
                    self._data.commit()
                except:
                    print('Failed to execute action:', action, file=sys.stderr)
                    raise

        except EndUnreachableException:
            print('Desired state (%s) is unreachable from (%s)' % (
                ', '.join(dfa.end_state), ', '.join(dfa.start_state)
            ))
            self.parser.exit(1)
        finally:
            self._data.save()


application = Application()
del Application

