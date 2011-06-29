from pyautomate import trackers, hash_

states = ''

def get_initial_state():
    trackers['last compiled'] = lambda: hash_('file.f')
    trackers['last compiled'].save()
    return 'state'

