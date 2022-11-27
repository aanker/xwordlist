---
layout: recipes
title: Wikipedia
title_url: https://en.wikipedia.org/
permalink: /recipes/wikipedia
---

### To get the primary text content of a Wikipedia page

The options below will grab the text from the main article of a Wikipedia page, defined by all text content within `<p>` tags.

```
--webpage https://en.wikipedia.org/wiki/[subject] --container id=bodyContent --webextract html-p
```
It is recommended that you first use the above recipe to pull the raw text and then manually delete any extraneous text that doesn’t make sense for your word list. Then you can run the standard commands for turning the remaining text into a word list by using either `line2word` or `word2word`.

### To get a list from a Wikipedia table

The options below will help you parse a Wikipedia table, a good example of which is a discography of a musician or list of films for an actor. It is best to be specific when you are pulling this kind of chart: for example, instead of going to David Bowie’s main [Wikipedia page](https://en.wikipedia.org/wiki/David_Bowie), go to the more specific David Bowie [discography page](https://en.wikipedia.org/wiki/David_Bowie_discography) or [filmography page](https://en.wikipedia.org/wiki/David_Bowie_filmography).

Every table in a standard Wikipedia page uses the class label `wikitable`. The instructions below — `container class=wikitable` — will grab all of such tables on the page. If you only want to get the content from one particular table, be sure to add `=N` to the end of the option, where `N` is which table (in order from the top) is being requested. For example, to pull the third table you would specify `container class=wikitable=3`. Experiment to make sure you are grabbing the data you are interested in.

Note that the options below work because most Wikipedia tables italicize the content that is important (i.e., the title of the album or movie). The option `webextract html-i` requests only text that is italicized, thus capturing album and movie titles.

```
--webpage https://en.wikipedia.org/wiki/[subject] --container class=wikitable --webextract html-i
```

For other tables — such as lists of song titles — the important words are in quotes. To get data from those tables, use these options instead.

```
--webpage https://en.wikipedia.org/wiki/[subject] --container class=wikitable --webextract html-th --regex '"(.*?)"'
```
With either of these grabs, it is best to go through the data before parsing it further as there can be a lot of extra content you may don’t want. Once you have deleted the extraneous content, then run either the `line2word` or `word2word` parsing command on that file to get it into word list shape.

### Additional Notes

*  We have found that although Wikipedia pages have many standard tags, often times they are not consistent from page to page, even when similar data is being presented. For example, this [directory of Disney characters](https://en.wikipedia.org/wiki/Category:Disney_animated_characters) links off to a number of sub-pages, many of which have very different formatting from others. This can make it difficult to use the `urllist` option to crawl a number of sub-pages the way you might on a more consistently structured site.
