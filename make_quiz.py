# -*- coding: utf-8 -*-
import json

SRC = r'C:\Users\JERMAI~1\AppData\Local\Temp\opencode\parsed5.json'
OUT = r'D:\VS_Code_Repositories\CiviilServiceReviewer\quiz.html'

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

GROUPS = [
    ('Mathematics', [('math_word_problems', 'Math Word Problems'),
                     ('data_sufficiency', 'Data Sufficiency')]),
    ('Clerical Operations', [('alphabetizing', 'Alphabetizing')]),
    ('English Vocabulary', [('synonyms', 'Synonyms'),
                            ('antonyms', 'Antonyms')]),
    ('English & Reading', [('single_word_analogy', 'Single Word Analogy'),
                           ('double_word_analogy', 'Double Word Analogy'),
                           ('identifying_errors', 'Identifying Errors'),
                           ('paragraph_development', 'Paragraph Development'),
                           ('correct_usage', 'Correct Usage'),
                           ('reading_comprehension', 'Reading Comprehension')]),
    ('Filipino', [('kasingkahulugan', 'Kasingkahulugan'),
                  ('kasalungat', 'Kasalungat'),
                  ('kawikaan', 'Kawikaan'),
                  ('wastong_gamit', 'Wastong Gamit'),
                  ('pagkilala_sa_mali', 'Pagkilala sa Mali'),
                  ('pag_unawa_sa_binasa', 'Pag-unawa sa Binasa'),
                  ('pagtatalata', 'Pagtatalata')]),
    ('Civics / General Information', [('constitution', 'Constitution')]),
    ('Abstract Reasoning', [('inductive_reasoning', 'Inductive Reasoning')]),
]

