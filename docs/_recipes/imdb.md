---
layout: recipes
title: IMDB
title_url: https://imdb.com
permalink: /recipes/imdb
---

### To get a filmography from an actor, director, producer, etc.

The profile page of a person on IMDB has a very complete list of all of their credits, broken down by role: actor, director, producer, writer, etc. Each section has the class label `filmo-category-section` and we can use that to pull data from the page. In addition, the name of each property (generally a movie or TV show) is bolded. To get every title in the filmography section, use the following formula.
```
webpage https://www.imdb.com/name/[ID-code-for-person]                     ; customize
container class=filmo-category-section
webextract html-b
```
To get only one of a person’s roles, change the second line to `container class=filmo-category-section=N` where `N` is the numbered order on the page of the role. For instance, if we look at the profile page of [Greta Gerwig](https://www.imdb.com/name/nm1950086), we see that the second section of filmography is her writing credits. To pull that list only, use these settings.

```
webpage https://www.imdb.com/name/nm1950086/
container class=filmo-category-section=2
webextract html-b
```
Once you are comfortable with the raw text, use one of the catch-all options to turn it into a word list. If you want the list parsed out by words (i.e., “LADY”, “BIRD”), use `word2word`. If you want the entire line to be a word (i.e., “LADYBIRD”), use the `line2word` option.

### To get biography data

Profiles on IMDB also include a more detailed biography of each person. Click through to that page if you want to parse out the informational text about the person, we will then grab all the text from the bio by looking for the `<p>` tags.
```
webpage https://www.imdb.com/name/[ID-code-for-person]/bio                ; customize
container id=bio_content
webextract html-p
```
To get all of the information on the bio page, including the trivia and other content, just switch to grabbing the `<div>` tags.
```
webpage https://www.imdb.com/name/[ID-code-for-person]/bio                ; customize
container id=bio_content
webextract html-div
```
With either of these grabs, it is best to go through the data before parsing it further as there can be a lot of extra content you probably don’t want, including the name of the author of the bio. Once you have deleted the extraneous content, then run either the `line2word` or `word2word` parsing command on that file to get it into word list shape.
