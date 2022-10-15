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


# Set up globals
__version__ = '22.01.02'
exec_name = os.path.basename(__file__)
exec_pieces = os.path.splitext(exec_name)
config_name = '{}.conf'.format(exec_pieces[0])

GLOBAL_SETTINGS = {
    'urllist_delay': 20,
    'file_add': 'xwl',
}


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

    def strip_nonalpha(self):
        newList = []
        for word in self.myList:
            newWord = ''.join([i for i in word if i.isalpha()])
            if len(newWord) > 0:
                newList.append(newWord)
        self.myList = newList

    def case_change(self, newCase):
        case_dict = {
            'upper': str.upper,
            'lower': str.lower,
        }
        if newCase in case_dict:
            self.myList = list(case_dict[newCase](line) for line in self.myList)
        elif newCase != 'none':
            print_line('Exiting... unknown case option <ansired>{}</ansired>'.format(newCase))
            sys.exit()

    def uniquify(self):
        self.myList = list(dict.fromkeys(self.myList))

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
            error_line = 'Regex pattern <ansired>{}</ansired> not valid, please check and try again'
            print_line(error_line.format(regexInput))
            sys.exit()

        except Exception as e:
            print_line('Error {}'.format(e))
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


def print_line(printText, endText='\n'):
    print_formatted_text(HTML(printText), end=endText)
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
            print_line('Exiting... incorrect option <ansired>{}</ansired>'.format(dict_parts[0]))
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
                    getURL = urllib.parse.urljoin('{}://{}'.format(parseExtract.scheme, parseExtract.netloc), getURL)
                localWords.append(getURL)
    elif extractWhat[:5] == 'html-':
        localWords = []
        extractTags = extractWhat[5:].split('_')
        for tag in extractTags:
            for link in soup.find_all(tag):
                text = link.get_text()
                localWords.append(text)
    else:
        print_line('Exiting... incorrect option for webextract:  <ansired>{}</ansired>'.format(extractWhat))
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
            print_line('Unable to load webpage, status code = {}'.format(r.status_code))

    except (requests.URLRequired, requests.RequestException):
        return False

    except AttributeError:
        error_line = 'HTML attribute <ansired>{}</ansired> not found, check document and try again'
        print_line(error_line.format(containerParse))
        sys.exit()

    except Exception as e:
        print_line('Web error {}'.format(e))
        sys.exit()


def get_file_content(inputFile):
    try:
        with open(inputFile, 'r') as inputOpen:
            return list(line.strip() for line in inputOpen)

    except UnicodeDecodeError:
        print_line('Exiting... only text files accepted')
        sys.exit()

    except FileNotFoundError:
        print_line('Exiting... input file <ansired>{}</ansired> does not exist'.format(inputFile))
        sys.exit()

    except Exception as e:
        print_line('Exiting... file error {}'.format(e))
        sys.exit()


def setup_output(localArgs, otherArgs):
    file_add = otherArgs['file_add'] if 'file_add' in otherArgs else GLOBAL_SETTINGS['file_add']

    # Has an output file been specified? If not, create from either file or URL
    if localArgs.output:
        outputFile = localArgs.output
    elif localArgs.input or localArgs.urllist:
        fileName = localArgs.input if localArgs.input else localArgs.urllist
        filePieces = os.path.splitext(fileName)
        outputFile = '{}_{}{}'.format(filePieces[0], file_add, filePieces[1])
    elif localArgs.webpage:
        urlPieces = urllib.parse.urlparse(localArgs.webpage).hostname.split('.')
        if len(urlPieces) > 1:
            outputFile = '{}_{}_{}.txt'.format(urlPieces[-2], urlPieces[-1], file_add)
        else:
            outputFile = '{}_{}.txt'.format(urlPieces[0], file_add)
        # See if a directory has been specified: don't need to check if valid by now
        if localArgs.directory is not None:
            outputFile = os.path.join(localArgs.directory, outputFile)
    else:
        # Nothing to set up
        return

    # Now check if the output file exists and prompt user if it does
    if pathlib.Path(outputFile).is_file():
        text = prompt(HTML('Output file named <ansired>{}</ansired> already exists. Overwrite? (Y/N): '.format(outputFile)))
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
                urlText = 'Getting <ansired>{}</ansired> ({} of {})'
                print_line(urlText.format(oneUrl, urlCount, urlLength), endText='')
                webWords = get_web_page(oneUrl, localArgs.container, localArgs.webextract)
                if webWords:
                    returnWords.extend(webWords)
                    if urlCount < urlLength:
                        delay = int(otherArgs['urllist_delay']) if 'urllist_delay' in otherArgs else GLOBAL_SETTINGS['urllist_delay']
                        print_line('  ...done ...sleeping {} seconds'.format(delay))
                        time.sleep(delay)
                    else:
                        print_line('  ...done')
                else:
                    print_line(' ...no content retrieved, was that a URL?')

    if len(returnWords) == 0:
        help_text = 'No input given, nothing to do (enter <ansired>{} -h</ansired> for help)'
        print_line(help_text.format(exec_name))
        sys.exit()

    return returnWords


