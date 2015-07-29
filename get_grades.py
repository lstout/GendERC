import os
import re
import sys
from multiprocessing.dummy import Pool
from os import listdir

import reader

"""
This script will extract the final full panel grades from the reviews.
The input are 2 folders, the full path to the 2 folders of reviews
"""


def find_files_folder(path, ext):
    onlyfiles = [os.path.join(path, f) for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == ext]
    return onlyfiles

if not os.path.exists('grades'):
    os.mkdir('grades')

round1 = find_files_folder(sys.argv[1], 'pdf')
round2 = find_files_folder(sys.argv[2], 'pdf')

re_grade = re.compile(r'Final\spanel\sscore\s:\s(A|B|C)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_range = re.compile(r'Ranking\srange\s\*:\s(\d+%-\d+%)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)


def func(f):
    fn = 'grades/' + f.split('/')[-1][:-4] + '.txt'

    if os.path.exists(fn):
        return

    try:
        text = reader.extract_text_pdf(f)
    except IOError as e:
        print e
        with open('faulty_files.txt', 'a') as fh:
            fh.write('\n%s' % (f.split('/')[-1][:-4], ))
        return
    try:
        grade = re_grade.search(text).groups()[0]
        range_ = re_range.search(text).groups()[0]
    except AttributeError as e:
        print e
        print text

    with open(fn, 'w') as fh:
        fh.write("%s %s" % (grade, range_))

total = round1 + round2

pool = Pool(7)
pool.map(func, total)
pool.close()
pool.join()
