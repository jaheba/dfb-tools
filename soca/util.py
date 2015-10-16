
import imp
import os
from ConfigParser import ConfigParser

def find_file(name, exclude=os.getenv('HOME')):
    current_dir = os.getcwd()

    while not os.path.exists(os.path.join(current_dir, name)):
        if current_dir in (exclude, '/'):
            break
        current_dir = os.path.dirname(current_dir)
    else:
        return os.path.join(current_dir, name)

    return None

def read_config(path):
    namespace = {}
    execfile(path, {}, namespace)
    return namespace