data_json = json.dumps(data, ensure_ascii=False)
data_json = data_json.replace('</', '<\\/')
groups_json = json.dumps(GROUPS, ensure_ascii=False)
groups_json = groups_json.replace('</', '<\\/')

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSC Civil Service Exam Reviewer 2026 - Quiz</title>
<style>
  :root {
    --bg: #f1f5f9; --card: #ffffff; --ink: #1e293b; --muted: #64748b;
    --line: #e2e8f0; --accent: #2563eb; --accent2: #1d4ed8;
    --good: #16a34a; --bad: #dc2626; --warn: #d97706;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
  }
  .wrap { max-width: 760px; margin: 0 auto; padding: 16px; }
  header {
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    color: #fff; padding: 18px 20px; border-radius: 14px;
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  }
  header h1 { margin: 0; font-size: 1.15rem; font-weight: 700; }
  header .sub { font-size: .8rem; opacity: .85; }
  .btn {
    border: 0; border-radius: 10px; cursor: pointer; font-size: .9rem;
    font-weight: 600; padding: 9px 14px; background: var(--accent); color: #fff;
    transition: filter .12s;
  }
  .btn:hover { filter: brightness(1.08); }
  .btn.ghost { background: transparent; color: var(--accent); border: 1.5px solid var(--accent); }
  .btn.ghost2 { background: var(--card); color: var(--ink); border: 1.5px solid var(--line); }
  .btn:disabled { opacity: .5; cursor: default; }
  .group { margin: 22px 0 6px; font-size: .78rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
  .card {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 14px 16px; margin: 8px 0; cursor: pointer;
    display: flex; align-items: center; justify-content: space-between; gap: 10px;
    transition: box-shadow .12s, transform .12s;
  }
  .card:hover { box-shadow: 0 3px 10px rgba(2,6,23,.08); transform: translateY(-1px); }
  .card .name { font-weight: 600; font-size: .98rem; }
  .card .cnt { color: var(--muted); font-size: .82rem; }
  .bar { height: 6px; border-radius: 4px; background: #e7ecf3; margin-top: 8px; overflow: hidden; }
  .bar > div { height: 100%; background: var(--accent); border-radius: 4px; }
  .pct { font-size: .78rem; font-weight: 700; color: var(--muted); white-space: nowrap; }
  .pct.done { color: var(--good); }
  .mockcard {
    background: linear-gradient(135deg, #0f172a, #334155);
    color: #fff; border-radius: 12px; padding: 16px 18px; margin: 14px 0;
    cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 10px;
    border: 1px solid #1e293b; transition: box-shadow .12s, transform .12s;
  }
  .mockcard:hover { box-shadow: 0 5px 16px rgba(2,6,23,.25); transform: translateY(-1px); }
  .mockcard .name { font-weight: 800; font-size: 1.05rem; }
  .mockcard .cnt { font-size: .8rem; opacity: .8; margin-top: 2px; }
  .mockcard .play { background: var(--accent); border-radius: 999px; width: 42px; height: 42px;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex: 0 0 auto; }
  .topline { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
  .topline .title { font-weight: 700; font-size: 1.02rem; flex: 1; }
  .timer {
    background: #0f172a; color: #4ade80; font-family: ui-monospace, Consolas, monospace;
    font-weight: 700; font-size: 1.05rem; padding: 6px 14px; border-radius: 999px;
    white-space: nowrap; letter-spacing: .02em;
  }
  .timer.urgent { background: var(--bad); color: #fff; animation: pulse 1s infinite; }
  @keyframes pulse { 50% { opacity: .75; } }
  .qmeta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }
  .badge { background: var(--accent); color: #fff; border-radius: 999px;
    font-size: .74rem; font-weight: 700; padding: 3px 10px; }
  .badge.warn { background: var(--warn); }
  .badge.gray { background: #94a3b8; }
  .scoreline { font-size: .85rem; color: var(--muted); }
  .qtext { font-size: 1.06rem; font-weight: 600; margin: 6px 0 14px; }
  .passage {
    background: #f8fafc; border: 1px solid var(--line); border-left: 4px solid var(--accent);
    border-radius: 10px; padding: 12px 14px; margin: 10px 0; font-size: .92rem;
    white-space: pre-wrap; color: #334155; max-height: 220px; overflow: auto;
  }
  .opt {
    display: block; width: 100%; text-align: left; margin: 8px 0;
    background: var(--card); border: 1.5px solid var(--line); border-radius: 10px;
    padding: 12px 14px; font-size: .96rem; cursor: pointer; color: var(--ink);
    transition: border-color .12s, background .12s;
  }
  .opt:hover:not(:disabled) { border-color: var(--accent); }
  .opt:disabled { cursor: default; }
  .opt .letter { font-weight: 700; margin-right: 8px; color: var(--muted); }
  .opt.correct { border-color: var(--good); background: #f0fdf4; }
  .opt.correct .letter { color: var(--good); }
  .opt.wrong { border-color: var(--bad); background: #fef2f2; }
  .opt.wrong .letter { color: var(--bad); }
  .opt.reveal { border-color: var(--good); background: #f0fdf4; }
  .fb { margin: 12px 0; padding: 12px 14px; border-radius: 10px; font-weight: 600; font-size: .95rem; }
  .fb.good { background: #f0fdf4; color: var(--good); border: 1px solid #bbf7d0; }
  .fb.bad { background: #fef2f2; color: var(--bad); border: 1px solid #fecaca; }
  .nav { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
  .nav .spacer { flex: 1; }
  .setrow {
    display: flex; align-items: center; gap: 10px; background: var(--card);
    border: 1px solid var(--line); border-radius: 10px; padding: 10px 14px; margin: 6px 0;
    cursor: pointer; font-size: .95rem;
  }
  .setrow input { accent-color: var(--accent); width: 17px; height: 17px; }
  .setrow .name { font-weight: 600; flex: 1; }
  .setrow .cnt { color: var(--muted); font-size: .8rem; white-space: nowrap; }
  .est {
    background: #eef2ff; border: 1px solid #c7d2fe; color: #3730a3; border-radius: 10px;
    padding: 10px 14px; margin: 12px 0; font-size: .88rem; font-weight: 600;
  }
  .summary-box { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px; text-align: center; margin: 10px 0; }
  .summary-box .big { font-size: 2.4rem; font-weight: 800; }
  .summary-box .big.good { color: var(--good); } .summary-box .big.mid { color: var(--warn); } .summary-box .big.bad { color: var(--bad); }
  .passbar { margin-top: 10px; font-weight: 700; font-size: .9rem; padding: 8px; border-radius: 8px; }
  .passbar.pass { background: #f0fdf4; color: var(--good); border: 1px solid #bbf7d0; }
  .passbar.fail { background: #fef2f2; color: var(--bad); border: 1px solid #fecaca; }
  .review { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; margin: 10px 0; }
  .review .rq { font-weight: 600; margin-bottom: 6px; }
  .review .ra { font-size: .9rem; color: var(--good); }
  .small { font-size: .8rem; color: var(--muted); }
  .foot { text-align: center; color: var(--muted); font-size: .78rem; margin: 24px 0 10px; }
  .toast { position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
    background: #0f172a; color: #fff; padding: 10px 16px; border-radius: 10px;
    font-size: .85rem; opacity: 0; transition: opacity .2s; pointer-events: none; z-index: 10; }
  .toast.show { opacity: 1; }
</style>
</head>
<body>
<div class="wrap" id="app"></div>
<div class="toast" id="toast"></div>
<script>
const DATA = __DATA__;
const GROUPS = __GROUPS__;
const LS_KEY = 'csc2026_progress_v1';
const LEVELS = {
  pro: { name: 'Professional', items: 170, minutes: 190 },
  sub: { name: 'Subprofessional', items: 165, minutes: 160 }
};
const ALL_KEYS = [];
for (const g of GROUPS) for (const it of g[1]) ALL_KEYS.push(it[0]);
const SECNAMES = {};
for (const g of GROUPS) for (const it of g[1]) SECNAMES[it[0]] = it[1];

let progress = {};
try { progress = JSON.parse(localStorage.getItem(LS_KEY)) || {}; } catch (e) {}

let quiz = { mode: 'home', flat: [], idx: 0, done: false, ans: null,
             timerOn: false, timeLeft: 0, timeTotal: 0, timeUsed: 0, timedOut: false,
             timerId: null, runAnswered: {}, label: '' };
let setup = { level: 'pro', sections: ALL_KEYS.slice(), timer: 'actual' };
let toastTimer = null;

function secStat(key) {
  const p = progress[key] || {};
  const total = DATA[key].length;
  const answered = Object.keys(p).length;
  const correct = Object.values(p).filter(v => v === 1).length;
  return { total, answered, correct };
}
function saveProgress() { localStorage.setItem(LS_KEY, JSON.stringify(progress)); }
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 1800);
}
function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}
function fmt(sec) {
  const s = Math.max(0, Math.round(sec));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
  const mm = String(m).padStart(2, '0'), ss = String(x).padStart(2, '0');
  return h ? h + ':' + mm + ':' + ss : mm + ':' + ss;
}
function fmtH(min) {
  if (min < 60) return min + 'm';
  const h = Math.floor(min / 60), m = min % 60;
  return m ? h + 'h ' + m + 'm' : h + 'h';
}

function render() {
  const app = document.getElementById('app');
  if (quiz.mode === 'home') app.innerHTML = homeHTML();
  else if (quiz.mode === 'mock-setup') app.innerHTML = mockSetupHTML();
  else if (quiz.mode === 'summary' || quiz.done) app.innerHTML = summaryHTML();
  else app.innerHTML = quizHTML();
  renderTimerBadge();
}

/* ---------- HOME ---------- */
function homeHTML() {
  let totalQ = 0, answeredQ = 0;
  for (const k in DATA) { const st = secStat(k); totalQ += st.total; answeredQ += st.answered; }
  let h = '<header><div><h1>CSC Civil Service Exam Reviewer 2026</h1>' +
          '<div class="sub">Offline interactive quiz &middot; ' + totalQ + ' questions &middot; passing rating 80%</div></div></header>';
  h += '<div class="mockcard" onclick="startMock()">' +
       '<div><div class="name">Mock Exam</div>' +
       '<div class="cnt">Timed practice at the real CSE pace (170 items / 3h10m) or with extra time</div></div>' +
       '<div class="play">&#9654;</div></div>';
  let inner = '';
  for (const [gname, items] of GROUPS) {
    inner += '<div class="group">' + esc(gname) + '</div>';
    for (const [key, label] of items) {
      const st = secStat(key);
      const pct = st.total ? Math.round(st.answered / st.total * 100) : 0;
      const done = st.answered === st.total;
      inner += '<div class="card" onclick="startSection(' + JSON.stringify(key) + ')">' +
        '<div style="flex:1"><div class="name">' + esc(label) + '</div>' +
        '<div class="cnt">' + st.answered + '/' + st.total + ' answered &middot; ' + st.correct + ' correct</div>' +
        '<div class="bar"><div style="width:' + pct + '%"></div></div></div>' +
        '<div class="pct' + (done ? ' done' : '') + '">' + pct + '%</div></div>';
    }
  }
  h += inner;
  h += '<div class="foot">' + answeredQ + '/' + totalQ + ' questions attempted across all sections &middot; ' +
       '<a href="javascript:void(0)" onclick="resetAll(event)" style="color:var(--bad)">Reset all progress</a></div>';
  return h;
}
function resetAll(ev) {
  if (ev) ev.stopPropagation();
  if (!confirm('Reset all progress?')) return;
  progress = {}; saveProgress(); render();
}
function startSection(key) {
  stopTimer();
  const flat = DATA[key].map((_, i) => ({ sec: key, idx: i }));
  quiz = { mode: 'quiz', flat: flat, idx: 0, done: false, ans: null,
           timerOn: false, timeLeft: 0, timeTotal: 0, timeUsed: 0, timedOut: false,
           timerId: null, runAnswered: {}, label: SECNAMES[key] };
  render();
}

/* ---------- MOCK SETUP ---------- */
function startMock() {
  stopTimer();
  quiz = { mode: 'mock-setup', flat: [], idx: 0, done: false, ans: null,
           timerOn: false, timeLeft: 0, timeTotal: 0, timeUsed: 0, timedOut: false,
           timerId: null, runAnswered: {}, label: 'Mock Exam' };
  render();
}
function paceOf(lvl) { return LEVELS[lvl].minutes / LEVELS[lvl].items; }
function selectedCount() { return setup.sections.reduce((s, k) => s + DATA[k].length, 0); }
function mockSetupHTML() {
  const n = selectedCount();
  const pace = paceOf(setup.level);
  const actual = Math.round(n * pace);
  const beginner = Math.round(actual * 1.5);
  const estLine = setup.timer === 'none' ? 'no timer (untimed practice)'
    : setup.timer === 'actual'
      ? 'time &asymp; <b>' + fmtH(actual) + '</b> at the real ' + LEVELS[setup.level].name + ' pace'
      : 'time &asymp; <b>' + fmtH(beginner) + '</b> (actual ' + fmtH(actual) + ' + 50%)';
  let secs = '';
  for (const [gname, items] of GROUPS) {
    secs += '<div class="group">' + esc(gname) + '</div>';
    for (const [key, label] of items) {
      const st = secStat(key);
      secs += '<label class="setrow"><input type="checkbox" onchange="toggleSec(' + JSON.stringify(key) + ', this.checked)" ' +
              (setup.sections.includes(key) ? 'checked' : '') + '>' +
              '<span class="name">' + esc(label) + '</span><span class="cnt">' + st.total + ' q</span></label>';
    }
  }
  return '<div class="topline"><button class="btn ghost2" onclick="backHome()">&#9776; Home</button>' +
         '<span class="spacer"></span><span class="badge">Mock Exam Setup</span></div>' +
         '<div class="group">Level &middot; sets the real per-item pace</div>' +
         '<label class="setrow"><input type="radio" name="lvl" value="pro" onchange="setLevel(this.value)" ' + (setup.level === 'pro' ? 'checked' : '') + '>' +
         '<span class="name">Professional</span><span class="cnt">170 items &middot; 3h 10m</span></label>' +
         '<label class="setrow"><input type="radio" name="lvl" value="sub" onchange="setLevel(this.value)" ' + (setup.level === 'sub' ? 'checked' : '') + '>' +
         '<span class="name">Subprofessional</span><span class="cnt">165 items &middot; 2h 40m</span></label>' +
         '<div class="group">Timer</div>' +
         '<label class="setrow"><input type="radio" name="tmr" value="actual" onchange="setTimer(this.value)" ' + (setup.timer === 'actual' ? 'checked' : '') + '>' +
         '<span class="name">Actual CSE timing</span><span class="cnt">real exam pace per item</span></label>' +
         '<label class="setrow"><input type="radio" name="tmr" value="beginner" onchange="setTimer(this.value)" ' + (setup.timer === 'beginner' ? 'checked' : '') + '>' +
         '<span class="name">Beginner &middot; more time</span><span class="cnt">50% extra time than the actual exam</span></label>' +
         '<label class="setrow"><input type="radio" name="tmr" value="none" onchange="setTimer(this.value)" ' + (setup.timer === 'none' ? 'checked' : '') + '>' +
         '<span class="name">No timer</span><span class="cnt">untimed practice</span></label>' +
         '<div class="group">Include sections</div>' + secs +
         '<div class="est">' + n + ' questions &middot; ' + estLine + '</div>' +
         '<div class="nav"><button class="btn" ' + (n === 0 ? 'disabled' : 'onclick="beginMock()"') + '>Start Mock Exam &rarr;</button></div>';
}
function toggleSec(k, on) {
  if (on) { if (!setup.sections.includes(k)) setup.sections.push(k); }
  else { setup.sections = setup.sections.filter(x => x !== k); }
  render();
}
function setLevel(l) { setup.level = l; render(); }
function setTimer(t) { setup.timer = t; render(); }
function backHome() { stopTimer(); quiz.mode = 'home'; render(); }
function beginMock() {
  const order = [];
  for (const g of GROUPS) for (const it of g[1]) {
    const key = it[0];
    if (setup.sections.includes(key)) DATA[key].forEach((_, i) => order.push({ sec: key, idx: i }));
  }
  if (!order.length) return;
  quiz = { mode: 'quiz', flat: order, idx: 0, done: false, ans: null,
           timerOn: false, timeLeft: 0, timeTotal: 0, timeUsed: 0, timedOut: false,
           timerId: null, runAnswered: {}, label: 'Mock Exam' };
  if (setup.timer !== 'none') {
    let mins = Math.round(order.length * paceOf(setup.level));
    if (setup.timer === 'beginner') mins = Math.round(mins * 1.5);
    const secs = mins * 60;
    quiz.timerOn = true; quiz.timeLeft = secs; quiz.timeTotal = secs;
  }
  render();
  if (quiz.timerOn) quiz.timerId = setInterval(tick, 1000);
}

/* ---------- QUIZ ---------- */
function currentQ() { const e = quiz.flat[quiz.idx]; return DATA[e.sec][e.idx]; }
function flatStat() {
  let answered = 0, correct = 0;
  for (const e of quiz.flat) {
    const p = (progress[e.sec] || {})[DATA[e.sec][e.idx].n];
    if (p !== undefined) { answered++; if (p === 1) correct++; }
  }
  return { total: quiz.flat.length, answered: answered, correct: correct };
}
function quizHTML() {
  const q = currentQ();
  const st = flatStat();
  const total = st.total;
  const pos = quiz.idx + 1;
  const isMock = quiz.label === 'Mock Exam';
  const e = quiz.flat[quiz.idx];
  const curSec = isMock ? 'Mock Exam &middot; ' + SECNAMES[e.sec] : quiz.label;
  const opts = q.o.map((o, i) => {
    const letter = String.fromCharCode(65 + i);
    let cls = 'opt', disp = esc(o), mark = '';
    if (quiz.ans !== null) {
      if (i === q.a) { cls += ' reveal'; mark = ' &#10003;'; }
      else if (i === quiz.ans) { cls += ' wrong'; mark = ' &#10007;'; }
    }
    return '<button class="' + cls + '" ' + (quiz.ans !== null ? 'disabled' : 'onclick="answer(' + i + ')")') + '>' +
           '<span class="letter">' + letter + '.</span>' + disp + mark + '</button>';
  }).join('');
  const passage = q.p ? '<div class="passage">' + esc(q.p) + '</div>' : '';
  const fb = quiz.ans !== null
    ? (quiz.ans === q.a
        ? '<div class="fb good">&#10003; Correct!</div>'
        : '<div class="fb bad">&#10007; Incorrect &mdash; correct answer: ' + String.fromCharCode(65 + q.a) + '.</div>')
    : '';
  const timer = quiz.timerOn
    ? '<span class="timer" id="timer">' + fmt(quiz.timeLeft) + '</span>'
    : '';
  const nav = '<div class="nav">' +
    '<button class="btn ghost2" ' + (pos <= 1 ? 'disabled' : 'onclick="go(-1)"') + '>&#8592; Prev</button>' +
    '<button class="btn ghost2" onclick="shuffle()">Shuffle</button>' +
    '<span class="spacer"></span>' +
    (pos >= total
      ? '<button class="btn" onclick="finish()">Finish &rarr;</button>'
      : '<button class="btn" onclick="go(1)">Next &rarr;</button>') +
    '</div>';
  return '<div class="topline"><button class="btn ghost2" onclick="quit()">&#9776; Home</button>' +
         '<span class="spacer"></span>' + timer + '</div>' +
         '<div class="card" style="cursor:default"><div class="qmeta">' +
         '<span class="badge gray">' + esc(curSec) + '</span>' +
         '<span class="badge">Q' + esc(q.n) + '</span>' +
         '<span class="scoreline">' + pos + ' of ' + total + ' &middot; ' + st.correct + '/' + st.answered + ' correct</span></div></div>' +
         passage +
         '<div class="qtext">' + esc(q.q) + '</div>' + opts + fb + nav;
}
function answer(i) {
  const q = currentQ();
  if (quiz.ans !== null) return;
  quiz.ans = i;
  quiz.runAnswered[quiz.idx] = true;
  const e = quiz.flat[quiz.idx];
  const key = e.sec;
  const cur = progress[key] || {};
  cur[q.n] = (i === q.a) ? 1 : 0;
  progress[key] = cur;
  saveProgress();
  render();
}
function go(d) { quiz.ans = null; quiz.idx += d; render(); }
function shuffle() {
  quiz.ans = null;
  for (let i = quiz.flat.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = quiz.flat[i]; quiz.flat[i] = quiz.flat[j]; quiz.flat[j] = tmp;
  }
  quiz.idx = 0;
  render();
  showToast('Order shuffled');
}
function quit() { stopTimer(); quiz.mode = 'home'; render(); }
function finish() { stopTimer(); quiz.timeUsed = quiz.timeTotal - quiz.timeLeft; quiz.done = true; render(); }
function retry() {
  stopTimer();
  quiz.done = false; quiz.ans = null; quiz.idx = 0; quiz.runAnswered = {};
  if (quiz.timeTotal > 0) { quiz.timerOn = true; quiz.timeLeft = quiz.timeTotal; quiz.timeUsed = 0; }
  render();
  if (quiz.timerOn && !quiz.timerId) quiz.timerId = setInterval(tick, 1000);
}
function tick() {
  if (!quiz.timerOn) return;
  quiz.timeLeft -= 1;
  if (quiz.timeLeft <= 0) { quiz.timeLeft = 0; finish(); return; }
  renderTimerBadge();
}
function renderTimerBadge() {
  const el = document.getElementById('timer');
  if (!el) return;
  el.textContent = fmt(quiz.timeLeft);
  el.classList.toggle('urgent', quiz.timeLeft <= 300);
}
function stopTimer() {
  if (quiz.timerId) { clearInterval(quiz.timerId); quiz.timerId = null; }
}

/* ---------- SUMMARY ---------- */
function summaryHTML() {
  const total = quiz.flat.length;
  let answered = 0, correct = 0, unanswered = 0;
  const wrong = [];
  const isMock = quiz.label === 'Mock Exam';
  for (let i = 0; i < total; i++) {
    if (!quiz.runAnswered[i]) { unanswered++; continue; }
    const e = quiz.flat[i];
    const q = DATA[e.sec][e.idx];
    const p = (progress[e.sec] || {})[q.n];
    answered++;
    if (p === 1) correct++;
    else wrong.push({ sec: e.sec, q: q });
  }
  const denom = isMock ? total : Math.max(1, answered);
  const pct = Math.round(correct / denom * 100);
  const cls = pct >= 80 ? 'good' : pct >= 50 ? 'mid' : 'bad';
  const pass = pct >= 80;
  let passbar = '';
  if (answered > 0 || isMock) {
    passbar = '<div class="passbar ' + (pass ? 'pass' : 'fail') + '">' +
      (pass ? '&#127942; Passed &mdash; rating ' + pct + '% (need 80%)' : 'Below the passing rating (80%). Keep reviewing!') + '</div>';
  }
  let timeLine = '';
  if (quiz.timeTotal > 0) {
    const used = Math.min(quiz.timeUsed, quiz.timeTotal);
    timeLine = '<div class="scoreline">Time used: ' + fmt(used) + ' / ' + fmt(quiz.timeTotal) + (quiz.timeUsed < quiz.timeTotal ? '' : ' &middot; time up') + '</div>';
  }
  let review = '';
  if (wrong.length) {
    review = '<div class="group">Review incorrect answers</div>';
    for (const w of wrong.slice(0, 50)) {
      const q = w.q;
      const letters = q.o.map((_, i) => String.fromCharCode(65 + i));
      review += '<div class="review"><div class="rq">' + esc(SECNAMES[w.sec]) + ' &middot; Q' + q.n + '. ' + esc(q.q) + '</div>' +
        '<div class="ra">&#10003; ' + letters[q.a] + '. ' + esc(q.o[q.a]) + '</div></div>';
    }
    if (wrong.length > 50) review += '<div class="small">...and ' + (wrong.length - 50) + ' more.</div>';
  } else if (answered > 0) {
    review = '<div class="fb good" style="margin-top:14px">&#127942; Perfect score! Great job.</div>';
  }
  const notes = unanswered ? '<div class="small" style="margin-top:8px">' + unanswered + ' unanswered' + (isMock ? ' (counted as wrong, like the real exam)' : '') + '</div>' : '';
  return '<div class="topline"><button class="btn ghost2" onclick="quit()">&#9776; Home</button>' +
         '<span class="spacer"></span>' +
         '<button class="btn ghost2" onclick="retry()">Retry</button></div>' +
         '<div class="summary-box"><div class="big ' + cls + '">' + pct + '%</div>' +
         '<div class="scoreline">' + correct + ' correct out of ' + denom + (isMock ? ' items' : ' answered') + '</div>' +
         timeLine + passbar + notes + '</div>' +
         review;
}

render();
</script>
</body>
</html>
"""

HTML = HTML.replace('__DATA__', data_json)
HTML = HTML.replace('__GROUPS__', groups_json)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)
print('written', OUT, len(HTML), 'bytes')
