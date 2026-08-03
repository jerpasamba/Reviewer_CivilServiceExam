# -*- coding: utf-8 -*-
import json
import os
import re

TEMP = r'C:\Users\JERMAI~1\AppData\Local\Temp\opencode'
SRC = os.path.join(TEMP, 'parsed_years.json')
OUT_DIR = r'D:\VS_Code_Repositories\CiviilServiceReviewer'
TEMPLATE = os.path.join(OUT_DIR, 'quiz.html')

SECTION_LABELS = {
    'english_grammar': 'English Grammar & Correct Usage',
    'vocabulary': 'English Vocabulary',
    'spelling_idioms': 'Correct Spelling & Idiomatic Expressions',
    'analogy': 'Analogy',
    'reading': 'Reading Comprehension',
    'paragraph_org': 'Paragraph Organization',
    'numerical': 'Numerical Reasoning',
    'clerical': 'Clerical Operations',
    'constitution': 'Constitution & General Information',
    'idiomatic': 'Idiomatic Expressions',
}

GROUPS_2018 = [
    ('English', ['english_grammar', 'vocabulary', 'spelling_idioms', 'analogy']),
    ('Reading', ['reading', 'paragraph_org']),
    ('Mathematics', ['numerical']),
    ('Clerical', ['clerical']),
    ('Civics / General Information', ['constitution']),
]

GROUPS_OTHER = [
    ('English', ['vocabulary', 'idiomatic', 'analogy']),
    ('Reading', ['reading', 'paragraph_org']),
    ('Mathematics', ['numerical']),
    ('Clerical', ['clerical']),
    ('Civics / General Information', ['constitution']),
]


def to_data(items):
    out = []
    for q in items:
        if 'a' not in q or not q['opts']:
            raise ValueError('question missing answer/options: %s' % q)
        t = ' '.join(q['text'])
        opts = [o['value'] for o in q['opts']]
        if not (0 <= q['a'] < len(opts)):
            raise ValueError('answer out of range: %s' % q)
        out.append({'n': q['num'], 'q': t, 'o': opts, 'a': q['a']})
    return out


def main():
    with open(SRC, encoding='utf-8') as f:
        parsed = json.load(f)
    with open(TEMPLATE, encoding='utf-8') as f:
        template = f.read()

    for year in ('2018', '2019', '2020'):
        data = parsed[year]
        groups = GROUPS_2018 if year == '2018' else GROUPS_OTHER

        data_out = {}
        groups_out = []
        for gname, keys in groups:
            items = []
            for k in keys:
                data_out[k] = to_data(data.get(k, []))
                items.append([k, SECTION_LABELS[k]])
            groups_out.append([gname, items])

        data_json = json.dumps(data_out, ensure_ascii=False).replace('</', '<\\/')
        groups_json = json.dumps(groups_out, ensure_ascii=False).replace('</', '<\\/')
        ls_key = 'csc%s_progress_v1' % year
        title = 'CSC Civil Service Exam Reviewer 2026 - %s Quiz' % year

        html = template
        html = html.replace(
            '<title>CSC Civil Service Exam Reviewer 2026 - Quiz</title>',
            '<title>%s</title>' % title)
        html = re.sub(r'^const DATA = .*;\r?$', 'const DATA = ' + data_json + ';',
                      html, count=1, flags=re.M)
        html = re.sub(r'^const GROUPS = .*;\r?$', 'const GROUPS = ' + groups_json + ';',
                      html, count=1, flags=re.M)
        html = re.sub(r"^const LS_KEY = .*;\r?$",
                      'const LS_KEY = ' + json.dumps(ls_key) + ';',
                      html, count=1, flags=re.M)
        html = html.replace(
            'CSC Civil Service Exam Reviewer 2026</h1>',
            'CSC Civil Service Exam Reviewer 2026 - %s Exam</h1>' % year)

        out_path = os.path.join(OUT_DIR, 'quiz-%s.html' % year)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        total = sum(len(v) for v in data_out.values())
        print('written %s  (%d questions, %d bytes)' % (out_path, total, len(html)))


if __name__ == '__main__':
    main()
