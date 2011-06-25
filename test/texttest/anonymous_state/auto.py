states = '''
- transitions:

      - action: run_client_a()
        to: client a running

      - action: run_client_b()
        to: client b running
'''

def get_initial_state():
    return ()

def run_client_a(): pass
def run_client_b(): pass

