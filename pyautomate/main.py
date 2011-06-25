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

version = '0.1-post'

def make_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Automation tool', prog='auto',
                epilog='For more information see TODO github link readme')
    parser.add_argument('desired_state', metavar='S', nargs='+', 
                    help='a state to reach')
    parser.add_argument('--file', '-f', dest='auto_path', default='auto.py',
                    help='the pyautomate config file (default: ./auto.py)')
    parser.add_argument('--exact', '-e', default=False, action='store_true',
                    help='when specified desired state must be matched ' + \
                    'exactly (default: partial match)')
    parser.add_argument('--verbosity', '-v', metavar='V', default=1, type=int,
                    help='verbosity of output. 0 for no output, 1 for ' + \
                    'listing actions, 2 for listing state switches and ' + \
                    'actions (default: 1)')
    parser.add_argument('--version', action='version', 
                    version='%(prog)s ' + version)
    return parser

def load_auto_file(auto_path):
    from importlib import import_module
    from collections import defaultdict
    import os.path
    import sys

    auto_path = os.path.abspath(auto_path)
    auto_dir, auto_file = os.path.split(auto_path)

    # allow importing
    sys.path.insert(0, auto_dir)

    # set it as working dir as this allows easier auto files
    os.chdir(auto_dir)
    auto_module_name = os.path.splitext(auto_file)[0]
    try:
        config = import_module(auto_module_name)
    except ImportError:
        parser.error('Could not find auto file at: %s' % auto_path)

    weights = defaultdict(lambda: 1000)
    if hasattr(config, 'weights'):
        weights.update(config.weights)
    config.weights = weights

    return config

def make_dfa(config, desired_state):
    from pyautomate.automata import GuardedState, StateDict, NFA, NFAAsDFA, \
        UnknownStatesException
    import yaml

    raw_states = yaml.load(config.states)
    states = StateDict()
    for raw_state in raw_states:
        state = GuardedState(raw_state)
        states[state.name] = state

    start_state = config.get_initial_state()
    if isinstance(start_state, str):
        start_state = (start_state,)
    elif not isinstance(start_state, tuple):
        parser.error('get_initial_state must return a str or a tuple of ' + \
                     'states, got: {0}'.format(start_state))

    try:
        nfa = NFA(states=states,
                  raw_start_states=start_state,
                  raw_end_states=desired_state)
    except UnknownStatesException as ex:
        parser.error('Unknown state(s) in desired state: {0}'.format(
                        ', '.join(ex.states)))
    return NFAAsDFA(nfa)

def execute_path(config, dfa, exact):
    from pyautomate.automata import EndUnreachableException
    import sys

    try:
        for from_, action, to in dfa.get_shortest_path(exact, config.weights):

            print1e(action)

            if options.verbosity == 2:

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
                eval(action, vars(config))
            except:
                print('Failed to execute action:', action, file=sys.stderr)
                raise

    except EndUnreachableException:
        print('Desired state (%s) is unreachable from (%s)' % (
            ', '.join(dfa.end_state), ', '.join(dfa.start_state)
        ))
        parser.exit(1)

parser = make_parser()
options = parser.parse_args()

import pyautomate.verbosity
pyautomate.verbosity.init(options.verbosity)
from pyautomate.verbosity import print1, print1e, print2, print2e

config = load_auto_file(options.auto_path)
dfa = make_dfa(config, options.desired_state)
execute_path(config, dfa, options.exact)

