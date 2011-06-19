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

from argparse import ArgumentParser

parser = ArgumentParser(description='Automation tool', prog='auto',
                epilog='For more information see TODO github link readme')
parser.add_argument('desired_state', metavar='S', nargs='+', 
                    help='the state to reach')
parser.add_argument('--file', '-f', dest='auto_path', default='auto.py',
                    help='the pyautomate config file (default: ./auto.py)')
parser.add_argument('--verbosity', '-v', default=1, type=int,
                    help='verbosity of output. 0 for no output, 1 for ' + \
                    'listing actions, 2 for listing state switches and ' + \
                    'actions (default: 1)')
options = parser.parse_args()

import verbosity
verbosity.init(options.verbosity)
from verbosity import print1, print1e, print2, print2e

from importlib import import_module
from collections import defaultdict
import os.path
import sys

auto_path = os.path.abspath(options.auto_path)
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

# do something...
from pyautomate.automaton import (
    NFA, NFAAsDFA, EndUnreachableException, UnknownStateException
)

desired_state = [state.replace('_', ' ') for state in options.desired_state]

try:
    nfa = NFA(transitions=config.state_machine,
              start_states=config.get_initial_state(),
              end_states=desired_state)
except UnknownStateException as ex:
    parser.error('Unknown state in desired state: %s' % ex.state)
    print('eeek')

dfa = NFAAsDFA(nfa)

try:

    print2e('Start state:', ', '.join(nfa.start_states))
    print2e()

    for from_, action, to in dfa.get_shortest_path(config.weights):

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
        ', '.join(nfa.end_states), ', '.join(nfa.start_states)
    ))
    parser.exit(1)
