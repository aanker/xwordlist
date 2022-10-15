---
layout: home
title: Help
permalink: /help/
---

The functionality of `xwordlist` can be divided into three categories:
*  [Input and Output](#input-and-output): start with content from your local machine and add more programmatically from the web. Build a list of URLs and crawl multiple pages on the web. Save everything to a file name of your choosing or let the software create one for you.
*  [Content Parsing](#content-parsing): take content from multiple sources and parse it into a normalized list of words. Grab all the words on a web page or limit to one ID, one or more classes and/or one or more HTML tags. Use a regex pattern to get rid of anything you don’t need.
*  [Word Transformation](#word-transformation): refine your list into something you can paste directly into your construction software — alphabetized, deduped, properly cased and with all the extraneous words filtered out.

Although `xwordlist` is a command line tool and all of its key functionality is available via command line options, it is often easier to use the [configuration file](#configuration-file) to enter a set of options before running the program with fewer or no command line options. Many of the [recipes provided on this site](/resources/#recipes) include options that you can paste directly into your configuration file to grab data off websites and start building word lists.

## Basic Example

The easiest way to understand `xwordlist` is to walk through the example of getting a list of song titles, something you might want to do if you are building a themed puzzle about a particular musician. In this case, we’ll be grabbing a list of songs by Tom Petty from [this page on SongLyrics](https://www.songlyrics.com/tom-petty-lyrics/):

To see what raw output looks like, we’ll first just get the whole page without any refinement:

```
python3 xwordlist.py --webpage https://www.songlyrics.com/tom-petty-lyrics/
```

After running this command, you should see a new file called `songlyrics_com_xwl.txt` in your `xwordlist` folder. Since no output file name was specified, a default based on the URL was created. Open the file with your favorite text editor and you will see that we have generated a file with all of the text strings from the SongLyrics web page, including random bits of page titles, navigation and advertising verbiage.

That is a good start, but now let’s just grab the text from the table in the middle with the title “Tom Petty Lyrics - by Popularity” which includes the list of song titles we are looking for. By examining the HTML of the page, we see that the text is contained in a table with the class name “tracklist”, which we can specify using the `--container` option. Next try the command:

```
python3 xwordlist.py --webpage https://www.songlyrics.com/tom-petty-lyrics/ --output tompetty.txt --container class=tracklist=1 --webextract html-a
```

Rather than let a default file be created, this time we have specified that the output should go to `tompetty.txt`; open that file to see the result. You may have noticed that when we specified the `--container` option, we included `class=tracklist=1`. If we had specified an ID, it would have to be unique to the page but there can be multiple uses of the same class name on a page and in this case, we wanted the first. If we had left out the `=1` on the end, `xwordlist` would have given us all of the instances of that class on the page. Try it to see what different outputs look like!

The list of song names is numbered, which is not something we want for our word list. By using `--webextract html-a`, we ask the software to further refine our query to only give us text within `<a>` tags, which very nicely contains each song title but not the numbers. If for some reason we wanted multiple tags — say for instance all the content that is either bolded or italicized — we could have specified `--webextract html-i_b_em_strong` which would include all of the text within `<i> <b> <em> <strong>` tags. Chain as many HTML tags as you need by separating them with the underscore character.

Now that we have a list of song titles, there are a few bits of clean up since most of these kinds of lists can be a bit noisy. For instance, this list of songs by Tom Petty includes multiple versions of the same song with additional words that we may not want for our final word list. First, we should alphabetize it to make it easier to scan. Rather than go back to the web, we’ll use the file we just created:

```
python3 xwordlist.py --input tompetty.txt --output tompetty.txt --alphabetize
```

Of course, you could save the alphabetized list to a different file name (or let the software create a new file) but for the purposes of this example, we will stick with the same file. Scan through that file and delete duplicates and anything that you wouldn’t want in your word list. Don’t worry about extraneous characters — like for instance the apostrophe on the end of Free Fallin’ — the software will clean that up. Once you have made any edits to that file, be sure to save it before continuing on to the next step.

From here, there are two ways we can go with this list. We may want to create a list where the entire song name is an entry, for instance for long themed entries such as “WONTBACKDOWN”. To do that, we need to strip out all non-alphabetic characters (including spaces) and dedupe the list. So first run this:

```
python3 xwordlist.py --input tompetty.txt --output tompetty_songs.txt --strip --dedupe --case upper --alphabetize
```

We saved this to a new file name for reasons that will become obvious in a second. Go open that new file `tompetty_songs.txt` and you will see a list of Tom Petty songs that are ready to be imported into your crossword construction software. But since most of these are long titles that are hard to fit into a standard crossword, we also want the individual words: for instance just the word “BREAK” to clue as “___ Down” for a shorter entry. To do that, we need to add the `--convert` option on our original list which will separate each title’s words into a new list. Try:

```
python3 xwordlist.py --input tompetty.txt --output tompetty_title_words.txt --convert --strip --dedupe --case upper --alphabetize --minimum
```

You now have two great lists to use to start building your Tom Petty puzzle! You can paste them into one doc and have `xwordlist` alphabetize and dedupe or you can just paste each individual list directly into your construction software, perhaps to score one set of words higher than the other. Experiement and figure out what works best for your constructing needs.

Also, check out the [recipes page](/resources/#recipes) for other possibilities. You can use the software to grab and convert the lyrics from individual songs, spider all of the songs at once or parse Wikipedia for album titles. Let us know what you find!

## List of Available Options

Each option below is shown as would be specified on the command line. To use as an option in the configuration file, you do not have to enter the dashes (i.e., `--input filename.txt` on the command line but `input filename.txt` in the configuration file.)

The order that options are specified in does not matter, the software knows the right order to take these operations so they don’t conflict with each other.

### Input and Output

`xwordlist` only works with text files, if it is given binary data it will let you know and then quit.

#### **--input** or **-i** filename.txt
Use the text file named `filename.txt` as an input for the parsing and transformation engine. If you specify other input sources (such as `--webpage` and `--urllist`), all will be added together before processing by the parsing and transformation engine.

#### **--webpage** or **-w** URL
Use the web page located at the address named by the URL as an input into the parsing and transformation engine. The software will grab all of the available text strings from the web page, unless other options are specified to narrow the request down (see `--container` and `--webextract` for more information). The URL should be the fully qualified address, including `http://` or `https://`. The software does not support authenticated sites.

If you specify other input sources (such as `--input` and `--urllist`), all will be added together before processing by the parsing and transformation engine.

#### **--urllist** filename.txt
Read the text file named `filename.txt` and loop through each of the URLs to find input for the parsing and transformation engine. This option functions the same as running the program multiple times using the `--webpage` option for each entry in `filename.txt`.

To work effectively, you should limit the URLs to the same site (or multiple sites with the same HTML structure) so that the software is able to parse the HTML consistently for each URL. Although you can specify multiple URLs, the text parsing and conversion options will act the same on everything retrieved.

The program pauses 20 seconds between each URL requested to be a good citizen and avoid getting blocked. To change this delay, see the [Changing Global Settings](#changing-global-settings) section below. If you specify other input sources (such as `--input` and `--webpage`), all will be added together before processing by the parsing and transformation engine.

#### **--output** or **-o** filename.txt
Save the list of words output by the parsing and transformation engine to the file named `filename.txt`. If you do not specify an output file name, a file will be created for you based on either the input file name or the domain name of the input web address plus the string `_xwl`. To change this string, see the [Changing Global Settings](#changing-global-settings) section below.

Your input and output files can be the same, the software will always prompt you before writing over an existing file.

#### **--directory** /path/to/folder
Set a directory to use for all input and output files. The software will look in the directory specified for files named in the `--input` and `--urllist` options and will write any file specified by the `--output` option (or the default file if no output is specified) to this directory.

For all inputs and outputs you can also specify a path as part of a file name as in `--input /path/to/wordlist.txt`.

## Content Parsing

#### **--container** tag=name
Limit the content read from web page(s) specified by either `--webpage` or `--urllist` to a particular HTML `id` or `class` tag. You must specify both the tag and the name of the element requested, for example `--container id=page_content` or `--container class=wikitable`.

Since the `id` tag must be unique on a properly structured HTML page, specifying an `id` element will return a single container. To specify a single instance of a `class` attribute, add `=N` which will only grab the Nth time that label appears on the page. For example, `class=tracklist=1` will retrieve the first instance of the tracklist `class` on a page. If you leave out the `=N` attribute, the software will grab all instances of that `class`. 

#### **--webextract** text (default) | links | html-XX
Specify what kind of content to grab from web pages. The default is `text` and for most web pages you will not need to use this option at all.

Use the `links` option when you want to retrieve URLs from a web page, for instance to build a text file of URLs to then feed to the `--urllist` option. `links` only returns URLs specified by `<a>` tags, it parses out the values located in the `href` element. If it finds relative URLs, it builds fully-qualified links based on the page’s URL.

Use the `html-XX` to further refine which text to pull from a web page by limiting to only text within specified tags. For instance, use `html-b` to only return text inside all `<b>` and `</b>` blocks. You can chain multiple tags by separating them with the underscore character, for example `html-i_em` will get all content in either `<i>` or `<em>` blocks.

#### **--regex** pattern
Refine which text to keep by using regex patterns. Whereas other options such as `--container` or `--webextract` will grab all of the text within whatever containers and/or elements specified, `--regex` allows you to narrow down to particular parts of text strings to keep. For examples of patterns to use, see regex examples. (*TK: regex examples*)

#### **--convert** "chars" (optional)
Take any block of text and turn it into a list of words. If `"chars"` is not specified, the software uses spaces to separate text into words and in most cases, that will suffice. If you do need to specify `"chars"`, put all characters to be used as delimiters inside the quotes. For instance, if you want to separate text blocks connected by either dashes or spaces, you would use `--convert "- "`.

## Word Transformation

#### **--alphabetize** or **-a**
Alphabetize the list of words.

#### **--case** none (default) | lower | upper
Change the case of all words in the list.

#### **--dedupe** or **-d** nocase (default) | bycase
Remove all duplicates in the list. The dedupe function by default is case insensitive: "apple" and "APPLE" are treated as the same word and the first instance found is kept. Use `--dedupe bycase` if you want the dedupe routine to be case sensitive.

#### **--minimum** or **-m** N
Remove all words with less than `N` characters. By default, `N` is 3 and for most crossword puzzle word lists, simply specifying `--minimum` or `-m` will be sufficient.

#### **--strip** or **-s**
Remove all non-alphabetic characters, to make your list crossword puzzle ready. (*TK: Add more flexibility on this setting*)

## Configuration File

`xwordlist` will also look for a configuration file named `xwordlist.conf` located in the same directory as the main Python program. For the word transformation options, you may want to store your preferences in the configuration file to save having to enter them on the command line each time.

The `xwordlist.conf` that is provided when you download from GitHub includes a commented out example of the format for each option. The format is the same as the command line options described above, but the dashes (`-` or `--`) are not necessary:
 
```
# options that take an argument:
case upper

# options that don’t take an argument:
alphabetize
```
Options entered on the command line take precedence over the configuration file. So for instance, set your default in the configuration file for `case upper` but then override it with `--case none` when you’re requesting links and don’t want to change the case of URLs. It is recommended that you specify your most important defaults (for example `directory`) in the configuration file and leave the inputs and outputs to the command line — but YMMV.

Many of the [recipes provided on this site](/resources/#recipes) include options that you can paste directly into your configuration file to grab data off websites and start building word lists.

### Changing Global Settings

The configuration file also includes global settings that are user editable:

*  `urllist_delay`:  the number of seconds between web page requests when you specify a list of URLs using the `--urllist` option. If you set this too low, you run the danger of looking like a bot and getting blocked by the website. Default setting: `20`

*  `file_add`:  the string added when a new output file needs to be created but no name is specified by the user. For instance, if the input file is `tompetty.txt` and `file_add` is set to `xwl`, the output file created will be named `tompetty_xwl.txt`. Default setting: `xwl`
