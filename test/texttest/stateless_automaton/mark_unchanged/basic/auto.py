from pyautomation import make_current

states = '''
'''

def get_initial_state():
    make_current('key', 'value')
    return 'state'

