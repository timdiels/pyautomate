from pyautomate import files_exist

states = ''

def get_initial_state():
    print(files_exist('file1.f', 'file2.f', 'directory.f'))
    return 'state'

