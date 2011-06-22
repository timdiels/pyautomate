pyautomate is an automation tool. pyautomate can be used to automate any set
of tasks. pyautomate offers a KISS CLI + auto.py config file interface. Unlike
other tools, you describe a system as a state machine and specify how to get
from one state to the other. You then use the CLI to specify the state you want
to reach, and pyautomate will get it done.

If you would like to use it as a library, let me know
(limyreth@gmail.com) and I'll provide you with a documented API.

.. contents::

Install/run instructions
========================
pyautomate is distributed using 0install, and thus requires no installation,
you can just run it.

The 0install feed (with instructions):
http://limyreth.sin.khk.be/feeds/pyautomate.xml

Usage
=====

I'll explain by using a simple example: developing a daemon. I want to
start, stop the daemon and run tests. If I want to run tests, the daemon should
obviously be running.

You usually want to start out by drawing your system on paper, for this case I
resulted with this `state diagram`__:

.. image:: https://github.com/limyreth/pyautomate/raw/master/readme_files/usage_diagram.png

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

.. A case where you would want to specify multiple source states is the following:

.. .. image:: https://github.com/limyreth/pyautomate/raw/master/readme_files/multiple_source_diagram.png

.. In this case you would only want to release a new version when both the client
  and the server tests succeed, which is specified as::

..    state_machine = {
        ('server passed tests', 'client passed tests') : {
            'release()' : ('server passed tests', 'client passed tests',
                           'released version')
        }
        # other states and transitions omitted for brevity
    }

1.2 get_initial_state
'''''''''''''''''''''
pyautomate also needs a way to figure out the start state, so we have to
provide it with a get_initial_state function::

  def get_initial_state():
      # omitted code to figure out if server is stopped/started
      return ('server stopped',)

This function returns a tuple with the state in which the system starts.

1.3 action functions
''''''''''''''''''''
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
  # (use --file param if you insist on running elsewhere)

  # tests the server, and makes sure it's stopped afterwards
  auto 'server passed tests' 'server stopped'

  # you can use underscores instead of spaces
  auto server_passed_tests server_stopped

You currently have to specify the full desired state. 
  
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
