#!/usr/bin/python3

import argparse
import os
import sys

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


def strip_nonalpha(wordList):
    newList = []
    for word in wordList:
        newWord = ''.join([i for i in word if i.isalpha()])
        if len(newWord) > 0:
            newList.append(newWord)
    return newList


def upper(wordList):
    return list(line.upper() for line in wordList)


def lower(wordList):
    return list(line.lower() for line in wordList)


def uniquify(wordList):
    return list(dict.fromkeys(wordList))


def alphabetize(wordList):
    return sorted(wordList, key=str.casefold)


def main():
    # First set up argparse
    parser = argparse.ArgumentParser(description='Fabulous word list builder')

    # Input and output options
    parser.add_argument('-i', '--input', type=argparse.FileType('r'), help='Input text file')
    output_help = 'Output text file: if no name specified, "_{}" is added\
                   to input file name and a new file is created'.format(file_add)
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help=output_help)

    # List transformation options
    parser.add_argument('-a', '--alphabetize', action='store_true', help='Alphabetize the list')
    convert_help = 'Converts a block of text to a word list. Default delimiter is a space but acccepts\
                    any number of characters in quotes (e.g., -c " ;," will separate words delimited\
                    by a space, comma or semicolon). Be careful with back slashes acting as an escape char'
    parser.add_argument('--convert', nargs='?', const=' ', help=convert_help)
    dedupe_help = 'Remove duplicates from the list. Note that this is case sensitive so always\
                    recommended that you also use -l or -u to put everything in the same case first'
    parser.add_argument('-d', '--dedupe', action='store_true', help=dedupe_help)
    parser.add_argument('-l', '--lower', action='store_true', help='Make all words lower case')
    parser.add_argument('-u', '--upper', action='store_true', help='Make all words upper case')
    parser.add_argument('-s', '--strip', action='store_true', help='Get rid of non-alphabetic characters')

    args = parser.parse_args()

    # Set up necessary vars
    input_flag = False
    transform_flag = False

    # Load input(s)
    if args.input:
        try:
            inputWords = list(line.strip() for line in args.input)
            inputName = args.input.name
            args.input.close()
            input_flag = True

        except UnicodeDecodeError:
            print('Sorry, only text files accepted')
            sys.exit()

        except Exception as e:
            print('error {}'.format(e))
            sys.exit()

    if not input_flag:
        print('No input given, nothing to do')
        sys.exit()

    # Do any text parsing
    if args.convert is not None:
        inputWords = convert(inputWords, args.convert)
        transform_flag = True

    # Do any text transforms
    if args.strip:
        inputWords = strip_nonalpha(inputWords)
        transform_flag = True

    if args.dedupe:
        inputWords = uniquify(inputWords)
        transform_flag = True

    if args.upper:
        inputWords = upper(inputWords)
        transform_flag = True

    if args.lower:
        inputWords = upper(inputWords)
        transform_flag = True

    if args.alphabetize:
        inputWords = alphabetize(inputWords)
        transform_flag = True

    # Now save the file
    if transform_flag:
        if args.output:
            saveFile = args.output
        else:
            filetup = os.path.splitext(inputName)
            saveFile = open('{}_{}{}'.format(filetup[0], file_add, filetup[1]), 'w')

        for line in inputWords:
            saveFile.write('{}\n'.format(line))
        print('New word list saved to {}'.format(saveFile.name))
        saveFile.close()

    elif not transform_flag:
        print('Nothing to write, no changes made')
        sys.exit()


if __name__ == '__main__':
    main()
