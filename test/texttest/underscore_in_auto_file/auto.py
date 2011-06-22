states = '''
- name: server_stopped

  transitions:

      - action: start_server()
        to: server_started
'''

def get_initial_state():
    return ('server stopped',)

def start_server():
    pass

