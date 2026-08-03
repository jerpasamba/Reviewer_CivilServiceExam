import fitz
import json
import re

REL = 'ilide.info-civil-service-exam-reviewer-for-2026-pr_9267b51c57b00c6302380d841a15e459.pdf'
doc = fitz.open(REL)

def norm0(t):
    return re.sub(r'[\s\u00a0]', '', t).lower()

def page_spans(pidx):
    page = doc[pidx]
    d = page.get_text('dict')
    out = []
    for block in d['blocks']:
        if 'lines' not in block:
            continue
        for line in block['lines']:
            for span in line['spans']:
                txt = span['text']
                col = span['color']
                r = (col >> 16) & 255
                g = (col >> 8) & 255
                b = col & 255
                is_red = r > 150 and g < 110 and b < 110
                y = span['origin'][1]
                x = span['origin'][0]
                if txt.strip():
                    out.append({'y': y, 'x': x, 't': txt, 'r': is_red})
    out.sort(key=lambda s: (round(s['y'], 1), s['x']))
    return out

def group_lines(spans):
    lines = []
    for s in spans:
        if lines and abs(lines[-1]['y'] - s['y']) < 3:
            lines[-1]['spans'].append(s)
        else:
            lines.append({'y': s['y'], 'spans': [s]})
    for ln in lines:
        ln['spans'].sort(key=lambda s: s['x'])
        ln['text'] = ''.join(sp['t'] for sp in ln['spans'])
        ln['x0'] = ln['spans'][0]['x']
        ln['n0'] = norm0(ln['text'])
    return lines

QNUM_STRICT = r'^(\d{1,3})\.(?:\s|$)'
QNUM_LOOSE = r'^(\d{1,3})\.\s*\S'

def stream_lines(page_range):
    out = []
    for p in page_range:
        h = doc[p].rect.height
        for ln in group_lines(page_spans(p)):
            if re.match(r'^P\s*a\s*g\s*e\s*\|\s*\d+', ln['text']):
                continue
            if ln['x0'] > 460:
                continue
            ln['ay'] = p * h + ln['y']
            out.append(ln)
    return out

def near_start(ln, title):
    return ln['n0'].startswith(title) or (title in ln['n0'] and ln['n0'].find(title) < 30)

PASSAGE_RE = re.compile(r'^[A-Z]{1,4}\.(?:\s|$)')

def collect_questions(lines, start_title=None, stop_title=None, qnum_re=QNUM_STRICT, start_after_re=None, qstart_max_x0=None, passage_x0_max=None):
    started = start_title is None
    gate = start_after_re is None
    questions = []
    cur = None
    passage = None
    in_passage = False
    for ln in lines:
        if stop_title and near_start(ln, stop_title):
            break
        if start_title and not started:
            if near_start(ln, start_title):
                started = True
            continue
        if not started:
            continue
        if not gate:
            if start_after_re and re.match(start_after_re, ln['text']):
                gate = True
            else:
                continue
        if qstart_max_x0 is not None and ln['x0'] >= qstart_max_x0:
            if cur is not None:
                cur['lines'].append(ln)
            continue
        m = re.match(qnum_re, ln['text'])
        if m and m.group(1):
            if cur:
                questions.append(cur)
            cur = {'num': int(m.group(1)), 'lines': [ln]}
            if passage:
                cur['passage'] = ' '.join(passage)
                passage = None
            in_passage = False
            continue
        if passage_x0_max is not None and not in_passage and PASSAGE_RE.match(ln['text']) and ln['x0'] < passage_x0_max:
            if cur:
                questions.append(cur)
                cur = None
            in_passage = True
            passage = [re.sub(r'\s+', ' ', ln['text']).strip()]
            continue
        if in_passage:
            passage.append(re.sub(r'\s+', ' ', ln['text']).strip())
            continue
        if cur is not None:
            cur['lines'].append(ln)
    if cur:
        questions.append(cur)
    return questions

LETTER_RE = re.compile(r'^([a-e])\.')
NUM_RE = re.compile(r'^([1-4])\.(?:\s|$)')
INLINE_RE = re.compile(r'(?<![a-z])([a-e])\.(?=\s|$)', re.IGNORECASE)

