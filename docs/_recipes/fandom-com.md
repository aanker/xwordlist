---
layout: recipes
title: Fandom
title_url: https://fandom.com/
permalink: /recipes/fandom
---

### To get the primary text content of a Fandom page

The options below will grab the text from an article on a standard Fandom wiki, defined by all text content within `<p>` tags.

```
webpage https://[fansite].fandom.com/wiki/[subject]                     ; customize
container id=mw-content-text
webextract html-p
```

Unfortunately there is no single container used by Fandom wikis that contains only the article text; the one used above (mw-content-text) may also include additional messages such as references to spoilers, other texts, etc. It is recommended that you first use the above recipe to pull the raw text and then manually delete any such extraneous text. Then you can run the standard commands for turning the remaining text into a word list by using either `line2word` or `word2word`.

### To get a list from a Fandom table

The options below will help you parse a Fandom table, a good example of which is a list of enchantments on the [Minecraft Fandom wiki](https://minecraft.fandom.com/wiki/Enchanting).

Every table in a standard Fandom page uses the class label `wikitable`. The instructions below — `container class=wikitable` — will grab all of such tables on the page. If you only want to get the content from one particular table, be sure to add `=N` to the end of the option, where `N` is which table (in order from the top) is being requested. For example, to pull the second table you would specify `container class=wikitable=2`. Experiment to make sure you are grabbing the data you are interested in.

To grab the key text (usually the first column), it is important to understand how the table is structured. For instance, on the above mentioned Minecraft enchantments page, the second table called “Summary of Enchantments” lists all the enchantments as a link (i.e., within an `<a>` tag). The option `webextract html-a` requests only text that is within links in that table, thus capturing the name of all the enchantments listed. To pull that list of enchantments, you would use this recipe.

```
webpage https://minecraft.fandom.com/wiki/Enchanting
container class=wikitable=2
webextract html-a
```

As described in the primary text section, this will also result in some extraneous data since there are a few other links in that table. Therefore, it is recommended that you first pull the raw text, then edit anything extraneous and finally run the additional commands `line2word` or `word2word`.

### Additional Notes

*  Each Fandom wiki tends to be pretty customized and so you will find that it is hard to use the same formula across multiple wikis. You are encouraged to explore the specifics of each wiki and look for a container `id` or `class` and specific HTML tags for the content you wish to grab. The only consistency we have noted is the use of the `wikitable` label for tables (similar to Wikipedia).
