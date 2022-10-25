#!/usr/bin/env python3

import configargparse
import os
import sys
import requests
import pathlib
import urllib.parse
import time
import re

from prompt_toolkit import prompt, print_formatted_text, HTML
from bs4 import BeautifulSoup
from anyascii import anyascii
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


GLOBAL_SETTINGS = {
    'urllist_delay': 20,
    'file_add': 'xwl',
    'impact_color': 'ansired',
}

IMPACT_COLOR = GLOBAL_SETTINGS['impact_color']

COLOR_OPTIONS = ['ansiblack', 'ansired', 'ansigreen', 'ansiyellow', 'ansiblue', 'ansimagenta',
                 'ansicyan', 'ansigray', 'ansibrightblack', 'ansibrightred', 'ansibrightgreen',
                 'ansibrightyellow', 'ansibrightblue', 'ansibrightmagenta', 'ansibrightcyan', 'ansiwhite']


class WordList:
    def __init__(self, myList=[]):
        self.myList = myList

    # List transformation options
    def remove_min(self, numChars):
        newList = []
        for line in self.myList:
            if line and len(line) >= numChars:
                newList.append(line)
        self.myList = newList

    def strip_nonalpha(self, stripWhat):
        newList = []
        if stripWhat in ['keepdiacritic', 'diacritic', 'true']:
            for word in self.myList:
                if stripWhat != 'keepdiacritic':
                    word = anyascii(word)
                newWord = ''.join([i for i in word if i.isalpha()])
                if len(newWord) > 0:
                    newList.append(newWord)
            self.myList = newList
        else:
            print_text = 'Exiting... unknown strip option <{color}>{stripWhat}</{color}>'
            print_line(print_text, {'stripWhat': stripWhat})
            sys.exit()

    def case_change(self, newCase):
        case_dict = {
            'upper': str.upper,
            'lower': str.lower,
        }
        if newCase in case_dict:
            self.myList = list(case_dict[newCase](line) for line in self.myList)
        elif newCase != 'none':
            print_text = 'Exiting... unknown case option <{color}>{newcase}</{color}>'
            print_line(print_text, {'newcase': newCase})
            sys.exit()

    def uniquify(self, dedupeType):
        if dedupeType == 'bycase':
            self.myList = list(dict.fromkeys(self.myList))
        elif dedupeType in ['nocase', 'true']:
            newList = []
            newSet = set()
            for line in self.myList:
                newLine = line.casefold()
                if newLine not in newSet:
                    newSet.add(newLine)
                    newList.append(line)
            self.myList = newList
        else:
            print_text = 'Exiting... incorrect dedupe option <{color}>{dedupeType}</{color}>'
            print_line(print_text, {'dedupeType': dedupeType})
            sys.exit()

    def alphabetize(self):
        self.myList = sorted(self.myList, key=str.casefold)

    # Content parsing options
    def regex(self, regexInput):
        try:
            newList = []
            for line in self.myList:
                newList.extend(re.findall(regexInput, line))
            self.myList = newList

        except re.error:
            error_text = 'Regex pattern <{color}>{regexInput}</{color}> not valid, please check and try again'
            print_line(error_text, {'regexInput': regexInput})
            sys.exit()

        except Exception as e:
            print_line('Error {e}', {'e': e})
            sys.exit()

    def convert(self, parseChars):
        # First trap for problem where defaults are assumed but not specified
        if parseChars == 'true':
            parseChars = ' '
        for char in parseChars:
            newList = []
            for line in self.myList:
                if line.find(char) != -1:
                    newList.extend(line.split(char))
                else:
                    newList.append(line)
            self.myList = newList


def print_line(printText, argument={}, endText='\n'):
    print_formatted_text(HTML(printText.format(**argument, color=IMPACT_COLOR)), end=endText)
    return


def create_dict(localAttrs):
    returnDict = {}
    for attr in localAttrs:
        dict_parts = attr.split('=')
        if dict_parts[0][:2] == '--':
            dict_parts[0] = dict_parts[0][2:]
        # See if it is a class dictionary, in which case we make a tuple
        if dict_parts[0] == 'class':
            numParts = int(dict_parts[2]) if len(dict_parts) == 3 else 0
            returnDict[dict_parts[0]] = (dict_parts[1], numParts)
        elif len(dict_parts) > 1:
            returnDict[dict_parts[0]] = dict_parts[1]
        else:
            print_text = 'Exiting... incorrect option <{color}>{dictPart}</{color}>'
            print_line(print_text, {'dictPart': dict_parts[0]})
            sys.exit()
    if len(returnDict) > 0:
        return returnDict
    else:
        print_line('Exiting... something is wrong with your configuration file')
        sys.exit()


