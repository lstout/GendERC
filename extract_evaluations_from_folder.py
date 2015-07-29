from __future__ import division

import os
import re
import sys
import time
from os import listdir

import reader

"""
This script will extract the text from the pdf-evaluations and seperate it into different directories.
The input is a folder full of evaluation forms.
"""


def find_files_folder(path, ext):
    onlyfiles = [os.path.join(path, f) for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == ext]
    return onlyfiles

re_review = re.compile(r'Reviewer\s+(?:\d)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_impact = re.compile(r'Research Project\s*(?:Ground-breaking nature and potential impact of the research project:)(.*?)(?:Scientific Approach:|Comments)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_approach = re.compile('Scientific Approach:(.*?)(?:Comments|$)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_comments = re.compile('Comments \(Optional for reviewers\)(.*)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_newlines = re.compile(r'((?<![\.!?])\s\n)', flags=re.DOTALL + re.UNICODE)
re_panel = re.compile(r'(\[.*?\])', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_panel_comment = re.compile(r'in this report.\s*(.*?)\[', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_panel_comment_parts = re.compile(r'(.*?)\s*\n\s*(.*?)\s*?(on the basis.*|overall.*|the panel therefore.*|the panel recommends.*)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_scores_B = re.compile(r'the ability to propose and conduct ground-(?:\s*breaking research\?)?\s*(Outstanding|Excellent|Very Good|Non-competitive).*?creative independent thinking\?\s*(Outstanding|Excellent|Very Good|Non-competitive).*?beyond the state of(?:\s*the art\?)?\s*(Outstanding|Excellent|Very Good|Non-competitive)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_scores_A = re.compile(r'\s*.*?(?:a significant amount of).*?\s*(Outstanding|Excellent|Very Good|Non-competitive)', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)
re_no_comment = re.compile(r'No\s*Comments\s*received*', flags=re.IGNORECASE + re.DOTALL + re.UNICODE)


def get_panel_reviews(text):
    reviews = re_review.split(text)

    try:
        panel_comment = reviews[0]
        panel_comment = re_newlines.sub("", panel_comment)
        panel_comment = re_panel_comment.search(panel_comment).groups()[0]

        p_appl, p_person, p_verdict = re_panel_comment_parts.search(panel_comment).groups()
        if not p_person:
            p_person = ''
    except AttributeError:
        p_appl = ''
        p_person = ''
        p_verdict = ''

    reviewers = []
    ret_l = [p_appl, p_person, p_verdict]
    for review in reviews[1:]:
        if not review.strip():
            continue

        scores = re_scores_B.search(review).groups()

        scores = ','.join(scores)

        try:
            score = re_scores_A.search(review).groups()[0]
            scores += ',' + str(score)
        except AttributeError:
            pass

        try:
            impact = re_impact.search(review).groups()[0]
        except AttributeError:
            impact = ''

        try:
            approach = re_approach.search(review).groups()[0]
        except AttributeError:
            approach = ''

        try:
            pi = re_comments.search(review).groups()[0]
        except AttributeError:
            pi = ''

        impact = re_panel.sub('', impact)
        impact = re_no_comment.sub(' ', impact)
        approach = re_panel.sub('', approach)
        approach = re_no_comment.sub(' ', approach)
        pi = re_panel.sub('', pi)
        pi = re_no_comment.sub(' ', pi)
        ret_l.append(impact)
        ret_l.append(approach)
        ret_l.append(scores)
        ret_l.append(pi)

    return ret_l

folder = sys.argv[1]

files = find_files_folder(folder, 'pdf')[327:]

if not os.path.exists('evaluations_split'):
    os.mkdir('evaluations_split')

if not os.path.exists('evaluations_whole'):
    os.mkdir('evaluations_whole')

if not os.path.exists('evaluation_scores'):
    os.mkdir('evaluation_scores')

field_names = '_panel_appl,_panel_person,_panel_verdict,' + ''.join('_r%d_appl,_r%d_meth,_r%d_scores,_r%d_person,' % (i, i, i, i) for i in range(1, 15))
field_names = field_names[:-1].split(',')

total = 0
for i, f in enumerate(files):
    print 'Processing', i + 1, 'of', len(files), '...'
    start = time.time()
    text = reader.extract_text_pdf(f)
    panel_reviews = get_panel_reviews(text)

    base = os.path.splitext(os.path.basename(f))[0]

    parts_base = 'evaluations_split/' + base

    scores_name = 'evaluation_scores/' + base + '.txt'
    score_file = open(scores_name, 'w')

    concat_name = 'evaluations_whole/' + base + '.txt'
    concat_file = open(concat_name, 'w')

    for i, name in enumerate(field_names):
        try:
            field = panel_reviews[i].replace(u"\u2018", "'").replace(u"\u2019", "'")
            field = field.strip()
            field = field.replace('\n', ' ')
            field = field.replace('\t', ' ')
            field = field.replace(u'\xb4', "'")
            field = field.replace(u'\u201c', '"')
            field = field.replace(u'\u201d', '"')
            field = field.replace(u'\u2013', '-')
            field = field.replace(u' -', '-')
            field = field.replace(u'\xef', 'i')
            field = field.encode("ascii", errors='ignore')

            if not field:
                continue

            if name[-6:] == 'scores':
                score_file.write(field + '\n')
                continue

            with open(parts_base + name + '.txt', 'w') as fh:
                fh.write(field + '\n\n')

            concat_file.write(field + '\n\n')

        except Exception as e:
            pass
    concat_file.close()
    score_file.close()

    print time.time() - start, 'seconds'
    total += time.time() - start
    print 'Done'

print total / len(files), 'seconds per doc average'
