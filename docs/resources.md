---
layout: home
title:  Resources and Recipes
menu_title: Resources
permalink: /resources/
---

To help you understand ways to use `xwordlist` as well as provide support for common usage patterns, please see the recipe pages linked below. It is important to remember whenever you grab words from sites on the internet, the data is only as reliable as the site itself. We recommend that you check your lists before using them to construct puzzles and that you don’t use any entry before making sure it is both appropriate to your puzzle and thematic enough to warrant its use.

## Recipes

For each recipe included in these pages, we have provided configuration file options that can be easily pasted into your `xwordlist.conf` file. Be sure to customize any links to the exact page(s) you want and to configure any output file names. The instructions given are specific to each site’s HTML when we created the recipes but of course, websites change. If you notice that one of the recipes is no longer working, don’t hesitate to open an [issue](https://github.com/aanker/xwordlist/issues) and let us know.

In general, it is good to test the content before you turn it into a word list. To do this, first run `xwordlist` without the options for `convert`, `strip`, `dedupe`, `alphabetize` and `case`. After being certain that the content you are pulling makes sense for your word list, run it again with all options and you will have a word list.

### Reference Sites

*  [Wikipedia](/recipes/wikipedia) - Pull reference text, tables of data, lists of collaborators and other information from Wikipedia

### Song Lyric Sites

*  [SongLyrics](/recipes/song-lyrics) - Get lists of songs and the lyrics of most well-known musicians
*  [LyricsFreak](/recipes/lyrics-freak) - Get lists of songs and the lyrics of most well-known musicians

### Movie and Television Sites

*  [IMDB](/recipes/imdb) - Get filmography and biographical data on actors, directors and other movie and television creators

## Legal Disclaimer

Always read the terms of service first! Our inclusion of any website does not guarantee that pulling information programmatically is allowed under the site’s terms of service or that you won’t be blocked trying. We make no representations of anything; you’re on your own when use `xwordlist` and when you download data from public websites while using it.
