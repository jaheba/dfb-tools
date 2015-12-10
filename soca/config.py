
schema = ''

host = ''
port = None
user = ''
password = ''

import util
import os

_config = os.environ.get('SOCA_CONFIG') or util.find_file('.socarc')

if _config:
    locals().update(util.read_config(_config))