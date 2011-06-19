# weightless
# not deterministic

state_machine = {
    ('server stopped',) : {
        'start_server()' : ('server started',)
    },
    ('server started',) : {
        'stop_server()' : ('server stopped',),
        'test_server()' : ('server started', 'server passed tests')
    }
    # TODO rm this?
    # a group:
    #('server passed tests', 'client passed tests') : {
    #    'release_version()' : ('server passed tests', 'client passed tests', 'version released')
    #}
}

def get_initial_state():
    return ('server stopped',)

def start_server():
    pass

def stop_server():
    pass

def test_server():
    pass
