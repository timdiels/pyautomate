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

from argparse import ArgumentParser
import sys

parser = ArgumentParser(description='Automation tool', prog='auto',
                epilog='For more information see TODO github link readme')
parser.add_argument('desired_state', metavar='S', nargs='+', 
                    help='the state to reach')
parser.add_argument('--file', dest='auto_path', default='auto.py',
                    help='the pyautomate config file (default: ./auto.py)')
options = parser.parse_args(sys.argv)

from importlib import import_module
from collections import defaultdict
import os.path

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

weights = defaultdict(lambda: 10)
if config.weights:
    weights.update(config.weights)
config.weights = weights

options.desired_state

# do something...
from pyautomation.automaton import NFA, NFAAsDFA

nfa = NFA(transitions=config.state_machine,
          start_states=config.get_initial_state(),
          end_states=options.desired_state)
dfa = NFAAsDFA(nfa)

action_path = dfa.get_shortest_path(config.weights)

# execute the actions
for action in action_path:
    print(action + ' ...')
    sys.eval(action)

