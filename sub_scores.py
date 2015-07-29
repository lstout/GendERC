import os
import re
import shutil
import sys
from os import listdir

"""
This script will extract the scores from the evaluations and remove them from those files.
"""


def find_files_folder(path, ext):
    onlyfiles = [os.path.join(path, f) for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == ext]
    return onlyfiles


def first_nonempty(_list):
    return next(s for s in _list if s)

re_ground_breaking_scores = re.compile('To what extent has the PI demonstrated the ability to propose and conduct ground-\s*(Very good|Excellent|Outstanding|Non-competitive)*?\s*breaking research\?\s*(Very good|Excellent|Outstanding|Non-competitive)*', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_evidence_scores = re.compile('To what extent does the PI provide evidence of creative independent thinking\?\s*(Very good|Excellent|Outstanding|Non-competitive)', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_achiev_scores = re.compile('To what extent have the achievements of the PI typically gone beyond the state of\s*(Very good|Excellent|Outstanding|Non-competitive)*?\s*the art\?\s*(Very good|Excellent|Outstanding|Non-competitive)*', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_commit_scores = re.compile('To what extent does the PI demonstrate the level of commitment to the project\s*(Very good|Excellent|Outstanding|Non-competitive)*?\s*necessary for its execution and the willingness to devote a significant amount of\s*(Very good|Excellent|Outstanding|Non-competitive)*?\s*time to the project \(min 50\% of the total working time on it and min 50\% in an EU\s*(Very good|Excellent|Outstanding|Non-competitive)*\s*Member State or Associated Country\) \(based on the full Scientific Proposal\)\?', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)

re_ground_breaking_sub = re.compile('Principal Investigator\s*To what extent has the PI demonstrated the ability to propose and conduct ground-\s*(?:Very good|Excellent|Outstanding|Non-competitive)*?\s*breaking research\?\s*(?:Very good|Excellent|Outstanding|Non-competitive)*', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_evidence_sub = re.compile('To what extent does the PI provide evidence of creative independent thinking\?\s*(?:Very good|Excellent|Outstanding|Non-competitive)', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_achiev_sub = re.compile('To what extent have the achievements of the PI typically gone beyond the state of\s*(?:Very good|Excellent|Outstanding|Non-competitive)*?\s*the art\?\s*(?:Very good|Excellent|Outstanding|Non-competitive)*', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_commit_sub = re.compile('To what extent does the PI demonstrate the level of commitment to the project\s*(?:Very good|Excellent|Outstanding|Non-competitive)*?\s*necessary for its execution and the willingness to devote a significant amount of\s*(?:Very good|Excellent|Outstanding|Non-competitive)*?\s*time to the project \(min 50\% of the total working time on it and min 50\% in an EU\s*(?:Very good|Excellent|Outstanding|Non-competitive)*\s*Member State or Associated Country\) \(based on the full Scientific Proposal\)\?', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)

re_boilerplate_1 = re.compile('The presentation given by the applicant during the interview and the answers to the questions that were addressed greatly contributed to build the panel\'s view about the proposal\'s strengths and weaknesses.', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_boilerplate_2 = re.compile('Both the individual reviews and the interview were the basis for the discussion and the final recommendation of the panel.\s*', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)

files = find_files_folder('evalutions_whole', 'txt')

for fn in files:
    print fn
    with open(fn) as fh:
        data = fh.read()
    gb_scores = [first_nonempty(l) for l in re_ground_breaking_scores.findall(data) if any(l)]
    creativ_scores = re_evidence_scores.findall(data)
    achiev_scores = [first_nonempty(l) for l in re_achiev_scores.findall(data)]
    commit_scores = [first_nonempty(l) for l in re_commit_scores.findall(data)]

    lists = [gb_scores, creativ_scores, achiev_scores, commit_scores] if commit_scores else [gb_scores, creativ_scores, achiev_scores]

    new_fn = fn.split('/')[-1]
    with open('evalutaion_scores/' + new_fn, 'w') as fh:
        fh.write('\t'.join(gb_scores) + '\n')
        fh.write('\t'.join(creativ_scores) + '\n')
        fh.write('\t'.join(achiev_scores) + '\n')
        fh.write('\t'.join(commit_scores) + '\n')

    data = re_ground_breaking_sub.sub('', data)
    data = re_evidence_sub.sub('', data)
    data = re_achiev_sub.sub('', data)
    data = re_commit_sub.sub('', data)

    data = re_boilerplate_1.sub('', data)
    data = re_boilerplate_2.sub('', data)


    with open('new_concat_files/' + new_fn, 'w') as fh:
        fh.write(data)

files = find_files_folder('evaluations_split', 'txt')

for fn in files:
    print fn
    with open(fn) as fh:
        data = fh.read()
    new_fn = fn.split('/')[-1]

    old_data = data
    data = re_ground_breaking_sub.sub('', data)
    data = re_evidence_sub.sub('', data)
    data = re_achiev_sub.sub('', data)
    data = re_commit_sub.sub('', data)

    data = re_boilerplate_1.sub('', data)
    data = re_boilerplate_2.sub('', data)

    if not data == old_data:
        with open('new_evaluations_split/' + new_fn, 'w') as fh:
            fh.write(data)

shutil.rmtree('evaluations_split')
shutil.rmtree('evaluations_whole')

os.rename('new_evaluations_split', 'evaluations_split')
os.rename('new_evaluations_whole', 'evaluations_whole')
