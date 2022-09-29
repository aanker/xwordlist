Below are recipes for downloading various types of text and links from different song list and lyric sites. Paste the options in each section into your `wordfab.conf` configuration file, update the URLs for the specifics of what you are trying to parse and run `wordfab`.

## [SongLyrics](http://songlyrics.com)

### To get list of URLs of songs by an artist

It is recommended that you alphabetize the list to look for duplicates or similar titles. For instance, often the same song will appear both in its studio and live versions with essentially the same lyrics. There is no reason to grab the text from both. You can use this list of URLs to get all the lyrics by an artist using the `urllist filename.txt` option below.
```
webpage http://www.songlyrics.com/[artist]-lyrics/
htmlparse class=tracklist
webextract links
alphabetize
```

### To get list of songs

The options below will get you a list of songs with spaces removed between words for long entries like “MARYJANESLASTDANCE”. To get a list of titles with spaces (e.g., “MARY JANES LAST DANCE”) leave out the `strip` option. To get the song titles converted into a word list (e.g., “MARY”, “JANES”, “LAST”, “DANCE”), add the `convert` option.
```
webpage http://www.songlyrics.com/[artist]-lyrics/
htmlparse class=tracklist
webextract text
strip
dedupe
alphabetize
case upper
```

### To get song lyrics
```
webpage http://www.songlyrics.com/[artist]/[song-name]-lyrics/
htmlparse id=songLyricsDiv
webextract text
convert
strip
dedupe
alphabetize
case upper
```

## [LyricsFreak](https://www.lyricsfreak.com)

### To get list of URLs of songs by an artist

It is recommended that you alphabetize the list to look for duplicates or similar titles. For instance, often the same song will appear both in its studio and live versions with essentially the same lyrics. There is no reason to grab the text from both. You can use this list of URLs to get all the lyrics by an artist using the `urllist filename.txt` option below.
```
webpage https://www.lyricsfreak.com/[initial]/[artist+name]/
htmlparse class=lf-list__container
webextract links
alphabetize
```

### To get list of songs

The options below will get you a list of songs with spaces removed between words for long entries like “MARYJANESLASTDANCE”. To get a list of titles with spaces (e.g., “MARY JANES LAST DANCE”) leave out the `strip` option. To get the song titles converted into a word list (e.g., “MARY”, “JANES”, “LAST”, “DANCE”), add the `convert` option.
```
webpage https://www.lyricsfreak.com/[initial]/[artist+name]/
htmlparse class=lf-list__container
webextract text
strip
dedupe
alphabetize
case upper
```
Note: Given how LyricsFreak constructs their list, every song will have the word ”LYRICS“ at the end (e.g., “MARYJANESLASTDANCELYRICS”). In the future, `wordfab` will have the ability to strip out such characters but for now, you should open the list of songs in your favorite text editor and do a search and replace. Also due to the way LyricsFreak structures the HTML, you will also fine a few extra words such as “STARS” and “TIME” in your list of songs. You should delete those by hand.

### To get song lyrics
```
webpage https://www.lyricsfreak.com/[initial]/[artist+name]/[song+name_datecode]
htmlparse id=content
webextract text
convert
strip
dedupe
alphabetize
case upper
```

## Legal Disclaimer

Always read the terms of service first! The inclusion of any site on this wiki does not guarantee that pulling information programmatically is allowed under the site’s terms of service or that you won’t be blocked trying. We make no representations of anything, you’re on your own when use wordfab and when you download data from public websites while using it.
