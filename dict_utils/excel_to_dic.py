import sys
from collections import defaultdict

import pandas

input_file = 'dictionary.xls'
df = pandas.read_excel(input_file, sheetname='dict_ADD.csv')

column_idxs = dict()

i = 1
for column in df:
    column_idxs[column] = i
    i += 1

words = defaultdict(set)

for column in df:
    for word in df[column].dropna():
        words[word].add(column_idxs[column])

fh = open('dictionary.dic', 'w')
fh.write('%\n')
for column in df:
    fh.write(str(column_idxs[column]) + '\t' + str(column) + '\n')

fh.write('\n%\n')
for k, v in words.items():
    try:
        fh.write(str(k).lower() + '\t')
        fh.write('\t'.join(map(str, v)) + '\n')
    except UnicodeEncodeError:
        pass

fh.close()