def _label_red(ln):
    return any(sp['r'] for sp in ln['spans'][:2])

def _value_red(ln):
    return any(sp['r'] for sp in ln['spans'][1:])

def parse_options(question, allow_numbered=False):
    opts = []
    cur = None
    for ln in question['lines']:
        text = ln['text']
        m = LETTER_RE.match(text)
        numbered = False
        if not m and allow_numbered:
            m = NUM_RE.match(text)
            numbered = bool(m)
        if m:
            label = m.group(1)
            val = text[m.end():].strip()
            if not val and ((cur is not None and cur['label'] == label) or any(o['label'] == label for o in opts)):
                continue
            if cur:
                opts.append(cur)
            cur = {'label': label, 'value': val,
                   'lines': [ln], 'label_red': _label_red(ln), 'value_red': _value_red(ln),
                   'inline': False, 'inline_pos': None}
        else:
            if cur is not None:
                cur['value'] += ' ' + text.strip()
                cur['lines'].append(ln)
                if any(sp['r'] for sp in ln['spans']):
                    cur['value_red'] = True
    if cur:
        opts.append(cur)
    if opts:
        opts = _recover_inline(question, opts)
        opts = _split_embedded(opts)
    for o in opts:
        o['value'] = re.sub(r'\s+', ' ', o['value']).strip()
    return opts

EMBED_RE = re.compile(r'\s([a-e])\.(?=\s)')

def _split_embedded(opts):
    out = []
    for o in opts:
        pieces = EMBED_RE.split(o['value'])
        if len(pieces) < 3:
            out.append(o)
            continue
        cur_label = o['label']
        cur_val = pieces[0].strip()
        segments = []
        i = 1
        while i < len(pieces):
            lbl = pieces[i]
            nxt = pieces[i + 1]
            if lbl > cur_label:
                segments.append((cur_label, cur_val))
                cur_label = lbl
                cur_val = nxt.strip()
            else:
                cur_val = (cur_val + ' ' + lbl + '.' + nxt).strip()
            i += 2
        segments.append((cur_label, cur_val))
        if len(segments) < 2:
            out.append(o)
            continue
        for k, (lbl, val) in enumerate(segments):
            no = dict(o)
            no['label'] = lbl
            no['value'] = val
            no['label_red'] = (k == 0 and o['label_red'])
            no['value_red'] = False
            no['embedded'] = True
            out.append(no)
    return out

def _recover_inline(question, opts):
    labels = [o['label'] for o in opts]
    if all(l in 'abcde' for l in labels):
        first = labels[0]
        if first != 'a' and ord(first) > ord('a') + 0:
            target = chr(ord(first) - 1)
            return _insert_inline(question, opts, target)
    return opts

def _insert_inline(question, opts, target):
    first_opt_line = opts[0]['lines'][0]
    for ln in question['lines']:
        if ln is first_opt_line:
            break
        matches = list(INLINE_RE.finditer(ln['text']))
        m = matches[-1] if matches else None
        if m and m.group(1) == target:
            pos = m.end()
            rest = ln['text'][pos:].strip()
            label_red = False
            value_red = False
            for sp in ln['spans']:
                if sp['r']:
                    if re.match(r'^%s\.' % target, sp['t'].strip()):
                        label_red = True
                    else:
                        value_red = True
            newopt = {'label': target, 'value': rest, 'lines': [ln],
                      'label_red': label_red, 'value_red': value_red,
                      'inline': True, 'inline_pos': m.start()}
            after_this = False
            for ln2 in question['lines']:
                if ln2 is ln:
                    after_this = True
                    continue
                if not after_this:
                    continue
                if LETTER_RE.match(ln2['text']):
                    break
                newopt['value'] += ' ' + ln2['text'].strip()
                newopt['lines'].append(ln2)
                if any(sp['r'] for sp in ln2['spans']):
                    newopt['value_red'] = True
            opts.insert(0, newopt)
            break
    return opts

