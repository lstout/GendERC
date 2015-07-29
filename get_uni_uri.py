import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup as Soup

"""
This script will try to get the dbpedia URI for a file with a list of universities.
The input is the filename of the list of universities and a file name where to save the resulting file.
"""

fn = sys.argv[1]
save_file = sys.argv[2]
base = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryClass=university&QueryString='

try:
    df = pd.DataFrame.from_csv(save_file)
except IOError:
    s = []
    with open(fn) as fh:
        for line in fh:
            line = line.strip()
            uni = pd.Series({'name': line, 'URI': None})
            s.append(uni)
    df = pd.DataFrame(s)
    df.to_csv(save_file)

df = df.where((pd.notnull(df)), None)
for index, row in df.iterrows():
    if row['URI']:
        continue
    print index
    xml = requests.get(base + row['name']).text
    s = Soup(xml)
    try:
        uri = s.find('result').find('uri').text
        row['URI'] = uri
    except:
        print row['name']
        try:
            uri = raw_input().strip()
            if uri:
                row['URI'] = uri
                print uri
        except KeyboardInterrupt:
            break

df.to_csv(save_file)
