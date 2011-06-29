from pyautomate import trackers, hash_

states = ''

def get_initial_state():
    trackers['last compiled'] = lambda: hash_('directory.f')
    trackers['last compiled'].make_current()
    return 'state'

