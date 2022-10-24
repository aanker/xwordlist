# xwordlist

`xwordlist` is a command line Python program designed to help you create, build and organize crossword puzzle word lists. As I started to think about constructing crossword puzzles with heavy themes — trying to make the entire puzzle themed, not just three or four long entries — I realized that I would need the ability to acquire and organize large amounts of text on very specific topics. After hacking around with a combination of search-and-replace text editors and Excel, I realized I needed to build someting more custom and thus `xwordlist` was born. 

Besides helping with basic text functions such as deduping, alphabetizing and changing case, this program is able to pull content out of structured web pages and parse large blocks of text, including lists of web pages with similarly structured content. Although I first started using the software to grab the lyrics of songs, I have added regex and better html parsing functionality to make it easier to get data from Wikipedia and less structured sites.

For more information, see the project’s main website hosted at [xwl.ist](https://xwl.ist). For an example of a themed 5x5 mini puzzle built with a word list assembled using this software, see [my personal website](https://quid.pro/xwords/tom-petty-mini/).

## Installation

It helps to have some familiarity with Python and terminal programs to install `xwordlist` but it is not a requirement. If your environment is all set up and you know `pip` is both installed and up-to-date, skip down to the `pip` instructions below. Most Macs and Linux users will find that `pip` is installed but probably needs to be updated. Most Windows users will need to install `pip` first. In other words, unless you really know what you are doing, you probably need to continue to follow the next paragraph.

On either Mac or Windows, search for `terminal` and your operating system should show you the name and how to launch your default terminal program. The first thing you will need to do is make sure your Python is up-to-date (required) and that you have activated a virtual environment (recommended). See [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) for helpful instructions on how to do both as well as how to install and upgrade `pip`. Follow the instructions on that page down to the section labeled *Installing from PyPI*.

SPECIAL NOTE:  I just started testing this on Windows and have noticed big differences in how the software works (short answer, much less well than on Mac/Linux). If you are a Windows user, it may be a bit early to use this software.

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

To install the software manually, copy the `xwordlist` code to your local working environment by either cloning this repository or downloading and unpacking the [zip archive](https://github.com/aanker/xwordlist/archive/refs/heads/main.zip) into a new directory. To install the dependencies required to make `xwordlist` work, use your terminal program to find the directory in which you have copied the files and type

```
python3 -m pip install -r requirements.txt
```
To see if your installation was successful, type
```
python3 xwordlist.py --version
```
If properly installed, the software should respond with its name and the installed version.

## Usage

If you have installed the software using `pip`, you should be able to run the program by simply typing `xwordlist` or `xwl`. For manual installs, you will need to type `python3 xwordlist.py`. The rest of the documentation assumes you have installed via `pip` and uses the short form.

For quick help instructions on the command line, type
```
xwordlist --help
```
Please see the [project’s main website](https://xwl.ist) for more information about using the software including a [basic example](https://xwl.ist/help/#basic-example), [recipes for common patterns](https://xwl.ist/resources/#recipes) and a [reference](https://xwl.ist/help/#list-of-available-options) to all options.

Find a bug? Please let us know [here](https://github.com/aanker/xwordlist/issues).

## License

This software is available as open source under the terms of the [MIT License](http://opensource.org/licenses/MIT).
