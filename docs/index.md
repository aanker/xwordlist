---
layout: home
---
`xwordlist` is a command line Python program designed to help you create, build and organize crossword puzzle word lists. As I started to think about constructing crossword puzzles with heavy themes — trying to make the entire puzzle themed, not just three or four long entries — I realized that I would need the ability to acquire and organize large amounts of text on very specific topics. After hacking around with a combination of search-and-replace text editors and Excel, I realized I needed to build someting more custom and thus `xwordlist` was born. 

Besides helping you with basic text functions such as deduping, alphabetizing and changing case, this program is also able to pull content out of structured web pages or parse large blocks of text, including lists of pages with similar content. Although I first started using the software to grab the lyrics of songs from a particular musician, I have added regex and better html parsing functionality to make getting data from Wikipedia and less structured sites a bit more possible.

## Installation
This is still an early stage project that may change often, I am not yet worrying when I change apis or update the functionality in fundamental ways. Use at your discretion!

For now, you are mostly on your own if you wish to install `xwordlist`. After making sure your python is up-to-date and you have activated a virtual environment (see [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/) for helpful instructions on that), you can copy the `xwordlist` code to your local working environment by either cloning [the repository](https://github.com/aanker/xwordlist) or downloading the [zip archive](https://github.com/aanker/xwordlist/archive/refs/heads/main.zip). To install the dependencies required to make `xwordlist` work, use your terminal program to find the directory in which you have copied the files and type
```
python3 -m pip install -r requirements.txt
```
To run the program, type
```
python3 xwordlist.py
```
If you need more instructions than that, you might be better off waiting until the project is further along. If you have comments or questions beyond what is provided on this site, please refer to the main [GitHub repository]() and feel free to open an [issue](https://github.com/aanker/xwordlist/issues) if you have further questions.

## Usage

For quick help instructions on the command line, type
```
python xwordlist.py --help
```

### Input and Output

`xwordlist` accepts three types of non-mutually exclusive inputs:
*  Text file:  `--input [filename.txt]` or `-i [filename.txt]`
*  Web URL:  `--webpage [URL]` or `-w [URL]`
*  Text file with list of web URLs:  `--urllist [filename.txt]`

If multiple inputs are specified, the contents of each source are added together. For instance, you can use your base word list as an input file and then add the contents of a web page by entering

```
python xwordlist.py --input tompettywords.txt --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/
```

You can specify the output file name with the command line option `--output [filename.txt]` or `-o [filename.txt]`. If you do not specify an output file name, a file will be created for you based on either the input file name or the domain name of the web URL. Your input and output files can be the same but `xwordlist` will always prompt you before writing over an existing file.

For more information about using a text file with a list of web URLs and setting a default directory, see the [expanded help page](/help).

### Content Parsing

The most useful content extraction tool in `xwordlist` is its ability to pull content out of structured web pages. When given a web URL (or text file with a list of web URLs), by default `xwordlist` will return an output file with all of the text on the web page(s). More useful is to only grab specific parts of the page, which you can do using the `--container` option. For instance, if you wish to get the lyrics to a song on the website [SongLyrics](http://songlyrics.com), you only need the content inside the HTML element with the ID “songLyricsDiv”.

```
python xwordlist.py --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/ --container id=songLyricsDiv
```

This will provide you with lines of text which is probably not what you ultimately want for a word list. The next option to use is `--convert` which takes any block of text and turns it into a list of words. To make it crossword construction ready, you will also want to remove any non-alphabetic characters using `--strip` or `-s` which gets rid of everything (including numbers) that you would not want in your word list.

For more information about the program’s content parsing ability, including how to target specific html class names or individual tags, see the [expanded help page](/help).

### Word Transformation

With any list of words derived from a public source such as a lyrics database, you will want a few more items that are relatively self explanatory.

*  Dedupe:  `--dedupe` or `-d`
*  Alphabetize:  `--alphabetize` or `-a`
*  Change case:  `--case lower | upper`
*  Minimum word length:  `--minimum X` or `-m X`

You should always change case to either lower or upper as part of deduping because the deduping routine is case sensitive. Also, the default minimum word length is 3 letters so if you’re happy with that (as most crosswords are), just `-m` without any additional number will screen out any word smaller than 3 letters.

The order of options entered on the command line doesn’t matter, `xwordlist` does everything in the most logical order.


### Configuration File

`xwordlist` will also look for a configuration file named `xwordlist.conf` located in the same directory as the main Python program. For the word transformation options, you may want to store your preferences in the configuration file to save having to enter them on the command line each time.

Options entered on the command line take precedence over the configuration file. So for instance, set your default in the configuration file for `case upper` but then override it with `--case none` when you’d rather look at raw text. It is recommended that you specify your most important defaults in the configuration file and leave the inputs and outputs to the command line — but YMMV.

The `xwordlist.conf` file included in the GitHub repository contains commented out examples of the usage of each option. 

For more information about setting configuration options, see the [expanded help page](/help).