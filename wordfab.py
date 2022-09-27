#!/usr/bin/python3

import configargparse
import os
import sys
import requests
import pathlib
import urllib.parse
import time

from prompt_toolkit import prompt, print_formatted_text, HTML
from bs4 import BeautifulSoup


# Set up globals
exec_name = os.path.basename(__file__)
exec_pieces = os.path.splitext(exec_name)
config_name = '{}.conf'.format(exec_pieces[0])
file_add = 'fab'
urllist_delay = 20


def convert(wordList, parseChars):
    newList = []
    for line in wordList:
        if line.find(parseChars[0]) != -1:
            subWordList = line.split(parseChars[0])
            for newWord in subWordList:
                if len(newWord) > 0:
                    newList.append(newWord)
            if len(parseChars[1:]) > 0:
                newList = convert(newList, parseChars[1:])
        else:
            newList.append(line)
    return newList


def remove_min(wordList, numChars):
    newList = []
    for line in wordList:
        if len(line) >= numChars:
            newList.append(line)
    return newList


def strip_nonalpha(wordList):
    newList = []
    for word in wordList:
        newWord = ''.join([i for i in word if i.isalpha()])
        if len(newWord) > 0:
            newList.append(newWord)
    return newList


def case_change(newCase, wordList):
    if newCase == 'upper':
        return list(line.upper() for line in wordList)
    else:
        return list(line.lower() for line in wordList)


def uniquify(wordList):
    return list(dict.fromkeys(wordList))


def alphabetize(wordList):
    return sorted(wordList, key=str.casefold)


def print_line(printText, endText='\n'):
    print_formatted_text(HTML(printText), end=endText)
    return


def create_dict(localAttrs):
    returnDict = {}
    for attr in localAttrs:
        dict_parts = attr.split('=')
        returnDict[dict_parts[0]] = dict_parts[1]
    if len(returnDict) > 0:
        return returnDict
    else:
        print_line('HTML attributes not entered correctly (use tag=term, see help for more info)')
        sys.exit()


def extract_from_web(extractWhat, soup):
    if extractWhat == 'text':
        localWords = soup.stripped_strings
    else:
        localWords = []
        for link in soup.find_all('a'):
            localWords.append(link.get('href'))
    return list(line for line in localWords)


def get_web_page(webURL, htmlParse, webExtract):
    try:
        r = requests.get(webURL)
        if r.status_code == 200:
            inputSoup = BeautifulSoup(r.text, 'html.parser')
            if htmlParse:
                parseDict = create_dict(htmlParse)
                return extract_from_web(webExtract, inputSoup.find(attrs=parseDict))
            else:
                return extract_from_web(webExtract, inputSoup)

    except (requests.URLRequired, requests.RequestException):
        return False

    except AttributeError:
        error_line = 'HTML attribute <ansired>{}</ansired> not found, check document and try again'
        print_line(error_line.format(htmlParse))
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


def setup_output(localArgs):
    # Has an output file been specified? If not, create from either file or URL
    if localArgs.output:
        outputFile = localArgs.output
    elif localArgs.input:
        filePieces = os.path.splitext(localArgs.input)
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