def build_qtext(q, opts):
    first_opt = opts[0]
    qtext_parts = []
    for ln in q['lines']:
        if ln is first_opt['lines'][0]:
            if first_opt['inline'] and first_opt['inline_pos'] is not None:
                qtext_parts.append(ln['text'][:first_opt['inline_pos']])
            break
        qtext_parts.append(ln['text'])
    qtext = ' '.join(qtext_parts)
    qtext = re.sub(r'^\s*\d+\.\s*', '', qtext)
    qtext = re.sub(r'\s+', ' ', qtext).strip()
    return qtext

def find_answer_index(opts, qlines):
    if not opts:
        return None
    for i, o in enumerate(opts):
        if o['label_red']:
            return i
    for i, o in enumerate(opts):
        if o['value_red'] and o['value']:
            return i
    for ln in qlines:
        for sp in ln['spans']:
            if not sp['r']:
                continue
            m = re.match(r'^([a-e])\.', sp['t'].strip())
            if m:
                letter = m.group(1)
                for i, o in enumerate(opts):
                    if o['label'] == letter:
                        return i
    for ln in qlines:
        for sp in ln['spans']:
            if not sp['r']:
                continue
            tv = norm0(sp['t'])
            if len(tv) < 2:
                continue
            for i, o in enumerate(opts):
                ov = norm0(o['value'])
                if ov and (tv in ov or ov in tv):
                    return i
    return None

def _finalize(q, opts):
    if not opts:
        return None
    qtext = build_qtext(q, opts)
    if not qtext:
        return None
    ans = find_answer_index(opts, q['lines'])
    ans_label = opts[ans]['label'] if ans is not None else None
    cleaned = []
    for o in opts:
        if o['value'] == '' and o['label'] != ans_label:
            continue
        cleaned.append(o)
    ans = None
    if ans_label is not None:
        for i, o in enumerate(cleaned):
            if o['label'] == ans_label:
                ans = i
                break
    out = {'n': q['num'], 'q': qtext, 'o': [o['value'] for o in cleaned], 'a': ans}
    if q.get('passage'):
        out['p'] = q['passage']
    return out

def make_standard(prange, start_title=None, stop_title=None, allow_numbered=True, qstart_max_x0=None, passage_x0_max=None):
    lines = stream_lines(prange)
    result = []
    for q in collect_questions(lines, start_title, stop_title, qstart_max_x0=qstart_max_x0, passage_x0_max=passage_x0_max):
        opts = parse_options(q, allow_numbered=allow_numbered and q['num'] > 4)
        r = _finalize(q, opts)
        if r:
            result.append(r)
    return result

def make_reading(prange, start_title=None, stop_title=None, passage_x0_max=100):
    lines = stream_lines(prange)
    result = []
    for q in collect_questions(lines, start_title, stop_title,
                               start_after_re=r'^[A-Z]{1,4}\.\s', passage_x0_max=passage_x0_max):
        opts = parse_options(q)
        r = _finalize(q, opts)
        if r:
            result.append(r)
    return result

def make_ds(prange):
    lines = stream_lines(prange)
    opts = []
    cur = None
    qs = []
    cur_q = None
    started = False
    for ln in lines:
        if near_start(ln, 'clericaloperations'):
            break
        if near_start(ln, 'datasufficiency'):
            started = True
            continue
        if not started:
            continue
        m = re.match(QNUM_STRICT, ln['text'])
        if m and m.group(1):
            if cur_q:
                qs.append(cur_q)
            cur_q = {'num': int(m.group(1)), 'lines': [ln]}
            continue
        if cur_q is None:
            m2 = re.match(r'^([a-e])\.\s*(.*)$', ln['text'])
            if m2:
                cur = {'letter': m2.group(1), 'value': m2.group(2).strip()}
                opts.append(cur)
            else:
                if cur is not None:
                    cur['value'] += ' ' + ln['text'].strip()
            continue
        cur_q['lines'].append(ln)
    if cur_q:
        qs.append(cur_q)
    result = []
    for q in qs:
        ans = None
        for ln in q['lines']:
            for sp in ln['spans']:
                if not sp['r']:
                    continue
                t = sp['t'].strip()
                m = re.match(r'^([a-e])\.', t)
                if m:
                    ans = m.group(1)
                    break
                nv = norm0(t)
                if nv and len(nv) >= 2:
                    for o in opts:
                        if nv in norm0(o['value']) or norm0(o['value']) in nv:
                            ans = o['letter']
                            break
                if ans:
                    break
            if ans:
                break
        text_parts = []
        for ln in q['lines']:
            if re.match(r'^Answer', ln['text']):
                continue
            if re.match(r'^\d+\)', ln['text']):
                continue
            text_parts.append(ln['text'])
        qtext = re.sub(r'\s+', ' ', ' '.join(text_parts))
        qtext = re.sub(r'^\s*\d+\.\s*', '', qtext).strip()
        if qtext:
            idx = None
            if ans:
                for i, o in enumerate(opts):
                    if o['letter'] == ans:
                        idx = i
                        break
            result.append({'n': q['num'], 'q': qtext, 'o': [o['value'] for o in opts], 'a': idx})
    return result

