# weightless
# not deterministic

state_machine = {
    ('server stopped',) : {
        'start_server()' : ('server started',)
    },
}

def get_initial_state():
    return ('server stopped',)


