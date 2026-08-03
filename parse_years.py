# -*- coding: utf-8 -*-
import json
import os
import re

TEMP = r'C:\Users\JERMAI~1\AppData\Local\Temp\opencode'
DUMPS = {
    '2018': os.path.join(TEMP, 'CSE_REVIEWER_2018.txt'),
    '2019': os.path.join(TEMP, 'CSE_REVIEWER_2019.txt'),
    '2020': os.path.join(TEMP, 'CSE_REVIEWER_2020.txt'),
}

WS = re.compile(r'\s+')


def read_lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read().splitlines()


def clean(s):
    s = s.replace('\u2019', "'").replace('\u2018', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2013', '-').replace('\u2014', '-')
    s = s.replace('\u00a0', ' ')
    return WS.sub(' ', s).strip()


PAGE_MARK = re.compile(r'^#+\s*PAGE\s+\d+\s*#+$', re.IGNORECASE)


def is_page_mark(line):
    return bool(PAGE_MARK.match(line))


SECTION_KEYS = [
    ('english_grammar', 'englishgrammarandcorrectusage'),
    ('english_grammar', 'englishgrammarandcorrectusagetestanswers'),
    ('vocabulary', 'englishvocabulary'),
    ('vocabulary', 'vocabulary'),
    ('spelling_idioms', 'correctspelling,idiomatic'),
    ('spelling_idioms', 'correctspelling'),
    ('analogy', 'civilserviceexamreviewerforanalogy'),
    ('analogy', 'wordanalogy'),
    ('analogy', 'analogyandlogic'),
    ('reading', 'readingcomprehension'),
    ('paragraph_org', 'paragraphorganization'),
    ('numerical', 'numericalreasoning'),
    ('clerical', 'clericaloperation'),
    ('clerical', 'clericalreasoning'),
    ('constitution', 'philippineconstitution'),
    ('constitution', 'constitution,generalinformation'),
    ('graphs', 'graphs'),
]


def detect_section(text):
    low = WS.sub('', text.lower())
    for sec, prefix in SECTION_KEYS:
        if low.startswith(prefix):
            return sec
    return None


# ---------------- 2018: numbered options ----------------

def num_opt_segments(text):
    matches = list(re.finditer(r'(?<![\d/])(\d{1,2})\.\s+', text))
    if len(matches) < 2 or matches[0].start() != 0:
        return [(None, text)]
    segs = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segs.append((int(m.group(1)), text[start:end].strip()))
    return segs


QNUM_N = re.compile(r'^(\d{1,3})(?:\.\)|\.|\))\s*(.*)$')


def parse_numbered(lines, sec_at=None):
    """sec_at: callable(line_index)->section key or None (for 2018 boundaries)."""
    questions = []
    cur = None
    cur_sec = None
    pending = None
    for idx, raw in enumerate(lines):
        if is_page_mark(raw):
            continue
        text = clean(raw)
        if not text:
            continue
        if sec_at is not None:
            sec = sec_at(idx)
            if cur_sec is not None and sec != cur_sec:
                if cur is not None:
                    questions.append(cur)
                    cur = None
                pending = None
            cur_sec = sec
        else:
            sec = None
        m = QNUM_N.match(text)
        if m:
            num, rest = int(m.group(1)), m.group(2)
            if cur is None and pending is not None:
                if num == 1 and rest:
                    cur = {'num': 1, 'text': [pending], 'opts': [{'label': 1, 'value': rest}],
                           'order': len(questions), 'sec': sec}
                    pending = None
                    continue
                pending = None
            segs = num_opt_segments(text)
            if cur is None:
                cur = {'num': num, 'text': [], 'opts': [], 'order': len(questions), 'sec': sec}
                if rest:
                    cur['text'].append(rest)
                continue
            if not cur['opts']:
                if len(segs) > 1 and (segs[0][0] == 1 or segs[0][0] == cur['num']):
                    cur['opts'] = [{'label': l, 'value': v} for l, v in segs]
                elif num == 1:
                    cur['opts'] = [{'label': 1, 'value': rest}]
                else:
                    questions.append(cur)
                    cur = {'num': num, 'text': [], 'opts': [], 'order': len(questions), 'sec': sec}
                    if rest:
                        cur['text'].append(rest)
                continue
            expected = cur['opts'][-1]['label'] + 1
            if len(segs) > 1 and segs[0][0] == expected and expected <= 4:
                cur['opts'].extend([{'label': l, 'value': v} for l, v in segs])
                continue
            if num == expected and expected <= 4:
                cur['opts'].append({'label': num, 'value': rest})
                continue
            questions.append(cur)
            cur = {'num': num, 'text': [], 'opts': [], 'order': len(questions), 'sec': sec}
            if rest:
                cur['text'].append(rest)
            continue
        if detect_section(text) or is_footer(text):
            continue
        if text.lower().startswith('instruction:') or text.lower().startswith('instructions:'):
            continue
        if cur is None:
            pending = text if (text.endswith('?') or '_' in text) else None
            continue
        if not cur['opts']:
            cur['text'].append(text)
        else:
            cur['opts'][-1]['value'] += ' ' + text
    if cur:
        questions.append(cur)
    return questions


# ---------------- 2019/2020: lettered options ----------------

QNUM_L = re.compile(r'^(\d{1,3})(?:\.\)|\.|\))\s*(.*)$')
OPT_L = re.compile(r'^([a-e])(?:\.\)|\.|\)|,)\s*(.*)$', re.IGNORECASE)
INLINE_OPT = re.compile(r'(?<!\w)([a-e])(?:\.\)|\.|\)|,)\s+', re.IGNORECASE)


def letter_opt_segments(text):
    """Split a line into multiple (label, value) options when options are inlined."""
    matches = list(INLINE_OPT.finditer(text))
    if len(matches) < 2 or matches[0].start() != 0:
        return [(None, text)]
    segs = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segs.append((m.group(1).lower(), text[start:end].strip()))
    return segs

NOISE = [
    'free reviewer', 'or search on', 'tips)', 'no copyright infringement',
    'https://', 'youtu.be', 'like and share', 'visit our',
    'facebook.com', 'video review', 'subscribe', 'smart!',
    'not for sale', 'free/leonalyn', 'free/lmtayone', 'shared 100% free',
    'philippines civil service exam',
]

FOOTER_KEYS = [r'^civil service exam \d{4} philippine$']


def is_footer(text):
    low = text.lower()
    return any(re.match(p, low) for p in FOOTER_KEYS)


def is_noise(text):
    low = text.lower()
    if re.match(r'^[?*•]\s*$', text):
        return True
    if re.match(r'^choices?\s*:?\s*$', low):
        return True
    for tok in NOISE:
        if tok in low:
            return True
    return False


PASSAGE_ANNOUNCE = re.compile(
    r'^questions?\s*(\d{1,3})\s*[-–]\s*(\d{1,3})\s+are\s+about\s+the\s+following\s+passage',
    re.IGNORECASE)


def parse_lettered(lines):
    questions = {}
    cur = None
    passage = None
    passage_end = None
    for raw in lines:
        if is_page_mark(raw):
            continue
        text = clean(raw)
        if not text:
            continue
        m_pass = PASSAGE_ANNOUNCE.match(text)
        if m_pass:
            passage = []
            passage_end = int(m_pass.group(2))
            continue
        if is_noise(text) or is_footer(text):
            continue
        if detect_section(text):
            continue
        m = QNUM_L.match(text)
        if m:
            num = int(m.group(1))
            rest = m.group(2).strip()
            if rest:
                rest = re.sub(r'(READING COMPREHENSION|PARAGRAPH ORGANIZATION|'
                              r'PHILIPPINE CONSTITUTION TEST)\s*$', '', rest).strip()
            cur = {'num': num, 'text': [], 'opts': [], 'order': num}
            if rest:
                cur['text'].append(rest)
            if passage is not None and num <= passage_end:
                cur['passage'] = ' '.join(passage)
                passage = None
                passage_end = None
            questions[num] = cur
            continue
        m_opt = OPT_L.match(text)
        if m_opt and cur is not None:
            segs = letter_opt_segments(text)
            if len(segs) > 1:
                for lbl, val in segs:
                    if not val:
                        continue
                    if any(o['label'] == lbl for o in cur['opts']):
                        continue
                    cur['opts'].append({'label': lbl, 'value': val})
                continue
            label = m_opt.group(1).lower()
            value = m_opt.group(2).strip()
            if not value:
                continue
            if any(o['label'] == label for o in cur['opts']):
                continue
            cur['opts'].append({'label': label, 'value': value})
            continue
        if passage is not None:
            passage.append(text)
            continue
        if cur is not None:
            if not cur['opts']:
                cur['text'].append(text)
            else:
                cur['opts'][-1]['value'] += ' ' + text
    return questions


# ---------------- Answers: 2018 ----------------

ANS_2018 = re.compile(r'(\d{1,3})\.\s*\((\d)\)')

ANSWER_HEADERS_2018 = [
    ('english_grammar', 'englishgrammarandcorrectusagetestanswers'),
    ('vocabulary', 'englishvocabularyanswers'),
    ('spelling_idioms', 'correctspellingandidiomaticexpressionsanswers'),
    ('analogy', 'analogyandlogicanswers'),
    ('reading', 'readingcomprehensionanswers'),
    ('paragraph_org', 'paragraphorganizationanswers'),
    ('numerical', 'numericalreasoningcorrectanswers'),
    ('clerical', 'clericaloperations'),
    ('clerical', 'clericalreasoninganswers'),
    ('constitution', 'philippineconstitution,generalinformation,currenteventsanswers'),
]


def parse_answers_2018(lines):
    sections = {}
    cur = None
    for raw in lines:
        if is_page_mark(raw):
            continue
        text = clean(raw)
        if not text:
            continue
        low = WS.sub('', text.lower())
        switched = False
        for sec, prefix in ANSWER_HEADERS_2018:
            if low.startswith(prefix):
                cur = sec
                sections[cur] = {'number': {}, 'answer_text': {}, 'text': []}
                switched = True
                break
        if switched:
            continue
        if cur is None:
            continue
        if cur == 'reading':
            m = re.match(r'^(\d{1,3})\.\s*(.*)$', text)
            if m:
                sections[cur]['text'].append((int(m.group(1)), m.group(2)))
            continue
        for mm in ANS_2018.finditer(text):
            sections[cur]['number'][int(mm.group(1))] = int(mm.group(2))
            sections[cur]['answer_text'][int(mm.group(1))] = text[mm.end():].strip()
    return sections


# ---------------- Answers: 2019/2020 ----------------

ANS_LE = re.compile(r'^(\d{1,3})(?:\.\)|\.|\))\s*(?:\((\d)\)|([a-e])\W*)\s*(.*)$', re.IGNORECASE)


def parse_answers_flat(lines):
    entries = []
    for raw in lines:
        if is_page_mark(raw):
            continue
        text = clean(raw)
        if not text:
            continue
        if detect_section(text) or is_noise(text):
            continue
        m = ANS_LE.match(text)
        if m:
            num = int(m.group(1))
            digit = m.group(2)
            letter = m.group(3)
            rest = m.group(4).strip()
            entries.append((num, digit if digit else (letter.lower() if letter else ''), rest))
    return entries


# ---------------- Section configs ----------------

YEAR_CONFIG = {
    '2018': {
        'answers_start': 1515,
        'boundaries': [
            ('english_grammar', 53), ('vocabulary', 198), ('spelling_idioms', 318),
            ('analogy', 388), ('reading', 536), ('paragraph_org', 764),
            ('numerical', 874), ('clerical', 1057), ('constitution', 1246),
        ],
        'ranges': None,
    },
    '2019': {
        'answers_start': 2234,
        'test_begins': 215,
        'para_slice': (1063, 1241),
        'ranges': [
            ('graphs', 1, 10), ('vocabulary', 11, 30), ('idiomatic', 31, 50),
            ('analogy', 51, 70), ('reading', 76, 95), ('paragraph_org', 96, 110),
            ('clerical', 111, 120), ('constitution', 121, 135),
            ('numerical', 136, 210),
        ],
    },
    '2020': {
        'answers_start': 2177,
        'test_begins': 206,
        'para_slice': (1250, 1420),
        'ranges': [
            ('graphs', 1, 10), ('vocabulary', 11, 30), ('idiomatic', 31, 50),
            ('analogy', 51, 70), ('reading', 71, 90), ('paragraph_org', 91, 105),
            ('clerical', 106, 115), ('constitution', 116, 130),
            ('numerical', 131, 180),
        ],
    },
}

SECTION_ORDER = ['english_grammar', 'vocabulary', 'spelling_idioms', 'analogy',
                 'reading', 'paragraph_org', 'numerical', 'clerical', 'constitution']


def apply_scored(qs, answers):
    """answers: list of (num, k, text). Pick number-based or order-based mapping by
    option-text containment score. Returns list of questions with 'a' set."""
    answers = [a for a in answers if a[1]]
    qs = sorted(qs, key=lambda q: q['order'])

    def score(ans_for_q):
        s = 0
        for q in qs:
            a = ans_for_q.get(id(q))
            if a is None:
                continue
            k, text = a
            if not text or not (1 <= k <= len(q['opts'])):
                continue
            opt = WS.sub('', q['opts'][k - 1]['value'].lower())
            ans = WS.sub('', text.lower())
            if opt and ans and (opt in ans or ans in opt):
                s += 1
        return s

    number_based = {}
    by_num = {a[0]: a for a in answers}
    for q in qs:
        a = by_num.get(q['num'])
        if a:
            number_based[id(q)] = (a[1], a[2])

    order_based = {}
    for i, q in enumerate(qs):
        if i < len(answers):
            order_based[id(q)] = (answers[i][1], answers[i][2])

    use_number = score(number_based) >= score(order_based)
    ans_for_q = number_based if use_number else order_based
    keep = []
    for q in qs:
        a = ans_for_q.get(id(q))
        if not a:
            continue
        k, _ = a
        if not (1 <= k <= len(q['opts'])):
            continue
        q['a'] = k - 1
        keep.append(q)
    return keep


def build_2018(dump):
    raw = read_lines(DUMPS[dump])
    a0 = YEAR_CONFIG['2018']['answers_start']
    boundaries = YEAR_CONFIG['2018']['boundaries']

    def sec_at(idx):
        sec = boundaries[0][0]
        for s, line in boundaries:
            if idx >= line:
                sec = s
            else:
                break
        return sec

    questions = parse_numbered(raw[:a0], sec_at=sec_at)
    anssecs = parse_answers_2018(raw[a0:])

    by_section = {}
    for q in questions:
        by_section.setdefault(q['sec'], []).append(q)

    out = {}
    for sec in SECTION_ORDER:
        qs = by_section.get(sec, [])
        ans = anssecs.get(sec)
        if sec == 'reading':
            keep = []
            if ans:
                textmap = dict(ans['text'])
                for q in qs:
                    at = textmap.get(q['num'])
                    if not at:
                        continue
                    ai = match_text_answer(q, at)
                    if ai is None:
                        continue
                    q['a'] = ai
                    keep.append(q)
            out[sec] = keep
        elif ans:
            atext = ans.get('answer_text', {})
            answers = [(n, k, atext.get(n, '')) for n, k in ans['number'].items()]
            out[sec] = apply_scored(qs, answers)
        else:
            out[sec] = []

    out['paragraph_org'] = post_paragraph(out.get('paragraph_org', []))
    out['clerical'] = merge_clerical_q6(out.get('clerical', []))
    return out


def match_text_answer(q, ans_text):
    na = WS.sub('', ans_text.lower())
    for i, o in enumerate(q['opts']):
        no = WS.sub('', o['value'].lower())
        if na and (na in no or no in na):
            return i
    return None


def post_paragraph(qs):
    out = []
    for q in qs:
        if not q['text']:
            continue
        q['text'] = [' '.join(q['text'])]
        out.append(q)
    return out


def merge_clerical_q6(qs):
    qs = sorted(qs, key=lambda q: q['order'])
    merged = []
    i = 0
    while i < len(qs):
        q = qs[i]
        nxt = qs[i + 1] if i + 1 < len(qs) else None
        if (nxt and not nxt['text'] and len(nxt['opts']) == 4 and
                all(re.match(r'^\d,\d,\d,\d$', o['value']) for o in nxt['opts'])):
            q['opts'] = nxt['opts']
            i += 2
            merged.append(q)
            continue
        merged.append(q)
        i += 1
    return merged


def build_2019_2020(dump):
    cfg = YEAR_CONFIG[dump]
    raw = read_lines(DUMPS[dump])
    a0 = cfg['answers_start']
    qpart = raw[:a0]

    para_a, para_b = cfg['para_slice']
    para_lines = qpart[para_a:para_b]
    other_lines = qpart[:para_a] + qpart[para_b:]

    qlettered = parse_lettered(other_lines)
    qnumbered = parse_numbered(para_lines)
    for q in qnumbered:
        qlettered[q['num']] = q

    entries = parse_answers_flat(raw[a0:])
    by_section = {name: [] for name, _, _ in cfg['ranges']}
    for e in entries:
        num = e[0]
        for name, lo, hi in cfg['ranges']:
            if lo <= num <= hi:
                by_section[name].append((num, e[1], e[2]))
                break

    out = {}
    for name, lo, hi in cfg['ranges']:
        if name == 'graphs':
            continue
        keep = []
        for num, label, rest in sorted(by_section[name], key=lambda x: x[0]):
            q = qlettered.get(num)
            if q is None:
                continue
            if label.isdigit():
                k = int(label)
                if not (1 <= k <= len(q['opts'])):
                    continue
                q['a'] = k - 1
            else:
                idx = next((i for i, o in enumerate(q['opts']) if o['label'] == label), None)
                if idx is None:
                    continue
                q['a'] = idx
            keep.append(q)
        out[name] = keep
    return out


def main():
    result = {}
    for year in ('2018', '2019', '2020'):
        print('====', year, '====')
        if year == '2018':
            data = build_2018(year)
        else:
            data = build_2019_2020(year)
        total = 0
        for sec, qs in data.items():
            n = len(qs)
            total += n
            bad = sum(1 for q in qs if 'a' not in q or not q['opts'])
            print('  %-16s %3d  (bad=%d)' % (sec, n, bad))
        print('  total:', total)
        result[year] = data
    with open(os.path.join(TEMP, 'parsed_years.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print('wrote parsed_years.json')


if __name__ == '__main__':
    main()
