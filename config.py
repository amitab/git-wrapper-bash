import re

branch_types = {
    'bug': {
        'default_parent': 'master',
        'regex': re.compile('[bB][uU][gG]')
    },
    'wl': {
        'default_parent': 'master',
        'regex': re.compile('[wW][lL]')
    }
}