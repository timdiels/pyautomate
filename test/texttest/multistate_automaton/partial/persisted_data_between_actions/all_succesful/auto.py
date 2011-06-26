from pyautomate import persisted

states = '''
- name: server stopped

  transitions:

      - action: start_server()
        to: server started

- name: server started

  transitions:

      - action: test_server()
        to: 
            - server started
            - server passed tests
'''

def get_initial_state():
    return 'server stopped'


def start_server():
    persisted['a'] = 1

def test_server():
    persisted['b'] = 1
