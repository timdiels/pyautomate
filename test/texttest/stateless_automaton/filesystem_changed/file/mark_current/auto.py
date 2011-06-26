from pyautomate import mark_file_current

states = ''

def get_initial_state():
    mark_file_current('file.f')
    return 'state'

