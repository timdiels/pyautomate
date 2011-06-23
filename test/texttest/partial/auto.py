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

- name: client untested

  transitions:

      - action: test_client()
        to: client passed tests

- name: not released

  transitions:

      - action: release()
        to: released last version
        guard:
            state contains:
                - server passed tests
                - client passed tests

'''

def get_initial_state():
    return ('server stopped', 'not released', 'client untested')

def start_server(): pass
def stop_server(): pass
def test_server(): pass
def test_client(): pass
def release(): pass
