from pyautomate import persisted

states = '''
'''

def get_initial_state():
    persisted['key'] = 'value'
    return 'state'

