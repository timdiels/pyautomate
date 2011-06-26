from pyautomate import has_changed

states = ''

def get_initial_state():
    print(has_changed('key', 'value'))
    return 'state'