def setup_input(localArgs):
    returnWords = []

    # Load input(s)
    if localArgs.input:
        fileWords = get_file_content(localArgs.input)
        if fileWords:
            returnWords.extend(fileWords)

    if localArgs.webpage:
        webWords = get_web_page(localArgs.webpage, localArgs.htmlparse, localArgs.webextract)
        if webWords:
            returnWords.extend(webWords)

    if localArgs.urllist:
        urlList = get_file_content(localArgs.urllist)
        if urlList:
            urlLength = len(urlList)
            urlCount = 0

            for oneUrl in urlList:
                urlCount += 1
                urlText = 'Getting <ansired>{}</ansired> ({} of {})'
                print_line(urlText.format(oneUrl, urlCount, urlLength), endText='')
                webWords = get_web_page(oneUrl, localArgs.htmlparse, localArgs.webextract)
                if webWords:
                    returnWords.extend(webWords)
                    if urlCount < urlLength:
                        print_line('  ...done ...sleeping {} seconds'.format(urllist_delay))
                        time.sleep(urllist_delay)
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
                                           description='Fabulous word list builder')

    # Input and output options
    parser.add_argument('-i', '--input', type=pathlib.Path, help='Input text file')
    parser.add_argument('-w', '--webpage', help='Input web URL')
    parser.add_argument('--urllist', type=pathlib.Path, help='Input multiple URLs in a document')
    output_help = 'Output text file: if no name specified, "_{}" is added to either the\
                   input file name or web domain name and a new file is created'.format(file_add)
    parser.add_argument('-o', '--output', type=pathlib.Path, help=output_help)
    directory_help = 'Set directory for input, output and urllist files'
    parser.add_argument('--directory', type=pathlib.Path, help=directory_help)

    # List transformation options
    parser.add_argument('-a', '--alphabetize', action='store_true', help='Alphabetize the list')
    case_help = 'Change the case of words in the list'
    parser.add_argument('--case', choices=['lower', 'upper', 'none'], default='none', help=case_help)
    htmlparse_help = 'Further refines the text from a webpage by narrowing to any HTML entity(ies) specified,\
                      using tag=term syntax (e.g., ID=main_content or class=lyrics). Multiple entities can\
                      be specified'
    parser.add_argument('--htmlparse', action='append', help=htmlparse_help)
    webextract_help = 'Specify whether to extract text or links from webpage specified with -w'
    parser.add_argument('--webextract', choices=['text', 'links'], default='text', help=webextract_help)
    convert_help = 'Converts a block of text to a word list. Default delimiter is a space but acccepts\
                    any number of characters in quotes (e.g., --convert " ;," will separate words delimited\
                    by a space, comma or semicolon). Be careful with back slashes acting as an escape character'
    parser.add_argument('--convert', nargs='?', const=' ', help=convert_help)
    dedupe_help = 'Remove duplicates from the word list. Note that this is case sensitive so it is recommended\
                   that you also use --case {lower | upper} to put everything in the same case first'
    parser.add_argument('-d', '--dedupe', action='store_true', help=dedupe_help)
    min_ltrs = 3
    minimum_help = 'Set minimum number of letters in a word (if not specified, default is {})'.format(min_ltrs)
    parser.add_argument('-m', '--minimum', nargs='?', type=int, const=min_ltrs, help=minimum_help)
    strip_help = 'Remove non-alphabetic characters (including spaces)'
    parser.add_argument('-s', '--strip', action='store_true', help=strip_help)

    args = parser.parse_args()

    # See if a default directory was specified and rewrite inputs and outputs as necessary
    if args.directory is not None:
        if pathlib.Path(args.directory).is_dir():
            args.input = os.path.join(args.directory, args.input) if args.input else None
            args.urllist = os.path.join(args.directory, args.urllist) if args.urllist else None
            args.output = os.path.join(args.directory, args.output) if args.output else None
        else:
            directory_error = 'Exiting... directory path <ansired>{}</ansired> does not exist'
            print_line(directory_error.format(args.directory))
            sys.exit()

    outputFile = setup_output(args)
    inputWords = setup_input(args)

    # Do any text parsing
    if args.convert is not None:
        inputWords = convert(inputWords, args.convert)

    if args.strip:
        inputWords = strip_nonalpha(inputWords)

    # Do any text transforms
    if args.minimum is not None:
        inputWords = remove_min(inputWords, args.minimum)

    if args.case != 'none':
        inputWords = case_change(args.case, inputWords)

    if args.dedupe:
        inputWords = uniquify(inputWords)

    if args.alphabetize:
        inputWords = alphabetize(inputWords)

    # Now save the file
    saveFile = open(outputFile, 'w')

    for line in inputWords:
        saveFile.write('{}\n'.format(line))

    print_line('New word list saved to <ansired>{}</ansired>'.format(saveFile.name))
    saveFile.close()


if __name__ == '__main__':
    main()
