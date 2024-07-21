import json


def await_function(message):
    val = json.loads(message.value())
    print(f'The message value is: {val}')
    return val
