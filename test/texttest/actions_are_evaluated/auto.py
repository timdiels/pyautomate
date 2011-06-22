# weightless
# not deterministic

states = '''
- name: server stopped

  transitions:

      - action: start_server()
        to: server started
'''

def get_initial_state():
    return ('server stopped',)


