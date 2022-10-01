# wordfab
`wordfab` is a command line Python program designed to help you create, build and organize crossword puzzle word lists. Besides helping you with basic functions such as deduping, alphabetizing and changing case, it is also able to pull text out of structured web pages or large blocks of text, including lists of pages with similar content — for instance, the lyrics of songs from a particular artist.

## Installation
For now, you are on your own if you wish to install `wordfab` (this is still an early stage project). You can clone the repository, install the dependencies and type `python wordfab.py`. If you need more instructions than that, you might be better off waiting until the project is further along. (*TK:  Add pip install*)

## Usage

For quick help instructions on the command line, type
```
python wordfab.py --help
```

### Input and Output

`wordfab` accepts three types of non-mutually exclusive inputs:
*  Text file:  `--input [filename.txt]` or `-i [filename.txt]`
*  Web URL:  `--webpage [URL]` or `-w [URL]`
*  Text file with list of web URLs:  `--urllist [filename.txt]`

If multiple inputs are specified, the contents of each source are added together. For instance, you can use your base word list as an input file and then add the contents of a web page by entering

```
python wordfab.py --input tompettywords.txt --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/
```

A file with a list of web URLs should contain one URL per line: it otherwise functions the same as running the program multiple times using the `--webpage` option. To work effectively, you should limit the URLs to the same site so that `wordfab` is able to parse the HTML consistently (see Content Parsing below).  In addition, the program pauses 20 seconds between each web request to be a good citizen and avoid getting blocked. (*TK:  Make this a user setting*)

You can specify the output file name with the command line option `--output [filename.txt]` or `-o [filename.txt]`. If you do not specify an output file name, a file will be created for you based on either the input file name or the domain name of the web URL plus the string `_fab` (*TK:  Make this a user setting*). Your input and output files can be the same but `wordfab` will always prompt you before writing over an existing file.

`wordfab` only works with text files, if it is given binary data it will let you know and then quit. For all inputs and outputs you can specify a path as part of a file name as in `--input /Users/aa/wordlist.txt` or use the `--directory /Users/aa/` argument to set a default path for all inputs and outputs.

### Content Parsing

The most useful content extraction tool in `wordfab` is its ability to pull content out of structured web pages. When given a web URL (or text file with a list of web URLs), by default `wordfab` will return an output file with all of the text on the web page(s). More useful is to only grab specific parts of the page, which you can do using the `--htmlparse` option. For instance, if you wish to get the lyrics to a song on the website [SongLyrics](http://songlyrics.com), you only need the content inside the HTML element with the ID “songLyricsDiv”.

```
python wordfab.py --webpage http://www.songlyrics.com/tom-petty/free-falling-lyrics/ --htmlparse id=songLyricsDiv
```

The `--htmlparse` option also works on classes (as in`class=XX`). To grab URLs instead of text, just set the additional option `--webextract links`. You can use the link extraction functionality to build your file of URLs that you then use to grab multiple text blocks. For instance, to grab a list of URLs for all of the songs by Tom Petty on SongLyrics, try

```
python wordfab.py --webpage http://www.songlyrics.com/tom-petty-lyrics/ --htmlparse class=tracklist --webextract links
```

Then take the file created and feed it back to grab all of the song lyrics by entering
```
python wordfab.py --urllist tom_petty_links.txt --htmlparse id=songLyricsDiv --webextract text
```
Note that you don’t need to add the `--webextract text` as that is the default for web extraction. Also note that you should go through the file of URLs before you ask `wordfab` to grab all of that content; you will find that there is a lot of duplication and you probably don’t need all of the URLs. `wordfab` works best hand in hand with your text editor of choice (I prefer Sublime Text personally).

Using the above content parsing options will provide you with lines of text which is probably not what you ultimately want for a word list. The next option to use is `--convert` which takes any block of text and turns it into a list of words. The default if you don’t specify anything is to use spaces as delimiters but you can ask `wordfab` to use additional characters as deliminters by adding them in quotes. For instance, `--convert " ;-,"` will separate words connected by spaces, semi-colons, dashes and commas.

Usually when you are pulling content from web pages, the default behavior for `--convert` is fine and you won’t need to use other delimiters. But to build a word list for crossword construction, you will want to remove all of those additional non-alphabetic characters. To do that, use `--strip` or `-s` which gets rid of everything (including numbers) that you would not want in your word list. (*TK: Add more flexibility on this setting*)

You may decide when you are pulling large amounts of content down that you want to take each step at a time to make sure you’re not getting junk data — in fact, at least until you have done some trial runs that is highly recommended! But `wordfab` knows the right order to take these operations so they don’t conflict with each other and you can chain multiple items at once. To come back to our list of links of Tom Petty songs, you could do the following and end up with a word list in one shot:

```
python wordfab.py --urllist tom_petty_links.txt --htmlparse id=songLyricsDiv --webextract text --convert --strip
```

### Word Transformation

With any list of words derived from a public source such as a lyrics database, you will want a few more items that are relatively self explanatory.

*  Dedupe:  `--dedupe` or `-d`
*  Alphabetize:  `--alphabetize` or `-a`
*  Change case:  `--case lower | upper`
*  Minimum word length:  `--minimum X` or `-m X`

You should always change case to either lower or upper as part of deduping because the deduping routine is case sensitive. Also, the default minimum word length is 3 letters so if you’re happy with that (as most crosswords are), just `-m` without any additional number will screen out any word smaller than 3 letters.

To bring it all home, the following command line along with the list of links we built above should give you a fully parsed, alphabetized, deduped, crossword ready list of words from Tom Petty’s oeuvre:

```
python wordfab.py --urllist tom_petty_links.txt --htmlparse id=songLyricsDiv --webextract text --convert --strip --dedupe --alphabetize --case upper --minimum
```

The order of options entered on the command line doesn’t matter, `wordfab` does everything in the most logical order. To simplify the above (and get rid of options that are defaults and don’t need to be specified), you could also enter:

```
python wordfab.py --urllist tom_petty_links.txt --htmlparse id=songLyricsDiv --convert -sdam --case upper 
```

## Configuration File

`wordfab` will also look for a configuration file named `wordfab.conf` located in the same directory as the main Python program. For the word transformation options, you may want to store your preferences in the configuration file to save having to enter them on the command line each time. One configuration option per line, but you can enter each setting in any one of a number of different ways:

```
# options that take an argument:
case upper
case = upper
case: upper
--case upper

# options that don’t take an argument:
--dedupe
dedupe
dedupe = True

# options that can have multiple items
htmlparse = [id=songLyricsDiv, class=linkList]
```
Options entered on the command line take precedence over the configuration file. So for instance, set your default in the configuration file for `case upper` but then override it with `--case none` when you’re requesting links and don’t want to change the case of URLs. It is recommended that you specify your most important defaults (for example `directory`) in the configuration file and leave the inputs and outputs to the command line — but YMMV.

The `wordfab.conf` file included with the GitHub repository contains commented out examples of the usage of each option.
