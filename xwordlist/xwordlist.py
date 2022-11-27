#!/usr/bin/env python3

import argparse
import os
import sys
import pathlib
import urllib.parse
import time

from . import xwl
from .xwlconfig import __version__, FILE, IMPACT_COLOR, init_config
from prompt_toolkit import prompt, print_formatted_text, HTML


def print_line(printText, argument={}, endText='\n'):
    print_formatted_text(HTML(printText.format(**argument, color=IMPACT_COLOR)), end=endText)
    return


def create_dict(localAttrs):
    returnDict = {}
    for attr in localAttrs:
        dict_parts = attr.split('=')
        # See if it is a class dictionary, in which case we make a tuple
        if dict_parts[0] == 'class':
            numParts = int(dict_parts[2]) if len(dict_parts) == 3 else 0
            returnDict[dict_parts[0]] = (dict_parts[1], numParts)
        else:
            returnDict[dict_parts[0]] = dict_parts[1]
    if len(returnDict) > 0:
        return returnDict
    else:
        print_line('Exiting... something is wrong with your --container setting')
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
    file_add = otherArgs['file_add'] if 'file_add' in otherArgs else otherArgs['globals']['file_add']

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
        webScrape = xwl.WebExtract(parseDict, localArgs.webextract)
        webScrape.pull_data(localArgs.webpage)
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
                webScrape = xwl.WebExtract(parseDict, localArgs.webextract)
                webScrape.pull_data(oneUrl)
                returnWords.extend(webScrape.returnWords)
                if urlCount < urlLength:
                    delay = int(otherArgs['urllist_delay'])
                    print_line('  ...done ...sleeping {delay} seconds', {'delay': delay})
                    time.sleep(delay)
                else:
                    print_line('  ...done')

    if len(returnWords) == 0:
        print_text = 'No input given, nothing to do (enter <{color}>{exec_name} -h</{color}> for help)'
        print_line(print_text, {'exec_name': FILE['name']})
        sys.exit()

    return returnWords


def do_word_options(localWords, localArgs, defaultArgs):
    thatOption = ''
    if localArgs.line2word and localArgs.word2word:
        print_text = 'Options <{color}>line2word</{color}> and <{color}>word2word</{color}>'
        print_text += ' are mutually exclusive, please use either but not both'
        print_line(print_text)
        sys.exit()
    elif localArgs.word2word:
        # If word2word we first do a convert
        localWords.convert(defaultArgs['convert'])
        thatOption = 'word2word'
    # Now run through all the other options
    optionList = ['strip', 'minimum', 'case', 'dedupe', 'alphabetize']
    for option in optionList:
        getattr(localWords, option)(defaultArgs[option])

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
    # First read config file and set up defaults
    defArgs = init_config()
    global IMPACT_COLOR
    IMPACT_COLOR = defArgs['globals']['impact_color']

    # First set up configargparse
    parser = argparse.ArgumentParser(description='Crossword puzzle word list builder')

    # Meta options
    parser.add_argument('-v', '--version', action='version', version=f"{FILE['name']} {__version__}")

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

    webextract_help = 'Specify what to extract from web inputs '
    webextract_help += f"[ text | links | html-XX ] - DEFAULT: {defArgs['defaults']['webextract']}"
    parser.add_argument('--webextract', nargs='?', default=defArgs['defaults']['webextract'], help=webextract_help)

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

    convert_help = 'Convert a block of text into individual words, separating words by spaces '
    parser.add_argument('--convert', nargs='?', const=defArgs['defaults']['convert'], help=convert_help)

    alphabetize_help = 'Alphabetize the list '
    alphabetize_help += f"[ normal | reverse ] - DEFAULT: {defArgs['defaults']['alphabetize']}"
    parser.add_argument('-a', '--alphabetize', nargs='?', const=defArgs['defaults']['alphabetize'], help=alphabetize_help)

    case_help = 'Change the case of words in the list '
    case_help += f"[ upper | lower | none ] - DEFAULT: {defArgs['defaults']['case']}"
    parser.add_argument('--case', nargs='?', const=defArgs['defaults']['case'], help=case_help)

    dedupe_help = 'Remove duplicates from the word list '
    dedupe_help += f"[ nocase | bycase ] - DEFAULT: {defArgs['defaults']['dedupe']}"
    parser.add_argument('-d', '--dedupe', nargs='?', const=defArgs['defaults']['dedupe'], help=dedupe_help)

    minimum_help = f"Minimum number of letters in a word - DEFAULT: {defArgs['defaults']['minimum']}"
    parser.add_argument('-m', '--minimum', nargs='?', const=defArgs['defaults']['minimum'], help=minimum_help)

    strip_help = 'Remove non-alphabetic characters '
    strip_help += f"[ diacritic | keepdiacritic ] - DEFAULT: {defArgs['defaults']['strip']}"
    parser.add_argument('-s', '--strip', nargs='?', const=defArgs['defaults']['strip'], help=strip_help)

    confArgs = parser.parse_args()

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
    outputFile = setup_output(confArgs, defArgs)
    try:
        inputWords = xwl.WordList(myList=setup_input(confArgs, defArgs['globals']))

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
            inputWords, thatOption = do_word_options(inputWords, confArgs, defArgs['defaults'])
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
        (err_info, ) = e.args
        if 'arg' in err_info:
            arg = f"<{IMPACT_COLOR}>{err_info['arg']}</{IMPACT_COLOR}>"
            print_formatted_text(HTML(err_info['error'].format(arg)))
        else:
            print_formatted_text(HTML(err_info['error']))
        sys.exit()

    # Now save the file
    save_output(outputFile, inputWords)


if __name__ == '__main__':
    main()
