# GendERC

This repository contains all scripts used in the automatic extraction of pdf files in the GendERC project of the academy assitants of the Network Institute in 2014. The project was conducted by Xiaoli Gou and [Luka Stout](github.com/lstout/) under supervision of Peter van den Besselaar. [The projects is found here!](http://www.networkinstitute.org/academy-assistants/academy-projects-14/)

#### What's what?
##### Ranking
[complete_ranking.txt](complete_ranking.txt) and [complete_ranking.xlsx](complete_ranking.xlsx) contain the rankings that are used in the process. It is a combination of the universities present in the [Leiden ranking 2014](http://www.leidenranking.com/ranking/2014), colleges that are associated with a universities and European Public Research Organisations. These PRO's are given the same ranking as an university in the same country as that PRO.
##### Extraction
* [CVs.py](CVs.py) contains the entire process of extracting the relevant parts of the CV and extraction the research institutes from them. This process makes heavy use of [DBPedia](http://wiki.dbpedia.org/) and [DBPedia spotlight](https://github.com/dbpedia-spotlight/dbpedia-spotlight).
* [extract_evaluations_from_folder.py](extract_evaluations_from_folder.py) extracts the text from the evaluation forms, removes boilerplate text and combines the files in such a way that they are easy to use with [LIWC](http://www.liwc.net/), which is the program used to do text analysis.

## Requirements
Python 2.7.9 (Tested, other versions might work.)

###Packages

* Pandas
* Numpy
* Requests
* SPARQLWrapper
* BeautifulSoup 4

* Ruby with [pdf-reader](http://github.com/yob/pdf-reader)  (For the text extraction)

## License
The code is licensed under a MIT license, found in [LICENSE](LICENSE).

