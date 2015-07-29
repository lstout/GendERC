from __future__ import division, print_function

import cPickle
import os
import re
import time
from collections import defaultdict
from functools import partial
from os import listdir

import pandas as pd
import requests
from SPARQLWrapper import JSON, SPARQLWrapper

import reader
from spotlight import SpotlightException, annotate

"""
This script will run the extraction from the CVs. It will extract all institutions from it.
The input to this script are two folders, one for both round.
"""


def find_files_folder(path, ext):
    onlyfiles = [os.path.join(path, f) for f in listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == ext]
    return onlyfiles

re_sections = re.compile(r'(section[\s▯]+?b[\s:\.]*?(.*)|c(?:\s)?urr?iculum\s*v(?:\s)?it(?:ae)?(.*)|about the principle investigator(.*)|personal\s+?information(.*)|cv\s+?of\s+?the\s+?principal\s+?investigator(.*)|6\s*Cattaneo\s*Part\s*B1\s*ABC(.*)|CV\s*applicant(.*)|http://goo\.gl/f4buun(.*)|CV, Pia Quist(.*)|Angela\s*Beth\s*Brueggemann,\s*MSc,\s*DPhil(.*)|b:\s*CV(.*)|http://solveigserre\.free\.fr(.*)|Personal\s*details(.*)|CV\s*-(.*))', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_section_track_record = re.compile(r'(?:section\s+?\(?c\)?|(?:e(?:\s)?arly)?(?:-track)?\s?a(?:\s)?chievements?|track[\s-]+?record)', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_cv = re.compile(r'education(.*?)current position(?:\(s\))?(.*?)previous position(?:\(s\))?(.*)', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)
re_grant = re.compile('(?<![\.\d])(\d{1,3}[\.,](\d{3}[\.,])*\d{3}(?!\d))', flags=re.DOTALL + re.UNICODE + re.MULTILINE + re.IGNORECASE)


def get_cv(text):
    sections = re_sections.search(text).groups()[0]
    cv, track_record = re_section_track_record.split(sections, maxsplit=1)
    return cv, track_record

types = '''DBpedia:EducationalInstitution,
DBpedia:University,
DBpedia:Government_agency,
Freebase:/education/academic_institution,
Freebase:/education/educational_institution,
Freebase:/education/school,
Freebase:/education/university,
Freebase:/education/university_system,
Freebase:/government/government_agency,
Schema:CollegeOrUniversity,
Schema:EducationalOrganization,
Schema:GovernmentOrganization,
DBpedia:Organisation,
Schema:Organization,
Freebase:/organization/organization,
Freebase:/organization'''
_dbp = partial(annotate, 'http://spotlight.dbpedia.org/rest/annotate', types=types)


def get_institutions(text):
    try:
        entities = _dbp(text)
    except SpotlightException:
        return []
    return_list = []
    for entity in entities:
        try:
            surf = entity['surfaceForm']
            if len(surf.split()) <= 1 and not surf.upper() == surf:
                continue
        except:
            continue
        return_list.append(entity)
    return return_list

ranking = pd.DataFrame.from_csv('institutes.txt', sep='\t')


def parse_cv(cv):
    search = re_cv.search(cv)
    if search:
        concat_cv = ('=' * 80 + '\n').join(s for s in search.groups() if s)
    else:
        concat_cv = cv

    all_insts = get_institutions(concat_cv)

    insts = defaultdict(list)
    for inst in all_insts:
        insts[inst['URI']].append(inst['surfaceForm'])

    institutions = []
    not_found = []
    for URI, surfForms in insts.items():
        try:
            print(ranking.loc[ranking['URI'] == URI])
            print(ranking.loc[ranking['URI'] == URI].index[0])
            rank = ranking.loc[ranking['URI'] == URI].index[0]
        except IndexError:
            rank = None
            not_found.append((surfForms, URI))
        institutions.append({'URI': URI, 'surfForms': surfForms, 'rank': rank})

    return institutions, not_found


def read_cv(f):
    ret_f = os.path.splitext(os.path.basename(f))[0]
    filename_text = 'cache/' + ret_f

    try:
        with open(filename_text) as fh:
            text = cPickle.load(fh)
    except:
        try:
            text = reader.extract_text_pdf(f)
        except Exception as e:
            return (ret_f[:6], "")
        with open(filename_text, 'w') as fh:
            cPickle.dump(text, fh)

    return (ret_f[:6], text)


def process_cv(f_text):
    f, text = f_text
    if not text:
        return (f, None, None, None)
    try:
        cv, track_record = get_cv(text)
        institutions, not_found = parse_cv(cv)
    except (AttributeError, ValueError, requests.HTTPError, SpotlightException) as e:
        print(f)
        print(type(e))
        print(e)
        return (f, None, None, None)
    return (f, institutions, not_found)

stop_n = -1
start = time.time()

files_round1 = find_files_folder(sys.argv[1], 'pdf')[:stop_n]
files_round2 = find_files_folder(sys.argv[2], 'pdf')[:stop_n]

print('Round 1:', len(files_round1))
print('Round 2:', len(files_round2))
sys.stdout.flush()
if not os.path.exists('cache/'):
    os.mkdir('cache')

processed_files = set()
if not os.path.exists('institutions.tsv'):
    with open('institutions.tsv', 'w') as fh:
        fh.write('id \t ints_name \t inst_uri \t rank \t frequency \n')
else:
    with open('institutions.tsv') as fh:
        for line in fh:
            line = line.split('\t')
            processed_files.add(line[0])

faulty_set = set()
if os.path.exists('faulty_files.txt'):
    with open('faulty_files.txt', 'r') as fn:
        for line in fn:
            faulty_set.add(line.strip())

faulty_files = []
not_found_all = []
correct_f = []
inst_file = open('institutions.tsv', 'a')

all_files = files_round1 + files_round2
all_files = [f for f in all_files if not os.path.splitext(os.path.basename(f))[0][:6] in processed_files and not os.path.splitext(os.path.basename(f))[0][:6] in faulty_set]
print('Filtered away', len(files_round1 + files_round2) - len(all_files), 'of', len(files_round1 + files_round2))

for i, f in enumerate(all_files, start=1):
    print(i, 'of', len(all_files), '(%.1f%%)' % (i / len(all_files) * 100), end='')
    sys.stdout.flush()
    print('\r', end='')

    text = read_cv(f)
    res = process_cv(text)
    f, insts, not_found = res

    if not insts and not not_found:
        faulty_files.append(f)
        continue
    if insts:
        for inst in insts:
            inst_file.write(f + '\t')
            inst_file.write(inst['surfForms'][0].encode('ascii', 'ignore') + '\t')
            inst_file.write(inst['URI'] + '\t')
            inst_file.write(str(inst['rank']) + '\t')
            inst_file.write(str(len(inst['surfForms'])) + '\n')

    correct_f.append(f)
    not_found_all += not_found
inst_file.close()

print()
i = 0
with open('unknown_institutions.csv', 'a+') as fn:
    already_saved = set()
    fn.seek(0)
    for line in fn:
        already_saved.add(line.strip().split('\t')[0])
    fn.seek(0, 2)
    for insts, URI in not_found_all:
        for inst in set(insts):
            string = inst.replace(',', '')
            if string in already_saved:
                already_saved.add(string)
                continue
            i += 1

print(i, 'not found as institutions in leiden ranking.')
print('Saved in unknown_institutions.csv')

print()
print(len(correct_f), 'correctly parsed files')
print()

new_faulty = 0
with open('faulty_files.txt', 'a') as fn:
    for filename in faulty_files:
        if filename in faulty_set:
            continue
        fn.write(filename + '\n')
        new_faulty += 1

print(new_faulty, 'faulty files saved in faulty_files.txt')

end = time.time()
try:
    print(end - start, 'seconds total.')
    print((end - start) / (len(correct_f) + new_faulty), 'seconds per results')
except:
    pass
