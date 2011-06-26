pyautomate is an automation tool. pyautomate can be used to automate any set
of tasks. pyautomate offers a KISS CLI + auto.py config file interface. Unlike
other tools, you describe a system as a `state machine`_ and specify how to get
from one state to the other. You then use the CLI to specify the state you want
to reach, and pyautomate will get it done. 

To get a good idea of what pyautomate can do for you I suggest you have a quick
scroll through `the usage section`__.

__ `usage`_

If you would like to use it as a library, let me know
(limyreth@gmail.com) and I'll provide you with a documented API.

.. contents::

Install/run instructions
========================
pyautomate is distributed using 0install, and thus requires no installation,
you can just run it.

The 0install feed (with instructions):
http://limyreth.sin.khk.be/feeds/pyautomate.xml

pyautomate's state machine
==========================
pyautomate's state machine is a non-deterministic finite state machine (NFA)
with the concept of guards added to its transitions, i.e. the transition can
only be taken if the guard is true. If that made no sense to you, read on.

pyautomate's state machine is a system based on states and transitions between
those states. The machine starts in one or more initial states and can be asked to try to
get to a desired state. A transition consists of a source state, multiple
target states and the action to execute in order to make the transition.

The state machine can be represented as a state diagram, e.g.:

.. image:: https://github.com/limyreth/pyautomate/raw/master/readme_files/usage_diagram.png

The state machine can be in multiple states at the same time (as it is
non-deterministic). E.g. when executing 'test_server()' with 'server started'
as current state, the machine will switch to both 'server started' and 'server
passed tests'. After that, it can still make a transition to 'server stopped'
and 'server passed tests' by executing 'stop_server()'.

Usage
=====
If you're not familiar with state machines, you should read `the above`__ first.

__ `state machine`_

I'll explain pyautomate with a simple example: developing a daemon. I want to
start, stop the daemon and run tests. If I want to run tests, the daemon should
obviously be running.

You usually want to start out by drawing your system on paper, for this case I
resulted with this `state diagram`__:

.. image:: https://github.com/limyreth/pyautomate/raw/master/readme_files/usage_diagram.png

This represents your state machine.

__ http://en.wikipedia.org/wiki/State_diagram

1 Write your auto.py file
-------------------------
The first step is to write an auto.py file. When running pyautomate, it looks
for this file in the working directory. You can also use the --file parameter
to point to a different file. 

The auto.py file contains:

- the definition of your state machine (a non-deterministic finite state
  machine to be exact)
- a function which returns the initial state of the state machine
- definitions of any transition functions you used
- optionally, weights of transitions

1.1 state_machine
'''''''''''''''''
Transform your diagram into `YAML`_ code that describes each state::

  states = '''
  - name: server stopped

    transitions:

        - action: start_server()
          to: server started

  - name: server started

    transitions:

        - action: stop_server()
          to: server stopped

        - action: test_server()
          to: 
              - server started
              - server passed tests
  '''

The action of each transition is python code that will be executed when the
transition is followed.

Note that the source state only needs to match the current state partially.
For example, when the current state is ('server started', 'server passed tests'),
it is clever enough to notice that it can get to ('server stopped', 'server
passed tests') by looking at the transitions of ('server started',).

Tip: you can put the YAML in a separate file like so::

  with open('states.yaml') as f:
      states = f.read()

Guards
``````
In some cases you may want to use guards to limit when a transition can be
done. Here's an example:

.. image:: https://github.com/limyreth/pyautomate/raw/master/readme_files/guard_diagram.png

In this case you would only want to release a new version when both the client
and the server tests succeed, so we'll use a guard for that, which is specified as::

  states = '''

  - name: not released

    transitions:

        - action: release()
          to: released last version
          guard:
              state contains:
                  - server passed tests
                  - client passed tests

  - name: server stopped

    transitions:

        - action: start_server()
          to: server started

  - name: server started

    transitions:

        - action: stop_server()
          to: server stopped

        - action: test_server()
          to: 
              - server started
              - server passed tests

  - name: client untested

    transitions:

        - action: test_client()
          to: client passed tests

  '''

I.e. not_released will only run when the state machine's current state
partially matches ('server passed tests', 'client passed tests')

Anonymous state
```````````````
The anonymous state is a nameless state. The current state always contains the
anonymous state. This allows you to use it as a starting point, e.g. you can
rewrite the guards example as follows::

  states = '''

  - transitions:

        - action: release()
          to: released last version
          guard:
              state contains:
                  - server passed tests
                  - client passed tests

        - action: test_client()
          to: client passed tests

  - name: server stopped

    transitions:

        - action: start_server()
          to: server started

  - name: server started

    transitions:

        - action: stop_server()
          to: server stopped

        - action: test_server()
          to: 
              - server started
              - server passed tests

  '''

This is shorter to write and is still easy to understand.


1.2 get_initial_state
'''''''''''''''''''''
pyautomate also needs a way to figure out the start state, so we have to
provide it with a get_initial_state function::

  def get_initial_state():
      # omitted code that finds out whether server is stopped/started
      return ('server stopped',)

