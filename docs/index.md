---
layout: home
title: 'Software for Building Puzzle Word Lists'
---

`xwordlist` is a [command line Python program](https://github.com/aanker/xwordlist) designed to help you create, build and organize crossword puzzle word lists. As I started to think about constructing crossword puzzles with heavy themes — trying to make the entire puzzle themed, not just three or four long entries — I realized that I would need the ability to acquire and organize large amounts of text on very specific topics. After hacking around with a combination of search-and-replace text editors and Excel, I realized I needed to build someting more custom and thus `xwordlist` was born. 

Besides helping with basic text functions such as deduping, alphabetizing and changing case, this program is able to pull content out of structured web pages and parse large blocks of text, including lists of web pages with similarly structured content. Although I first started using the software to grab the lyrics of songs, I have added regex and better html parsing functionality to make it easier to get data from Wikipedia and less structured sites.

For an example of a themed 5x5 mini puzzle built with a word list assembled using this software, see [my personal website](https://quid.pro/xwords/tom-petty-mini/).

## Installation

It helps to have some familiarity with Python and terminal programs to install `xwordlist` but it is not a requirement. If your environment is all set up and you know `pip` is both installed and up-to-date, skip down to the `pip` instructions below. Most Macs and Linux users will find that `pip` is installed but probably needs to be updated. Most Windows users will need to install `pip` first. In other words, unless you really know what you are doing, you probably need to continue to follow the next paragraph.

On either Mac or Windows, search for `terminal` and your operating system should show you the name and how to launch your default terminal program. The first thing you will need to do is make sure your Python is up-to-date (required) and that you have activated a virtual environment (recommended). See [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) for helpful instructions on how to do both as well as how to install and upgrade `pip`. Follow the instructions on that page down to the section labeled *Installing from PyPI*.

From there, you can install `xwordlist` by typing

```
pip install xwordlist
```
Be sure to type `xwordlist` as there is other software called `wordlist` (without the “x”) which is not what you want. To see if your installation was successful, type
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

### Configuration File

`xwordlist` will also look for a configuration file named `xwordlist.conf` located in either the same directory as the main Python program or in a folder in the user’s home directory (`~/xwordlist`). For the word transformation options, you may want to store your preferences in the configuration file to save having to enter them on the command line each time.

Options entered on the command line take precedence over the configuration file. So for instance, set your default in the configuration file for `case upper` but then override it with `--case none` when you’d rather look at raw text. It is recommended that you specify your most important defaults in the configuration file and leave the inputs and outputs to the command line — but YMMV.

The `xwordlist.conf` file included in the GitHub repository contains commented out examples of the usage of each option. 

For more information about setting configuration options, see the [expanded help page](/help). Also, be sure to check out the various [recipes pages](/resources/#recipes) which provide options you can paste directly into your configuration file to do common activities.

## License

This software is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
