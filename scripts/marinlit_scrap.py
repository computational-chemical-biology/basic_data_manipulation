import urllib
from bs4 import BeautifulSoup
import pandas as pd
import sys

#url = 'https://pubs.rsc.org/marinlit/compound/cs000000061862'

def getArticle(url):
    response = urllib.request.urlopen(url)
    webContent = response.read()
    soup = BeautifulSoup(webContent)
    ps = soup.find_all('p')
    doi, title = ("", "")
    for x in ps:
        if 'DOI' in str(x):
            doi = x.text
        elif 'title=' in str([a for a in x.children][0]):
            title = x.text
    return (doi, title)

if __name__=='__main__':
    filename = sys.argv[1]
    outfile = sys.argv[2]
    db = pd.read_csv(filename, sep='\t')

    articles = []
    missing = []
    for i in db.index:
        url = 'https://pubs.rsc.org/marinlit/compound/%s' % db.loc[i, 'Identifier']
        try:
            articles.append(getArticle(url))
        except:
            missing.append(db.loc[i, 'Identifier'])

    pd.DataFrame(articles).to_csv(outfile, sep='\t', index=None, header=None)