def make_ie(prange, start_title=None, stop_title=None):
    lines = stream_lines(prange)
    result = []
    for q in collect_questions(lines, start_title, stop_title, qnum_re=QNUM_LOOSE):
        letters = set()
        ans_letter = None
        for ln in q['lines']:
            for sp in ln['spans']:
                m = re.match(r'^([a-e])\.?$', sp['t'].strip())
                if m:
                    letters.add(m.group(1))
                    if sp['r']:
                        ans_letter = m.group(1)
        text_parts = []
        for ln in q['lines']:
            if re.match(r'^[a-e]([.\s]*[a-e])*\.?\s*$', ln['text'].strip()):
                continue
            text_parts.append(ln['text'])
        qtext = re.sub(r'\s+', ' ', ' '.join(text_parts)).strip()
        qtext = re.sub(r'^\s*\d+\.\s*', '', qtext)
        if not qtext:
            continue
        ordered = [c for c in 'abcde' if c in letters]
        opts = [c.upper() for c in ordered] if ordered else ['A', 'B', 'C', 'D', 'E']
        ans = None
        if ans_letter and ans_letter in ordered:
            ans = ordered.index(ans_letter)
        result.append({'n': q['num'], 'q': qtext, 'o': opts, 'a': ans})
    return result

def make_mali(prange, start_title=None, stop_title=None):
    lines = stream_lines(prange)
    result = []
    for q in collect_questions(lines, start_title, stop_title):
        letter_tokens = []
        for ln in q['lines']:
            for m in re.finditer(r'(?<![\w])([a-e])(?=[\s.,]|$)', ln['text']):
                letter_tokens.append(m.group(1))
        seen = []
        for l in letter_tokens:
            if l not in seen:
                seen.append(l)
        ans_letter = None
        for ln in q['lines']:
            for sp in ln['spans']:
                if not sp['r']:
                    continue
                m = re.match(r'^([a-e])\.?\s*$', sp['t'].strip())
                if m:
                    ans_letter = m.group(1)
                else:
                    m2 = re.match(r'^([a-e])\s', sp['t'].strip())
                    if m2:
                        ans_letter = m2.group(1)
        text_parts = []
        for ln in q['lines']:
            if re.match(r'^[a-e](?:[\s.,]+[a-e])*[\s.,]*$', ln['text'].strip()):
                continue
            text_parts.append(ln['text'])
        qtext = re.sub(r'\s+', ' ', ' '.join(text_parts)).strip()
        qtext = re.sub(r'^\s*\d+\.\s*', '', qtext)
        if not qtext:
            continue
        opts = [l.upper() for l in sorted(seen)] if len(seen) >= 2 else ['A', 'B', 'C', 'D', 'E']
        ans = None
        if ans_letter and ans_letter in seen:
            ans = seen.index(ans_letter)
        result.append({'n': q['num'], 'q': qtext, 'o': opts, 'a': ans})
    return result

