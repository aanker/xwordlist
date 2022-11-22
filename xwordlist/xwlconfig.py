import os
import configparser

from importlib.metadata import version


# Set up globals
__version__ = version('xwordlist')

FILE = {
    'name': 'xwordlist',
    'conf': 'xwordlist.conf',
}

CONFIG = os.path.join(os.path.expanduser('~/.config/xwordlist'), FILE['conf'])

DEFAULTS = {
    'convert': '',
    'strip': 'diacritic',
    'minimum': 3,
    'case': 'upper',
    'dedupe': 'nocase',
    'webextract': 'text',
    'alphabetize': 'normal',
}

GLOBAL_SETTINGS = {
    'urllist_delay': 20,
    'file_add': 'xwl',
    'impact_color': 'ansired',
}

IMPACT_COLOR = 'ansired'
COLOR_OPTIONS = ['ansiblack', 'ansired', 'ansigreen', 'ansiyellow', 'ansiblue', 'ansimagenta',
                 'ansicyan', 'ansigray', 'ansibrightblack', 'ansibrightred', 'ansibrightgreen',
                 'ansibrightyellow', 'ansibrightblue', 'ansibrightmagenta', 'ansibrightcyan', 'ansiwhite']


def init_config():
    configClass = configparser.ConfigParser()
    configClass['globals'] = GLOBAL_SETTINGS
    configClass['defaults'] = DEFAULTS

    # First see if the config file exists and if not, create it
    if not os.path.exists(CONFIG):
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        open(CONFIG, 'w').close()

    # Otherwise read the file
    else:
        configClass.read_file(open(CONFIG))

    # See if conf file contains an impact color
    global IMPACT_COLOR
    IMPACT_COLOR = configClass.get('globals', 'impact_color')

    # Now write a new file
    configClass.write(open(CONFIG, 'w'))
    return configClass
