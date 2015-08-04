# GendERC

This repository contains all scripts used in the automatic extraction of pdf files in the GendERC project of the academy assitants of the Network Institute in 2014. The project was conducted by Xiaoli Gou and [Luka Stout](github.com/lstout/) under supervision of [Peter van den Besselaar](http://www.vandenbesselaar.net/). [The project is found here!](http://www.networkinstitute.org/academy-assistants/academy-projects-14/).
In this project we try to identify possible gender-specific influences on the assessment of the [ERC](http://erc.europa.eu/) Starting Grant. Are the decision criteria in the application process of the Starting Grant gender-biased, and/or are they deployed in a gender biased manner?

We will try to find an answer to these questions by first focussing on a linguistic analysis of evaluation forms to see whether there is a difference in how female applicants are treated compared to how male applicants are treated, and how funded and unfunded applications compare.

For the second part we will try to see whether there is an actual gender bias or whether the problem of this bias lies deeper in the system. This will be done by looking at performance related data. We will use earlier grants in combination with previous institutions as a proxy for performance.

We will also look at the influence of the panel that reviews an applicant on the success chance of applicants.

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

