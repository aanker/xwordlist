---
layout: recipes
title: LyricsFreak
title_url: https://www.lyricsfreak.com
permalink: /recipes/lyrics-freak
---

### To get list of URLs of songs by an artist

We suggest alphabetizing the list to look for duplicates or similar titles. For instance, often the same song will appear both in its studio and live versions with essentially the same lyrics: there is probably no reason to grab the text from both. You can use this list of URLs to get all the lyrics by an artist using the last recipe on this page.

```
--webpage https://www.lyricsfreak.com/[initial]/[artist+name]/ --container class=lf-list__container=1 --webextract links --alphabetize
```

### To get list of songs

The options below will get you a list of songs with spaces removed between words for long entries like “MARYJANESLASTDANCE”. To get the song titles converted into a word list (e.g., “MARY”, “JANES”, “LAST”, “DANCE”), replace `line2word` with `word2word`.

```
--webpage https://www.lyricsfreak.com/[initial]/[artist+name]/ --webextract html-a --regex '(.*?) Lyrics' --line2word
```

### To get song lyrics

Use the recipe below to get the lyrics from a single song. 

```
--webpage https://www.lyricsfreak.com/[initial]/[artist+name]/[song+name_datecode] --container id=content --webextract text --word2word
```

To get the lyrics from all songs by an artist, run the first recipe to get a file with a list of URLs and then use the recipe below.

```
--urllist --container id=content --webextract text --word2word
```

### Additional Notes

*  We have noticed that LyricsFreak will sometimes include non-lyric content such as “Short guitar break” within the text of lyrics. Always be sure to check the output for anything that doesn’t make sense for your word list.
