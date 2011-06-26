from pyautomate import has_file_changed

states = ''

def get_initial_state():
    print(has_file_changed('file.f'))
    return 'state'

