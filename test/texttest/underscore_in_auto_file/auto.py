# weightless
# not deterministic

state_machine = {
    ('server stopped',) : {
        'start_server()' : ('server_started',)
    },
}

def get_initial_state():
    return ('server stopped',)

def start_server():
    pass

