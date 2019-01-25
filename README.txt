# topic-analyzer
Project by Srivatsan Ananthakrishnan.
Dependency:
python -m nltk.downloader punkt

1. Step 1: Html Parsing:
a) BeautifulSoap4
Library: BeautifulSoap4
Reference : http://www.pythonforbeginners.com/python-on-the-web/web-scraping-with-beautifulsoup/
commands:
python -m pip install beautifulsoup4 


b) Content Extraction: 
Library name - NewsPaper
Reference: https://github.com/codelucas/newspaper
Command:
python -m pip install newspaper3k

2. Noun Chunker:
Library: Spacy, Wikipedia
For spacy, in windows, make sure that there Visual C++ 14 build tools installed.
If not, install from here http://landinghub.visualstudio.com/visual-cpp-build-tools

Commands:
python -m pip install -U spacy
python -m spacy download en_core_web_sm
python -m pip install wikipedia

3. Kmeans Clustering:
Library: Numpy, Gensim
python -m pip install numpy
python -m pip install --upgrade gensim

Data Set: GoogleNews Pre-trained data set. Download from source file folder from the drive link.

4. Ranking:
Library: requests, beautifulsoup4
commands: pip install beautifulsoup4
pip install requests
reference : http://www.pythonforbeginners.com/beautifulsoup/beautifulsoup-4-python

Sample test websites:
http://thehill.com/policy/cybersecurity/361583-4-legal-dimensions-of-the-uber-data-breach
http://news.bbc.co.uk/2/hi/health/2284783.stm
http://www.latimes.com/business/hiltzik/la-fi-hiltzik-net-neutrality-20171122-story.html 




