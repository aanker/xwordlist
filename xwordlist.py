#!/usr/bin/env python3

import configargparse
import os
import sys
import pathlib
import urllib.parse
import time
import xwl

from prompt_toolkit import prompt, print_formatted_text, HTML
from importlib.metadata import version


# Set up globals
__version__ = version('xwordlist')

FILE = {
    'name': __name__,
    'conf': f'{__name__}.conf',
    'exec_path': os.path.dirname(os.path.abspath(__file__)),
    'user_path': os.path.join(pathlib.Path.home(), __name__, '')
}

REPO = {
    'home': 'https://github.com/aanker/xwordlist/',
    'conf': 'https://github.com/aanker/xwordlist/blob/main/xwordlist.conf',
}

CONFIG_EXEC = os.path.join(FILE['exec_path'], FILE['conf'])
CONFIG_HOME = os.path.join(FILE['user_path'], FILE['conf'])

DEFAULTS = {
    'convert': ' ',
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

IMPACT_COLOR = GLOBAL_SETTINGS['impact_color']
COLOR_OPTIONS = ['ansiblack', 'ansired', 'ansigreen', 'ansiyellow', 'ansiblue', 'ansimagenta',
                 'ansicyan', 'ansigray', 'ansibrightblack', 'ansibrightred', 'ansibrightgreen',
                 'ansibrightyellow', 'ansibrightblue', 'ansibrightmagenta', 'ansibrightcyan', 'ansiwhite']


def print_line(printText, argument={}, endText='\n'):
    print_formatted_text(HTML(printText.format(**argument, color=IMPACT_COLOR)), end=endText)
    return


def create_dict(localAttrs):
    returnDict = {}
    arg_list = []
    for attr in localAttrs:
        dict_parts = attr.split('=')
        if dict_parts[0][:2] == '--':
            dict_parts[0] = dict_parts[0][2:]
        # See if it is a class dictionary, in which case we make a tuple
        if dict_parts[0] == 'class':
            numParts = int(dict_parts[2]) if len(dict_parts) == 3 else 0
            returnDict[dict_parts[0]] = (dict_parts[1], numParts)
        elif len(dict_parts) > 1 and (dict_parts[0] in GLOBAL_SETTINGS or dict_parts[0] in ['class', 'id']):
            returnDict[dict_parts[0]] = dict_parts[1]
        else:
            arg_list.append(dict_parts[0])
    if len(arg_list) > 0:
        for arg in arg_list:
            print_text = 'Exiting... incorrect option <{color}>{arg}</{color}>'
            print_line(print_text, {'arg': arg})
        sys.exit()
    elif len(returnDict) > 0:
        return returnDict
    else:
        print_line('Exiting... something is wrong with your configuration settings')
        sys.exit()


def get_file_content(inputFile):
    try:
        with open(inputFile, 'r') as inputOpen:
            return list(line.strip() for line in inputOpen)

    except UnicodeDecodeError:
        print_line('Exiting... only text files accepted')
        sys.exit()

    except FileNotFoundError:
        error_text = 'Exiting... input file <{color}>{inputFile}</{color}> does not exist'
        print_line(error_text, {'inputFile': inputFile})
        sys.exit()

    except Exception as e:
        print_line('Exiting... file error {e}', {'e': e})
        sys.exit()


def save_output(localOuput, localWords):
    try:
        with open(localOuput, 'w') as outputOpen:
            outputOpen.writelines(str(line) + '\n' for line in localWords.myList)
        print_text = 'New list saved to <{color}>{output}</{color}>'
        print_line(print_text, {'output': outputOpen.name})

    except Exception as e:
        print_line('Exiting... file save error {e}', {'e': e})
        sys.exit()


def setup_output(localArgs, otherArgs):
    file_add = otherArgs['file_add'] if 'file_add' in otherArgs else GLOBAL_SETTINGS['file_add']

    try:
        # Has an output file been specified? If not, create from either file or URL
        if localArgs.output:
            outputFile = localArgs.output
        elif localArgs.input or localArgs.urllist:
            fileName = localArgs.input[0] if localArgs.input else localArgs.urllist
            filePieces = os.path.splitext(fileName)
            outputFile = f'{filePieces[0]}_{file_add}{filePieces[1]}'
        elif localArgs.webpage:
            urlPieces = urllib.parse.urlparse(localArgs.webpage).hostname.split('.')
            if len(urlPieces) > 1:
                outputFile = f'{urlPieces[-2]}_{urlPieces[-1]}_{file_add}.txt'
            else:
                outputFile = f'{urlPieces[0]}_{file_add}.txt'
            # See if a directory has been specified: don't need to check if valid by now
            if localArgs.directory is not None:
                outputFile = os.path.join(localArgs.directory, outputFile)
        else:
            # Nothing to set up
            return

        # Now check if the output file exists and prompt user if it does
        if pathlib.Path(outputFile).is_file():
            prompt_text = 'Output file named <{color}>{output}</{color}> already exists. Overwrite? (Y/N): '
            text = prompt(HTML(prompt_text.format(color=IMPACT_COLOR, output=outputFile)))
            if text != 'Y' and text != 'y':
                print_line('Exiting... please enter a different file name at the command line')
                sys.exit()
        return outputFile

    except AttributeError:
        print_line('Exiting... problem setting up output file. Probably a problem with the URL you entered')
        sys.exit()

    except Exception as e:
        print_line('Exiting... setup_output error {e}', {'e': e})
        sys.exit()


def setup_input(localArgs, otherArgs):
    returnWords = []
    parseDict = {}

    # Load input(s)
    if localArgs.input:
        for inputFile in localArgs.input:
            fileWords = get_file_content(inputFile)
            if fileWords:
                returnWords.extend(fileWords)

    if localArgs.webpage:
        if localArgs.container:
            parseDict = create_dict(localArgs.container)
        webScrape = xwl.WebExtract(color=IMPACT_COLOR)
        webScrape.get_web_page(localArgs.webpage, parseDict, localArgs.webextract)
        returnWords.extend(webScrape.returnWords)

    if localArgs.urllist:
        urlList = get_file_content(localArgs.urllist)
        if urlList:
            urlLength = len(urlList)
            if localArgs.container:
                parseDict = create_dict(localArgs.container)

            for urlCount, oneUrl in enumerate(urlList, start=1):
                print_text = 'Getting <{color}>{oneUrl}</{color}> ({urlCount} of {urlLength})'
                arg_dict = {
                    'oneUrl': oneUrl,
                    'urlCount': urlCount,
                    'urlLength': urlLength,
                }
                print_line(print_text, arg_dict, endText='')
                webScrape = xwl.WebExtract(color=IMPACT_COLOR)
                webScrape.get_web_page(oneUrl, parseDict, localArgs.webextract)
                returnWords.extend(webScrape.returnWords)
                if urlCount < urlLength:
                    delay = int(otherArgs['urllist_delay']) if 'urllist_delay' in otherArgs else GLOBAL_SETTINGS['urllist_delay']
                    print_line('  ...done ...sleeping {delay} seconds', {'delay': delay})
                    time.sleep(delay)
                else:
                    print_line('  ...done')

    if len(returnWords) == 0:
        print_text = 'No input given, nothing to do (enter <{color}>{exec_name} -h</{color}> for help)'
        print_line(print_text, {'exec_name': FILE['name']})
        sys.exit()

    return returnWords


def do_config():
    # Tells user where their config file is
    if pathlib.Path(CONFIG_EXEC).is_file() and pathlib.Path(CONFIG_HOME).is_file():
        print_text = 'There are configuration files located at both <{color}>{config_exec}</{color}>'
        print_text += ' and <{color}>{config_home}</{color}>.\nThe one located in the folder <{color}>{home_path}</{color}>'
        print_text += ' will take precedence and is the one you should edit.'
        arg_dict = {
            'config_home': CONFIG_HOME,
            'config_exec': CONFIG_EXEC,
            'home_path': FILE['user_path'],
        }
        print_line(print_text, arg_dict)
        sys.exit()

    elif pathlib.Path(CONFIG_EXEC).is_file():
        whereFile = CONFIG_EXEC
    elif pathlib.Path(CONFIG_HOME).is_file():
        whereFile = CONFIG_HOME
    else:
        print_text = 'Cannot find a configuration file.\nYou should download a new version from this'
        print_text += ' location: <{color}>{repo_conf}</{color}>\nSave it in a directory'
        print_text += ' located at <{color}>{home_path}</{color}> and edit it there.'
        arg_dict = {
            'repo_conf': REPO['conf'],
            'home_path': FILE['user_path'],
        }
        print_line(print_text, arg_dict)
        sys.exit()

    print_text = 'Your configuration file is located at <{color}>{whereFile}</{color}>'
    print_line(print_text, {'whereFile': whereFile})
    sys.exit()


def do_word_options(localWords, localArgs):
    thatOption = ''
    if localArgs.line2word and localArgs.word2word:
        print_text = 'Options <{color}>line2word</{color}> and <{color}>word2word</{color}>'
        print_text += ' are mutually exclusive, please use either but not both'
        print_line(print_text)
        sys.exit()
    elif localArgs.word2word:
        # If word2word we first do a convert
        localWords.convert(DEFAULTS['convert'])
        thatOption = 'word2word'
    # Now run through all the other options
    optionList = ['strip', 'minimum', 'case', 'dedupe', 'alphabetize']
    for option in optionList:
        getattr(localWords, option)(DEFAULTS[option])

    if thatOption == '':
        thatOption = 'line2word'
    return localWords, thatOption


def do_ignore(whichOption, thatOption):
    print_text = 'Option <{color}>{whichOption}</{color}> ignored due to use of <{color}>{thatOption}</{color}>'
    arg_dict = {
        'whichOption': whichOption,
        'thatOption': thatOption,
    }
    print_line(print_text, arg_dict)


def main():
    # First set up configargparse
    parser = configargparse.ArgumentParser(default_config_files=[CONFIG_EXEC, CONFIG_HOME],
                                           description='Crossword puzzle word list builder')

    # Meta options
    parser.add_argument('-v', '--version', action='version', version=f"{FILE['name']} {__version__}")
    parser.add_argument('--config', action='store_true', help='locate your config file and quit')

    # Input and output options
    parser.add_argument('-i', '--input', nargs='*', type=pathlib.Path, help='Input one or more text file(s)')
    parser.add_argument('-w', '--webpage', help='Input web URL')
    parser.add_argument('--urllist', type=pathlib.Path, help='Input multiple URLs in a document')
    output_help = 'Output text file: if no name specified, a default name is created'
    parser.add_argument('-o', '--output', type=pathlib.Path, help=output_help)
    directory_help = 'Set directory for input, output and urllist files'
    parser.add_argument('--directory', type=pathlib.Path, help=directory_help)

    # Content parsing options
    container_help = 'Further refines the text from a webpage by narrowing to any HTML entity(ies) specified,\
                      using tag=term syntax (e.g., id=main_content or class=lyrics).'
    parser.add_argument('--container', nargs=1, help=container_help)
    webextract_help = 'Specify whether to extract text, links or specific tags from web inputs'
    parser.add_argument('--webextract', nargs='?', default=DEFAULTS['webextract'], help=webextract_help)
    parser.add_argument('--regex', nargs=1, help='Parse text based on regex')

    # List transformation options
    line2word_help = 'Convert each line of text into a word by stripping out spaces and other non-alphabetic\
                      characters, dedupe the list, alphabetize and capitalize every word. Remove all words\
                      below the minimum word size. This is the equivalent of running xwordlist with each of those\
                      options set and saves having to enter each one individually. See the help documentation to\
                      better understand how this works.'
    parser.add_argument('--line2word', action='store_true', help=line2word_help)
    word2word_help = 'Convert blocks of text into individual words delimited by spaces, strip out non-alphabetic\
                      characters, dedupe the list, alphabetize and capitalize every word. Remove all words\
                      below the minimum word size. This is the equivalent of running xwordlist with each of those\
                      options set and saves having to enter each one individually. See the help documentation to\
                      better understand how this works.'
    parser.add_argument('--word2word', action='store_true', help=word2word_help)
    convert_help = 'Convert a block of text into individual words, separating words by spaces. See help\
                    documentation for additional options'
    parser.add_argument('--convert', nargs='?', const=DEFAULTS['convert'], help=convert_help)
    alphabetize_help = '{normal (default) | reverse} Alphabetize the list'
    parser.add_argument('-a', '--alphabetize', nargs='?', const=DEFAULTS['alphabetize'], help=alphabetize_help)
    case_help = ' {upper (default) | lower | none} Change the case of words in the list'
    parser.add_argument('--case', nargs='?', const=DEFAULTS['case'], help=case_help)
    dedupe_help = '{nocase (default) | bycase} Remove duplicates from the word list. By default, ignores\
                   case: "apple" and "APPLE" are the same word and the first instance found is kept.\
                   Use --dedupe bycase to treat each as a different word'
    parser.add_argument('-d', '--dedupe', nargs='?', const=DEFAULTS['dedupe'], help=dedupe_help)
    minimum_help = f"Set minimum number of letters in a word (if not specified, default is {DEFAULTS['minimum']})"
    parser.add_argument('-m', '--minimum', nargs='?', const=DEFAULTS['minimum'], help=minimum_help)
    strip_help = '{diacritic (default) | keepdiacritic} Remove non-alphabetic characters (including spaces).\
                  By default, converts diacritical marks into English letters  (e.g., Renée becomes Renee).\
                  Use --strip keepdiacritic to leave diacriticals in.'
    parser.add_argument('-s', '--strip', nargs='?', const=DEFAULTS['strip'], help=strip_help)

    args = parser.parse_known_args()
    confArgs = args[0]

    # Check to see if we've found any additional configuration data
    envArgs = create_dict(args[1]) if len(args[1]) > 0 else {}

    # Update items with defaults that come through as 'true'
    for arg in DEFAULTS:
        if getattr(confArgs, arg) == 'true':
            setattr(confArgs, arg, DEFAULTS[arg])

    # See if conf file contains an impact color
    if 'impact_color' in envArgs and f"ansi{envArgs['impact_color']}" in COLOR_OPTIONS:
        global IMPACT_COLOR
        IMPACT_COLOR = f"ansi{envArgs['impact_color']}"

    # See if the user selected --config, in which case we should handle that immediately
    if confArgs.config:
        do_config()

    # See if a default directory was specified and rewrite inputs and outputs as necessary
    if confArgs.directory is not None:
        if pathlib.Path(confArgs.directory).is_dir():
            if confArgs.input:
                inputFiles = []
                for inputFile in confArgs.input:
                    inputFiles.append(os.path.join(confArgs.directory, inputFile) if inputFile else None)
                confArgs.input = inputFiles
            confArgs.urllist = os.path.join(confArgs.directory, confArgs.urllist) if confArgs.urllist else None
            confArgs.output = os.path.join(confArgs.directory, confArgs.output) if confArgs.output else None
        else:
            print_text = 'Exiting... directory path <{color}>{directory}</{color}> does not exist'
            print_line(print_text, {'directory': confArgs.directory})
            sys.exit()

    # Set up output file to make sure it doesn't exist then grab all inputs (including web parsing)
    outputFile = setup_output(confArgs, envArgs)
    try:
        inputWords = xwl.WordList(myList=setup_input(confArgs, envArgs), color=IMPACT_COLOR)

        # Do any text parsing
        if confArgs.regex is not None:
            if confArgs.regex[0] == 'true':
                regex_error = 'Exiting... no regex pattern given, please use format '
                regex_error += '<{color}>regex PATTERN</{color}> in configuration file'
                print_line(regex_error)
                sys.exit()
            inputWords.regex(confArgs.regex[0])

        # First figure out if they set either combination option
        if confArgs.line2word or confArgs.word2word:
            inputWords, thatOption = do_word_options(inputWords, confArgs)
        else:
            thatOption = False

        # Now run through remaining options
        # We also trap for the case where the user had one of the line2word or word2word options
        # but also uses one of the duplicative other options (we ignore the duplicative one)
        optionList = ['convert', 'strip', 'minimum', 'case', 'dedupe', 'alphabetize']
        for option in optionList:
            confOption = getattr(confArgs, option)
            if confOption is not None:
                do_ignore(option, thatOption) if thatOption else getattr(inputWords, option)(confOption)

    except xwl.XWLException as e:
        print_formatted_text(HTML(e))
        sys.exit()

    # Now save the file
    save_output(outputFile, inputWords)


if __name__ == '__main__':
    main()