def extract_from_web(extractWhat, soup, extractURL):
    # A few ways the default option can come in, try that first
    if extractWhat == 'text' or extractWhat == 'true' or extractWhat is None:
        localWords = soup.stripped_strings
    elif extractWhat == 'links':
        localWords = []
        for link in soup.find_all('a'):
            getURL = link.get('href')
            if getURL:
                parsePieces = urllib.parse.urlsplit(getURL)
                # Check to see if absolute or relative URL.  If relative, make it absolute
                if parsePieces.scheme == '' and parsePieces.netloc == '':
                    parseExtract = urllib.parse.urlsplit(extractURL)
                    getURL = urllib.parse.urljoin(f'{parseExtract.scheme}://{parseExtract.netloc}', getURL)
                localWords.append(getURL)
    elif extractWhat[:5] == 'html-':
        localWords = []
        extractTags = extractWhat[5:].split('_')
        for tag in extractTags:
            for link in soup.find_all(tag):
                text = link.get_text()
                localWords.append(text)
    else:
        print_text = 'Exiting... incorrect option for webextract:  <{color}>{extractWhat}</{color}>'
        print_line(print_text, {'extractWhat': extractWhat})
        sys.exit()

    return list(line for line in localWords)


def get_web_page(webURL, containerParse, webExtract):
    try:
        r = requests.get(webURL)
        if r.status_code == 200:
            inputSoup = BeautifulSoup(r.text, 'html.parser')
            if containerParse:
                parseDict = create_dict(containerParse)
                # See if we have a class, in which case, have to do more screening (1 to N classes)
                if 'class' in parseDict:
                    classDict = {}
                    classDict['class'], whichNum = parseDict['class']
                    returnWords = []
                    fullSoup = inputSoup.find_all(attrs=classDict)
                    for counter, whichSoup in enumerate(fullSoup, start=1):
                        if whichNum == counter or whichNum == 0:
                            returnWords.extend(extract_from_web(webExtract, whichSoup, webURL))
                    return returnWords
                else:
                    return extract_from_web(webExtract, inputSoup.find(attrs=parseDict), webURL)
            else:
                return extract_from_web(webExtract, inputSoup, webURL)
        elif r.status_code == 403:
            print_line('Unable to load webpage due to code 403: this usually means we are being blocked')

        else:
            print_text = 'Unable to load webpage, status code = {statusCode}'
            print_line(print_text, {'statusCode': r.status_code})

    except (requests.URLRequired, requests.RequestException):
        return False

    except AttributeError:
        error_text = 'HTML attribute <{color}>{containerParse}</{color}> not found, check document and try again'
        print_line(error_text, {'containerParse': containerParse})
        sys.exit()

    except Exception as e:
        print_line('Web error {e}', {'e': e})
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

    # Has an output file been specified? If not, create from either file or URL
    if localArgs.output:
        outputFile = localArgs.output
    elif localArgs.input or localArgs.urllist:
        fileName = localArgs.input if localArgs.input else localArgs.urllist
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


def setup_input(localArgs, otherArgs):
    returnWords = []

    # Load input(s)
    if localArgs.input:
        fileWords = get_file_content(localArgs.input)
        if fileWords:
            returnWords.extend(fileWords)

    if localArgs.webpage:
        webWords = get_web_page(localArgs.webpage, localArgs.container, localArgs.webextract)
        if webWords:
            returnWords.extend(webWords)

    if localArgs.urllist:
        urlList = get_file_content(localArgs.urllist)
        if urlList:
            urlLength = len(urlList)

            for urlCount, oneUrl in enumerate(urlList, start=1):
                print_text = 'Getting <{color}>{oneUrl}</{color}> ({urlCount} of {urlLength})'
                arg_dict = {
                    'oneUrl': oneUrl,
                    'urlCount': urlCount,
                    'urlLength': urlLength,
                }
                print_line(print_text, arg_dict, endText='')
                webWords = get_web_page(oneUrl, localArgs.container, localArgs.webextract)
                if webWords:
                    returnWords.extend(webWords)
                    if urlCount < urlLength:
                        delay = int(otherArgs['urllist_delay']) if 'urllist_delay' in otherArgs else GLOBAL_SETTINGS['urllist_delay']
                        print_line('  ...done ...sleeping {delay} seconds', {'delay': delay})
                        time.sleep(delay)
                    else:
                        print_line('  ...done')
                else:
                    print_line(' ...no content retrieved, was that a URL?')

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


