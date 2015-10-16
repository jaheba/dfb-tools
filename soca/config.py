
schema = ''

host = ''
port = None
user = ''
password = ''

import util
_config = util.find_file('.socarc')
if _config:
    locals().update(util.read_config(_config))