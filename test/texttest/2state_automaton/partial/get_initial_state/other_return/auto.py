states = '''
- name: server stopped

  transitions:

      - action: start_server()
        to: server started
'''

def get_initial_state():
    return 2

def start_server():
    pass