def main():
    # First set up configargparse
    parser = configargparse.ArgumentParser(default_config_files=[CONFIG_EXEC, CONFIG_HOME],
                                           description='Crossword puzzle word list builder')

    # Meta options
    parser.add_argument('-v', '--version', action='version', version=f"{FILE['name']} {__version__}")
    parser.add_argument('--config', action='store_true', help='locate your config file and quit')

    # Input and output options
    parser.add_argument('-i', '--input', type=pathlib.Path, help='Input text file')
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
    parser.add_argument('--webextract', nargs='?', default='text', help=webextract_help)
    convert_help = 'Convert a block of text to a word list. Default delimiter is a space but acccepts\
                    any number of characters in quotes (e.g., --convert " ;," will separate words delimited\
                    by a space, comma or semicolon). Be careful with back slashes acting as an escape character'
    parser.add_argument('--convert', nargs='?', const=' ', help=convert_help)
    parser.add_argument('--regex', nargs=1, help='Parse text based on regex')

    # List transformation options
    parser.add_argument('-a', '--alphabetize', action='store_true', help='Alphabetize the list')
    case_help = ' {none (default) | lower | upper} Change the case of words in the list'
    parser.add_argument('--case', nargs='?', const='none', help=case_help)
    dedupe_help = '{nocase (default) | bycase} Remove duplicates from the word list. By default, ignores\
                   case: "apple" and "APPLE" are the same word and the first instance found is kept.\
                   Use --dedupe bycase to treat each as a different word'
    parser.add_argument('-d', '--dedupe', nargs='?', const='nocase', help=dedupe_help)
    min_ltrs = 3
    minimum_help = f'Set minimum number of letters in a word (if not specified, default is {min_ltrs})'
    parser.add_argument('-m', '--minimum', nargs='?', type=int, const=min_ltrs, help=minimum_help)
    strip_help = '{diacritic (default) | keepdiacritic} Remove non-alphabetic characters (including spaces).\
                  By default, converts diacritical marks into English letters  (e.g., Renée becomes Renee).\
                  Use --strip keepdiacritic to leave diacriticals in.'
    parser.add_argument('-s', '--strip', nargs='?', const='diacritic', help=strip_help)

    args = parser.parse_known_args()
    confArgs = args[0]

    # Check to see if we've found any configuration data
    envArgs = create_dict(args[1]) if len(args[1]) > 0 else {}

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
            confArgs.input = os.path.join(confArgs.directory, confArgs.input) if confArgs.input else None
            confArgs.urllist = os.path.join(confArgs.directory, confArgs.urllist) if confArgs.urllist else None
            confArgs.output = os.path.join(confArgs.directory, confArgs.output) if confArgs.output else None
        else:
            print_text = 'Exiting... directory path <{color}>{directory}</{color}> does not exist'
            print_line(print_text, {'directory': confArgs.directory})
            sys.exit()

    outputFile = setup_output(confArgs, envArgs)
    inputWords = WordList(setup_input(confArgs, envArgs))

    # Do any text parsing
    if confArgs.regex is not None:
        if confArgs.regex[0] == 'true':
            regex_error = 'Exiting... no regex pattern given, please use format '
            regex_error += '<{color}>regex PATTERN</{color}> in configuration file'
            print_line(regex_error)
            sys.exit()
        inputWords.regex(confArgs.regex[0])

    if confArgs.convert is not None:
        inputWords.convert(confArgs.convert)

    if confArgs.strip is not None:
        inputWords.strip_nonalpha(confArgs.strip)

    # Do any text transforms
    if confArgs.minimum is not None:
        inputWords.remove_min(confArgs.minimum)

    if confArgs.case is not None:
        inputWords.case_change(confArgs.case)

    if confArgs.dedupe is not None:
        inputWords.uniquify(confArgs.dedupe)

    if confArgs.alphabetize:
        inputWords.alphabetize()

    # Now save the file
    save_output(outputFile, inputWords)


if __name__ == '__main__':
    main()