SECTIONS = [
    ('math_word_problems', range(3, 20), 'standard', 'wordproblemsandoperations', 'datasufficiency'),
    ('data_sufficiency', range(19, 25), 'ds', None, None),
    ('alphabetizing', range(24, 33), 'standard', 'clericaloperations', 'synonyms', {'qstart_max_x0': 100}),
    ('synonyms', range(32, 41), 'standard', 'synonyms', 'antonyms'),
    ('antonyms', range(40, 49), 'standard', 'antonyms', 'single-wordanalogy'),
    ('single_word_analogy', range(48, 57), 'standard', 'single-wordanalogy', 'double-wordanalogy'),
    ('double_word_analogy', range(56, 65), 'standard', 'double-wordanalogy', 'identifyingerrors'),
    ('identifying_errors', range(64, 72), 'ie', 'identifyingerrors', 'paragraphdevelopment'),
    ('paragraph_development', range(71, 75), 'standard', 'paragraphdevelopment', 'correctusage'),
    ('correct_usage', range(74, 83), 'standard', 'correctusage', 'readingcomprehension'),
    ('reading_comprehension', range(82, 100), 'reading', 'readingcomprehension', 'kasingkahulugan', {'passage_x0_max': 100}),
    ('kasingkahulugan', range(99, 105), 'standard', 'kasingkahulugan', 'kasalungat'),
    ('kasalungat', range(104, 110), 'standard', 'kasalungat', 'kawikaan'),
    ('kawikaan', range(109, 115), 'standard', 'kawikaan', 'wastonggamit'),
    ('wastong_gamit', range(114, 121), 'standard', 'wastonggamit', 'pagkilalasamali'),
    ('pagkilala_sa_mali', range(120, 124), 'mali', 'pagkilalasamali', 'pag-unawasabinasa'),
    ('pag_unawa_sa_binasa', range(123, 134), 'standard', 'pag-unawasabinasa', 'pagtatalata', {'passage_x0_max': 100}),
    ('pagtatalata', range(133, 137), 'standard', 'pagtatalata', 'constitution', {'passage_x0_max': 100}),
    ('constitution', range(136, 143), 'standard', 'constitution', 'inductivereasoning'),
    ('inductive_reasoning', range(142, 152), 'standard', 'inductivereasoning', 'abstractreasoning'),
]

OVERRIDES = {
    ('math_word_problems', 71): {'o': ['weight', 'perimeter', 'volume', 'area'], 'a': 1},
    ('pagkilala_sa_mali', 2): {'o': ['A', 'B', 'C', 'D', 'E'], 'a': 4},
    ('identifying_errors', 17): {'o': ['A', 'B', 'C', 'D', 'E'], 'a': 0},
    ('constitution', 22): {'o': ['April 15', 'April 30', 'March 15', 'March 30'], 'a': 0},
}

SKIP = {
    ('math_word_problems', 25),
    ('math_word_problems', 31),
}

def build():
    out = {}
    for row in SECTIONS:
        name, prange, kind, start, stop = row[:5]
        kwargs = row[5] if len(row) > 5 else {}
        if kind == 'standard':
            qs = make_standard(prange, start, stop, **kwargs)
        elif kind == 'ds':
            qs = make_ds(prange)
        elif kind == 'ie':
            qs = make_ie(prange, start, stop)
        elif kind == 'reading':
            qs = make_reading(prange, start, stop, **kwargs)
        else:
            qs = make_mali(prange, start, stop)
        kept = []
        for q in qs:
            key = (name, q['n'])
            if key in SKIP:
                continue
            if key in OVERRIDES:
                q = dict(q)
                q.update(OVERRIDES[key])
            kept.append(q)
        out[name] = kept
        no_ans = [q['n'] for q in kept if q['a'] is None]
        nums = [q['n'] for q in kept]
        print('%s: %d q, noans=%s, nums=%s..%s' % (name, len(kept), no_ans,
              (min(nums) if nums else '-'), (max(nums) if nums else '-')))
    return out

if __name__ == '__main__':
    out = build()
    with open(r'C:\Users\JERMAI~1\AppData\Local\Temp\opencode\parsed5.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('saved parsed5.json')
