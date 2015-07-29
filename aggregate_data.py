from __future__ import division

import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

"""
This script will aggregate the data from the institute extraction from the CVs and median/std dev from the evaluation form scores.
"""


def find_files_folder(path, ext):
    onlyfiles = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith(ext)]
    return onlyfiles


def inst_statistics(insts):
    if not insts:
        return 0, None, None, None
    ranks = []
    total_length = 0
    s = 0

    for inst in insts:
        ranks.append(inst[0])
        total_length += inst[1]
        s += inst[0] * inst[1]
    return len(insts), min(ranks), s / total_length, max(ranks)

score_transform = {'Non-competitive': 4, 'Very good': 3, 'Excellent': 2, 'Outstanding': 1}


def transform_scores(scores):
    ret_score = []
    for score in scores:
        ret_score.append(score_transform[score])
    return ret_score

avg = lambda l: sum(l) / len(l)
diff = np.std


def score_statistics(all_scores):
    # 1avg, 1diff, 2avg..
    ret = []
    n_reviewers = 0
    for scores in all_scores:
        if not scores:
            ret += [None, None]
            continue
        avg_score = avg(scores)
        diff_score = diff(scores)
        ret += [avg_score, diff_score]
        n_reviewers = len(scores)
    ret.append(n_reviewers)
    return tuple(ret)

institutions = defaultdict(list)
with open('institutions.tsv') as fh:
    headers = fh.readline().strip().split('\t')
    for line in fh:
        line = line.strip().split('\t')
        ID = int(line[0])
        rank = line[-2]
        freq = line[-1]
        try:
            rank = int(rank)
            freq = int(freq)
        except:
            #print line
            continue
        institutions[ID].append((rank, freq))

score_fns = find_files_folder('evaluation_scores', 'txt')
scores = {}
for fn in score_fns:
    with open(fn) as fh:
        f = fn.split('/')[-1][:-4]
        score = [[], [], [], []]
        n_reviewers = 0
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            line = line.split('\t')
            score[i] = transform_scores(line)
        if not any(score):
            with open('faulty_files.txt', 'a') as faulty_fh:
                faulty_fh.write(f + '\n')
            continue
    scores[int(f)] = score

grade_fns = find_files_folder('grades', 'txt')
percentages = {}
for fn in grade_fns:
    with open(fn) as fh:
        f = fn.split('/')[-1][:-4]
        grade, percentage = fh.readline().split()
        percentages[int(f)] = percentage

faulty = set()
with open('faulty_files.txt') as fh:
    for line in fh:
        line = line.strip()
        if line:
            faulty.add(int(line))

IDs = list(set(institutions.keys()) | set(scores.keys()) | set(percentages.keys()) | faulty)
data_file = open('new_data.tsv', 'w')
sep = '\t'
headers = sep.join(['id', 'score1 avg', 'score1 stddev', 'score2 avg', 'score2 stddev',
        'score3 avg', 'score3 stddev', 'score4 avg', 'score4 stddev', 'nr reviewers',
        'percentage group', 'nr institutions', 'highest ranked institution',
        'median rank institutions', 'lowest ranked institution'])
data_file.write(headers + '\n')
for ID in IDs:
    s = [ID]

    try:
        s.extend(score_statistics(scores[ID]))
    except:
        s.extend(score_statistics([[], [], [], []]))

    try:
        s.append(percentages[ID])
    except:
        s.append(None)

    try:
        s.extend(inst_statistics(institutions[ID]))
    except:
        s.extend([0, None, None, None])

    new_s = sep.join(map(str, s)) + '\n'
    new_s = new_s.replace('.', ',')
    data_file.write(new_s)
data_file.close()
