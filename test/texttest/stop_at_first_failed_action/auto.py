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


def get_initial_state():
    return ('server stopped',)


def start_server():
    pass

def stop_server():
    pass

def test_server():
    print(this_will_stop_execution)