This function returns a tuple of states in which the system starts (remember
that the state machine can be in multiple states at the same time).

When returning a single state, you may also return a string::

  def get_initial_state():
      # omitted code that finds out whether server is stopped/started
      return 'server stopped'

1.3 implement the actions
'''''''''''''''''''''''''
Now we'll define functions for anything we used as an action::

  # they don't really have to be defined here, they just have to be available
  # in this namespace
  from myproject.server import start_server, stop_server
  from myproject.tests import runner

  def test_server():
      tests_succeeded = runner.run_tests()
      if not tests_succeeded:
          raise Exception('tests failed')

Execution of actions stops at the first action that throws an exception.

1.4 weights
'''''''''''
You can influence pyautomation's path finding by attaching weights to actions.
The greater the weight the less likely an action is to be executed/followed.

Although not useful in this example, we could hint to pyautomate that
stop_server is inexpensive to execute by giving it a low weight::

  weights = {
      'test_server()' : 500
  }

Note that the omitted actions are assigned a default weight of 1000.

2 Run pyautomate
----------------
Now that auto.py is written, you can get it to run actions for you. 

I like to make the following alias for pyautomate::

  0alias auto http://limyreth.sin.khk.be/feeds/pyautomate.xml

Some examples::

  # all the examples are executed from the same directory as the auto.py file
  # (use --file param if you want to run elsewhere, note that pyautomate will
  cd to the directory where the file is located before executing it)

  # tests the server, and makes sure it's stopped afterwards
  auto 'server passed tests' 'server stopped'

  # you can use underscores instead of spaces
  auto server_passed_tests server_stopped

  # note that you don't have to specify the exact state a partial state will
  # do, e.g. if we don't care if the server is running or not but just want it
  # tested
  auto server_passed_tests

  # if you really do want an exact match, you can specify --exact to force this
  auto --exact server_passed_tests server_stopped

auto.py helper functions
========================

This lists functions that aid in writing auto.py functions: checking if a file
has changed, ...

pyautomate.persisted and pyautomate.has_changed
-----------------------------------------------
If you need to save data between pyautomate runs, you can use
pyautomate.persisted like so::

  from pyautomate import persisted

  def release():
      persisted['last released version'] = get_version()

Keys mustn't start with '#', these are reserved for pyautomate. The data is
saved in .pyautomate in the same directory as the auto.py file.

A common use case is to check if a saved value has changed since the last run::

  from pyautomate import has_changed

  def get_initial_state():
      last_released = not has_changed('last released version', get_version())
      return 'released last' if last_released else 'not released last'


More examples
=============
None, currently.

.. TODO: refer to other projects where we use pyautomate. Point directly to its
      page and its auto file

Features in upcoming releases
=============================
A GUI tool or a reader of UML state diagram files will be added to allow
specifying state machines more easily.

Partial desired state, rather than requiring a full state.


.. _YAML: http://en.wikipedia.org/wiki/YAML
.. _state machine: `pyautomate's state machine`_
