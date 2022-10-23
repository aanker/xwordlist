---
layout: home
title: 'Software for Building Puzzle Word Lists'
---

`xwordlist` is a [command line Python program](https://github.com/aanker/xwordlist) designed to help you create, build and organize crossword puzzle word lists. As I started to think about constructing crossword puzzles with heavy themes — trying to make the entire puzzle themed, not just three or four long entries — I realized that I would need the ability to acquire and organize large amounts of text on very specific topics. After hacking around with a combination of search-and-replace text editors and Excel, I realized I needed to build someting more custom and thus `xwordlist` was born. 

Besides helping with basic text functions such as deduping, alphabetizing and changing case, this program is able to pull content out of structured web pages and parse large blocks of text, including lists of web pages with similarly structured content. Although I first started using the software to grab the lyrics of songs, I have added regex and better html parsing functionality to make it easier to get data from Wikipedia and less structured sites.

For an example of a themed 5x5 mini puzzle built with a word list assembled using this software, see [my personal website](https://quid.pro/xwords/tom-petty-mini/).

## Installation

It helps to have some familiarity with Python and terminal programs to install `xwordlist` but it is not a requirement. If you are good with all of that, skip down to the `pip` instructions below. Otherwise on either Mac or Windows, search for `terminal` and your operating system should show you the name and how to launch your default terminal program.

The first thing you will need to do is make sure your Python is up-to-date (required) and that you have activated a virtual environment (recommended). See [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) for helpful instructions on how to do both. Follow the instructions down to the section labeled *Installing from PyPI*.

From there, you can install `xwordlist` by typing

```
pip install xwordlist
```
To see if your installation was successful, type
```
xwordlist --version
```
If properly installed, the software should respond with its name and the installed version.

### Manual Installation

To install the software manually, copy the `xwordlist` code to your local working environment by either cloning the [GitHub repository](https://github.com/aanker/xwordlist) or downloading and unpacking the [zip archive](https://github.com/aanker/xwordlist/archive/refs/heads/main.zip) into a new directory. To install the dependencies required to make `xwordlist` work, use your terminal program to find the directory in which you have copied the files and type

```
python3 -m pip install -r requirements.txt
```
To see if your installation was successful, type
```
python3 xwordlist.py --version
```
If properly installed, the software should respond with its name and the installed version.

### Upgrading

As an early stage project, `xwordlist` is likely to be updated often — including new features and bug fixes. For a record of changes and to see the most current version number, see the [changelog](changelog). Remember that you can always check which version you have by typing `xwordlist --version`.

To update your installation using `pip`, type

```
pip install --upgrade xwordlist
```
To upgrade a manual installation, it is best to repeat the installation process replacing old files with the new ones downloaded from GitHub.

## Usage

If you have installed the software using `pip`, you should be able to run the program by simply typing `xwordlist` or `xwl`. For manual installs, you will need to type `python3 xwordlist.py`. The rest of the documentation assumes you have installed via `pip` and uses the short form.

For quick help instructions on the command line, type
```
xwordlist --help
```
For an example of how to use the software as well as a reference to all options, see the [expanded help page](/help).

### Input and Output

`xwordlist` accepts three types of non-mutually exclusive inputs:
*  Text file:  `--input filename.txt` or `-i filename.txt`
*  Web URL:  `--webpage URL` or `-w URL`
*  Text file with list of web URLs:  `--urllist filename.txt`

If multiple inputs are specified, the contents of each source are added together. For instance, you can use your base word list as an input file and then add the contents of a web page by entering

```
xwordlist --input tompettywords.txt --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/
```

You can specify the output file name with the command line option `--output filename.txt` or `-o filename.txt`. If you do not specify an output file name, a file will be created for you based on either the input file name or the domain name of the web URL. Your input and output files can be the same but `xwordlist` will always prompt you before writing over an existing file.

For more information about using a text file with a list of web URLs and setting a default directory, see the [expanded help page](/help).

### Content Parsing

The most useful content extraction tool in `xwordlist` is its ability to pull content out of structured web pages. When given a web URL (or text file with a list of web URLs), by default `xwordlist` will return an output file with all of the text on the web page(s). More useful is to only grab specific parts of the page, which you can do using the `--container` option. For instance, if you wish to get the lyrics to a song on the website [SongLyrics](http://songlyrics.com), you only need the content inside the HTML element with the ID “songLyricsDiv”.

```
xwordlist --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/ --container id=songLyricsDiv
```

This will provide you with lines of text which is probably not what you ultimately want for a word list. The next option to use is `--convert` which takes any block of text and turns it into a list of words. To make it crossword construction ready, you will also want to remove any non-alphabetic characters using `--strip` or `-s` which gets rid of everything (including numbers) that you would not want in your word list.

For more information about the program’s content parsing ability, including how to target specific html class names or individual tags and how to use regex patterns, see the [expanded help page](/help).

### Word Transformation

With any list of words derived from a public source such as a lyrics database, you will want a few more items that are relatively self explanatory.

*  Dedupe:  `--dedupe` or `-d`
*  Alphabetize:  `--alphabetize` or `-a`
*  Change case:  `--case lower | upper`
*  Minimum word length:  `--minimum N` or `-m N`

The dedupe function by default is case insensitive: "apple" and "APPLE" are treated as the same word and the first instance found is kept. Use `--dedupe bycase` if you want the dedupe routine to be case sensitive. Also, the default minimum word length is 3 letters so if you’re happy with that (as most crosswords are), just `-m` without any additional number will screen out any word smaller than 3 letters.

The order of options entered on the command line doesn’t matter, `xwordlist` does everything in the most logical order.

### Configuration File

`xwordlist` will also look for a configuration file named `xwordlist.conf` located in either the same directory as the main Python program or in a folder in the user’s home directory (`~/xwordlist`). For the word transformation options, you may want to store your preferences in the configuration file to save having to enter them on the command line each time.

Options entered on the command line take precedence over the configuration file. So for instance, set your default in the configuration file for `case upper` but then override it with `--case none` when you’d rather look at raw text. It is recommended that you specify your most important defaults in the configuration file and leave the inputs and outputs to the command line — but YMMV.

The `xwordlist.conf` file included in the GitHub repository contains commented out examples of the usage of each option. 

For more information about setting configuration options, see the [expanded help page](/help).

## License

This software is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
