#!/usr/bin/python3

import configargparse
import os
import sys
import requests
import pathlib
import urllib.parse

from prompt_toolkit import prompt, print_formatted_text, HTML
from bs4 import BeautifulSoup


# Set up globals
exec_name = os.path.basename(__file__)
exec_pieces = os.path.splitext(exec_name)
config_name = '{}.conf'.format(exec_pieces[0])
file_add = 'fab'


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


def print_line(printText):
    print_formatted_text(HTML(printText))
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


def setup_output(localArgs):
    # Has an output file been specified? If not, create from either file or URL
    if localArgs.output:
        outputFile = localArgs.output
    elif localArgs.input:
        filePieces = os.path.splitext(localArgs.input.name)
        outputFile = '{}_{}{}'.format(filePieces[0], file_add, filePieces[1])
    elif localArgs.webpage:
        urlPieces = urllib.parse.urlparse(localArgs.webpage).hostname.split('.')
        if len(urlPieces) > 1:
            outputFile = '{}_{}_{}.txt'.format(urlPieces[-2], urlPieces[-1], file_add)
        else:
            outputFile = '{}_{}.txt'.format(urlPieces[0], file_add)
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
        try:
            fileWords = list(line.strip() for line in localArgs.input)
            localArgs.input.close()
            returnWords.extend(fileWords)

        except UnicodeDecodeError:
            print_line('Sorry, only text files accepted')
            sys.exit()

        except Exception as e:
            print_line('File error {}'.format(e))
            sys.exit()

    if localArgs.webpage:
        try:
            r = requests.get(localArgs.webpage)
            if r.status_code == 200:
                inputSoup = BeautifulSoup(r.text, 'html.parser')
                if localArgs.htmlparse:
                    parseDict = create_dict(localArgs.htmlparse)
                    webWords = inputSoup.find(attrs=parseDict).stripped_strings
                else:
                    webWords = inputSoup.stripped_strings
                webWords = list(line for line in webWords)
                returnWords.extend(webWords)

        except AttributeError:
            error_line = 'HTML attribute <ansired>{}</ansired> not found, check document and try again'
            print_line(error_line.format(localArgs.htmlparse))
            sys.exit()

        except Exception as e:
            print_line('Web error {}'.format(e))
            sys.exit()

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
    parser.add_argument('-i', '--input', type=configargparse.FileType('r'), help='Input text file')
    parser.add_argument('-w', '--webpage', help='Input web URL')
    output_help = 'Output text file: if no name specified, "_{}" is added to either the\
                   input file name or web domain name and a new file is created'.format(file_add)
    parser.add_argument('-o', '--output', type=pathlib.Path, help=output_help)

    # List transformation options
    parser.add_argument('-a', '--alphabetize', action='store_true', help='Alphabetize the list')
    case_help = 'Change the case of words in the list'
    parser.add_argument('--case', choices=['lower', 'upper', 'none'], default='none', help=case_help)
    htmlparse_help = 'Further refines the text from a webpage by narrowing to any HTML entity(ies) specified,\
                      using tag=term syntax (e.g., ID=main_content or class=lyrics). Multiple entities can\
                      be specified'
    parser.add_argument('--htmlparse', action='append', help=htmlparse_help)
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
    parser.add_argument('-s', '--strip', action='store_true', help='Get rid of non-alphabetic characters')

    args = parser.parse_args()

    outputFile = setup_output(args)
    inputWords = setup_input(args)

    # Do any text parsing
    if args.convert is not None:
        inputWords = convert(inputWords, args.convert)

    # Do any text transforms
    if args.strip:
        inputWords = strip_nonalpha(inputWords)

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
