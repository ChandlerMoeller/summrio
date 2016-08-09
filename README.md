# summrio
Summrio takes in text in the form of a url to an article on a news website and will output a summary of that text. This project was built with adding more modules (more functionality beyond just news articles) in mind.
##How it Works
###Get text
####From a news article web page:
Newsarticle.py will take in a web page url (although it will probably work for any web page with a block of text). News websites do not have a standard way of displaying their text. Newsarticle.py will attempt to find the article text by traversing through the html tree (which was created through the BeautifulSoup library). Newsarticle will assume that the article text is in the node whose leaf children contain the most text. The assumed text is then passed to summrio.py.
####From somewhere else:
Will be added in the future

###Summarize
Summrio.py will make a frequency list of all words in the text (discluding some commonly used words and words 3 letters or less). Multipliers are added if that word begins with a capital letter and if that word is in the article title (if there is a title). Summrio.py will then score each sentence based on that sentences proximity to the front of the paragraph that it is in, the proximity of the paragraph that it is in to the beginning of the article, and the words from the frequency list that are cotained in the sentence. After each sentence has been given a score, the average of those scores and the standard deviation of the scores are calculated. Any sentence that has a score greater than the average + the standard deviation will be output in the summary.

##Contents
###summrio.py  
Functions used to turn text into a summary.
###newsarticle.py
Specific functions for getting text from news articles web pages.
###helper.py
More general functions that could be reused in future modules.

##Being worked on
* Animation
* Look into switching web parsing library to something else for effeciency reasons
* Add more modules in addition to newsarticle.py

##Problems
* Fixing compatibility with a few news sites
