states = '''
- name: A

  transitions:

      - action: c()
        to: C

      - action: b()
        to: B

- name: B

  transitions:

      - action: bc()
        to: C
'''


def get_initial_state():
    return ('A',)

def b(): pass
def c(): pass
def bc(): pass

weights = {
    'b()': 500,
    'bc()': 501
}
