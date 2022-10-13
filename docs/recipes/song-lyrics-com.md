---
layout: recipes
title: SongLyrics
title_url: http://songlyrics.com
permalink: /recipes/song-lyrics
---

### To get list of URLs of songs by an artist

We suggest alphabetizing the list to look for duplicates or similar titles. For instance, often the same song will appear both in its studio and live versions with essentially the same lyrics: there is probably no reason to grab the text from both. You can use this list of URLs to get all the lyrics by an artist using the last recipe on this page.

```
webpage http://www.songlyrics.com/[artist]-lyrics/                      ; customize
container class=tracklist=1
webextract links
alphabetize
```

### To get list of songs

The options below will get you a list of songs with spaces removed between words for long entries like “MARYJANESLASTDANCE”. To get a list of titles with spaces (e.g., “MARY JANES LAST DANCE”) leave out the `strip` option. To get the song titles converted into a word list (e.g., “MARY”, “JANES”, “LAST”, “DANCE”), add the `convert` option.
```
webpage http://www.songlyrics.com/[artist]-lyrics/                      ; customize
container class=tracklist=1
webextract text
strip
dedupe
alphabetize
case upper
```

### To get song lyrics

Use the recipe below to get the lyrics from a single song. 

```
webpage http://www.songlyrics.com/[artist]/[song-name]-lyrics/          ; customize
container id=songLyricsDiv
webextract text
convert
strip
dedupe
alphabetize
case upper
```

To get the lyrics from all songs by an artist, run the first recipe to get a file with a list of URLs and then use the recipe below.

```
urllist [urlfile.txt]                                                   ; customize
container id=songLyricsDiv
webextract text
convert
strip
dedupe
alphabetize
case upper
```