def main():
    # First set up configargparse
    parser = configargparse.ArgumentParser(default_config_files=[config_name],
                                           description='Crossword puzzle word list builder')

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
    case_help = 'Change the case of words in the list'
    parser.add_argument('--case', choices=['lower', 'upper', 'none'], default='none', help=case_help)
    dedupe_help = 'Remove duplicates from the word list. Note that this is case sensitive so it is recommended\
                   that you also use --case {lower | upper} to put everything in the same case first'
    parser.add_argument('-d', '--dedupe', action='store_true', help=dedupe_help)
    min_ltrs = 3
    minimum_help = 'Set minimum number of letters in a word (if not specified, default is {})'.format(min_ltrs)
    parser.add_argument('-m', '--minimum', nargs='?', type=int, const=min_ltrs, help=minimum_help)
    strip_help = 'Remove non-alphabetic characters (including spaces)'
    parser.add_argument('-s', '--strip', action='store_true', help=strip_help)

    args = parser.parse_known_args()
    confArgs = args[0]
    envArgs = create_dict(args[1])

    # See if a default directory was specified and rewrite inputs and outputs as necessary
    if confArgs.directory is not None:
        if pathlib.Path(confArgs.directory).is_dir():
            confArgs.input = os.path.join(confArgs.directory, confArgs.input) if confArgs.input else None
            confArgs.urllist = os.path.join(confArgs.directory, confArgs.urllist) if confArgs.urllist else None
            confArgs.output = os.path.join(confArgs.directory, confArgs.output) if confArgs.output else None
        else:
            directory_error = 'Exiting... directory path <ansired>{}</ansired> does not exist'
            print_line(directory_error.format(confArgs.directory))
            sys.exit()

    outputFile = setup_output(confArgs, envArgs)
    inputWords = WordList(setup_input(confArgs, envArgs))

    # Do any text parsing
    if confArgs.regex is not None:
        if confArgs.regex[0] == 'true':
            regex_error = 'Exiting... no regex pattern given, please use format '
            regex_error += '<ansired>regex PATTERN</ansired> in configuration file'
            print_line(regex_error)
            sys.exit()
        inputWords.regex(confArgs.regex[0])

    if confArgs.convert is not None:
        inputWords.convert(confArgs.convert)

    if confArgs.strip:
        inputWords.strip_nonalpha()

    # Do any text transforms
    if confArgs.minimum is not None:
        inputWords.remove_min(confArgs.minimum)

    if confArgs.case != 'none':
        inputWords.case_change(confArgs.case)

    if confArgs.dedupe:
        inputWords.uniquify()

    if confArgs.alphabetize:
        inputWords.alphabetize()

    # Now save the file
    saveFile = open(outputFile, 'w')

    for line in inputWords.myList:
        saveFile.write('{}\n'.format(line))

    print_line('New list saved to <ansired>{}</ansired>'.format(saveFile.name))
    saveFile.close()


if __name__ == '__main__':
    main()
