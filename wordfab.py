#!/usr/bin/python3

import argparse
import os
import sys

file_add = 'fab'


def upper(wordList):
    return list(line.upper() for line in wordList)


def lower(wordList):
    return list(line.lower() for line in wordList)


def uniquify(wordList):
    return list(dict.fromkeys(wordList))


def alphabetize(wordList):
    return sorted(wordList)


def main():
    # First set up argparse
    parser = argparse.ArgumentParser(description='Fabulous word list builder')

    # Input and output options
    parser.add_argument('input', type=argparse.FileType('r'), help='Input text file')
    output_help = 'Output text file: if no name specified, "_{}" is added\
                   to input file name and a new file is created'.format(file_add)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help=output_help)

    # List transformation options
    parser.add_argument('-a', '--alphabetize', action='store_true', help='Alphabetize the list')
    parser.add_argument('-d', '--dedupe', action='store_true', help='Remove duplicates from the list')
    parser.add_argument('-l', '--lower', action='store_true', help='Make all words lower case')
    parser.add_argument('-u', '--upper', action='store_true', help='Make all words upper case')

    args = parser.parse_args()

    # Set up necessary vars
    transformed = False

    # Load input file
    try:
        inputWords = list(line.strip() for line in args.input)
        inputName = args.input.name
        args.input.close()

    except Exception:
        sys.exit()

    # Do any text transforms
    if args.upper:
        inputWords = upper(inputWords)
        transformed = True

    if args.lower:
        inputWords = upper(inputWords)
        transformed = True

    if args.dedupe:
        inputWords = uniquify(inputWords)
        transformed = True

    if args.alphabetize:
        inputWords = alphabetize(inputWords)
        transformed = True

    # Now save the file
    if transformed:
        if args.output:
            saveFile = args.output
        else:
            filetup = os.path.splitext(inputName)
            saveFile = open('{}_{}{}'.format(filetup[0], file_add, filetup[1]), 'w')

        for line in inputWords:
            saveFile.write('{}\n'.format(line))
        saveFile.close()

    elif not transformed:
        print('Nothing to write, no changes made')


if __name__ == '__main__':
    main()
