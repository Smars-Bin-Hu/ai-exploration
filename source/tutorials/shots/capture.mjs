// Screenshots of the harness board (1.7.45) for the tutorials: each screen by name, into source/tutorials/img/_board/<name>.png, at deviceScaleFactor 2.
//
// How to run it (from the repository root; needs Google Chrome and playwright-core from ~/Developer/smarshu.com, as build.py does):
//
//   python3 source/tutorials/shots/demo.py build      # once: the demo workspace (harness 1.7.45, repos/orders-service, made-up tasks)
//   python3 source/tutorials/shots/demo.py start      # its board on 127.0.0.1:8845, in the background
//   node source/tutorials/shots/capture.mjs --make-chat   # once: the one task with a real chat in VS Code (New task, Ask me first: see below)
//   node source/tutorials/shots/capture.mjs           # every screen; or name some: node source/tutorials/shots/capture.mjs plan review
//   python3 source/tutorials/shots/demo.py stop
//
// It starts from a running board and changes no task: each run pairs a new browser (demo.py pair: a second `harness task board`, which makes the
// running board hand out a new link), presses Enter, and visits the screens. The one thing it moves is the clock of retry-stock-calls (demo.py touch),
// so the board shows that task at work. It opens the approval window of Confirm requirement and cancels it.
//
// --make-chat fills the New task form (as the new-task screen does, with the name add-gift-wrap and Ask me first) and presses Create and send:
// the board makes a Copilot chat in the VS Code that runs on this computer, and its agent opens the task and asks its first questions. That spends
// one request of Copilot. The live-waiting screen needs it; without it, that screen is skipped with a note.
//
// The screen names are in SCREENS below, each with what it shows: those of tutorial 1, then tour-* (tutorial 2, every screen and window of the
// board), stop-*, checks-*, outside-*, kb-* (tutorials 3 to 6). Their tasks come from demo.py extra (build runs it too). The outside-* screens are
// taken with the demo tool pack on (demo.py pack on, then off again): with it on, the VS Code that runs here was not started with the pack's
// folder, so its Enter screen says Not ready (outside-enter-not-ready). The demo stays with the pack off.
// A screen that cannot be taken is named at the end (exit 1); the others are still written.

import { createRequire } from 'module';
import { execFileSync } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const { chromium } = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../../..');
const DEMO = process.env.HARNESS_DEMO || path.join(REPO, '.claude/loops/2026-11-17-ai-exploration-map/demo');
const OUT = path.join(REPO, 'source/tutorials/img/_board');
const BOARD = 'http://127.0.0.1:8845';
const CHAT_TASK = 'add-gift-wrap';
const WIDTH = 1280;
const MAIN = { x: 20, right: 1128 };  // the column of the board and the task pages; the round buttons on the right are left out

const demo = (...args) => execFileSync('python3', [path.join(HERE, 'demo.py'), ...args], { encoding: 'utf8' }).trim();
const sleep = (ms) => new Promise((done) => setTimeout(done, ms));

// The region of a page to keep: from the top of the page (or of `from`) to the bottom of `to`, across the main column.
async function box(page, locator) {
  await locator.first().scrollIntoViewIfNeeded().catch(() => {});
  const found = await locator.first().boundingBox();
  if (!found) throw new Error('not on the page: ' + locator);
  const scroll = await page.evaluate(() => window.scrollY);
  return { x: found.x, y: found.y + scroll, width: found.width, height: found.height, bottom: found.y + scroll + found.height };
}

async function region(page, { from = null, to = null, top = 0, pad = 14, x = MAIN.x, right = MAIN.right }) {
  const start = from ? (await box(page, from)).y - pad : top;
  const end = to ? (await box(page, to)).bottom + pad : start + 860;
  await page.evaluate(() => window.scrollTo(0, 0));
  return { x, y: Math.max(0, start), width: right - x, height: end - Math.max(0, start) };
}

// --- no name and no path of this computer on a screen -------------------------------------------------------------------------------------
// The PNGs go into a public repository. Every page gets a script (before its own) that rewrites what it shows, and keeps rewriting it while the
// page draws itself again: the person's login name becomes alex, the home folder /Users/alex, the demo folder /Users/alex/harness (or repos),
// Python of this computer /usr/local/bin/python3. Text nodes and the values and placeholders of inputs; the page's data and the files stay as they are.
// Before each screenshot the visible text inside the picture is checked again (shoot): what is left is named, and the run fails.
const HOME = os.homedir();
const USER = os.userInfo().username;
const SCRUB = { home: HOME, user: USER, demo: DEMO, tilde: DEMO.startsWith(HOME + '/') ? '~' + DEMO.slice(HOME.length) : '' };
function scrubber(conf) {  // runs in the page
  const esc = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const rules = [];
  for (const base of [conf.demo, conf.tilde].filter(Boolean)) {
    const to = base.startsWith('~') ? '~' : '/Users/alex';
    rules.push([new RegExp(esc(base + '/harness'), 'g'), to + '/harness'], [new RegExp(esc(base + '/repos'), 'g'), to + '/repos'], [new RegExp(esc(base), 'g'), to + '/demo']);
  }
  rules.push([new RegExp(esc(conf.home), 'g'), '/Users/alex'],
             [/\/opt\/anaconda3\/bin\/python3?/g, '/usr/local/bin/python3'], [/\/opt\/anaconda3/g, '/usr/local'],
             [new RegExp('\\b' + esc(conf.user) + '(?=@)', 'g'), 'alex'], [new RegExp('\\b' + esc(conf.user) + '\\b', 'g'), 'alex']);
  const fix = (text) => rules.reduce((out, [from, to]) => out.replace(from, to), text);
  const changed = window.__scrubbed = window.__scrubbed || new Set();
  const textNode = (node) => { const next = fix(node.nodeValue); if (next !== node.nodeValue) { node.nodeValue = next; changed.add(node); } };
  const field = (el) => {
    if (el.value !== undefined && typeof el.value === 'string') { const next = fix(el.value); if (next !== el.value) { el.value = next; changed.add(el); } }
    const ph = el.getAttribute && el.getAttribute('placeholder');
    if (ph) { const next = fix(ph); if (next !== ph) { el.setAttribute('placeholder', next); changed.add(el); } }
  };
  const walk = (root) => {
    if (!root) return;
    if (root.nodeType === 3) return textNode(root);
    const tree = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = tree.nextNode(); node; node = tree.nextNode()) textNode(node);
    if (root.querySelectorAll) root.querySelectorAll('input, textarea').forEach(field);
  };
  window.__scrub = () => walk(document.body);
  const start = () => {
    walk(document.body);
    new MutationObserver((list) => { for (const item of list) { if (item.type === 'characterData') textNode(item.target); else item.addedNodes.forEach(walk); } })
      .observe(document.body, { childList: true, subtree: true, characterData: true });
    setInterval(() => document.querySelectorAll('input, textarea').forEach(field), 200);  // a value set by a script makes no mutation
  };
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
}
function leftIn([conf, clip]) {  // runs in the page: what is still there inside the picture, and whether anything in it was rewritten
  window.__scrub && window.__scrub();
  const area = clip || { x: window.scrollX, y: window.scrollY, width: window.innerWidth, height: window.innerHeight };
  const inside = (rect) => rect.width > 0 && rect.height > 0 && rect.right + window.scrollX > area.x && rect.left + window.scrollX < area.x + area.width && rect.bottom + window.scrollY > area.y && rect.top + window.scrollY < area.y + area.height;
  const shown = (node) => { const range = document.createRange(); range.selectNodeContents(node); return [...range.getClientRects()].some(inside); };
  const bad = new RegExp('/Users/(?!alex\\b)|/opt/|' + conf.user, 'i');
  const copyright = /(©|Copyright \(c\))\s*\d{4}\s*Smars Hu/g;  // the harness's own license line, as the product shows it: kept, and counted apart
  const left = [], notices = [];
  const tree = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = tree.nextNode(); node; node = tree.nextNode()) {
    if (!node.nodeValue.trim() || !shown(node)) continue;
    if (copyright.test(node.nodeValue)) notices.push(node.nodeValue.trim().slice(0, 60));
    copyright.lastIndex = 0;
    const text = node.nodeValue.replace(copyright, '');
    if (bad.test(text)) left.push(text.trim().slice(0, 120));
  }
  for (const el of document.querySelectorAll('input, textarea')) {
    if (!inside(el.getBoundingClientRect())) continue;
    for (const text of [el.value, el.getAttribute('placeholder')]) if (text && bad.test(text)) left.push('[input] ' + text.slice(0, 120));
  }
  const rewritten = [...(window.__scrubbed || [])].filter((node) => node.isConnected && (node.nodeType === 3 ? shown(node) : inside(node.getBoundingClientRect()))).length;
  return { left, notices, rewritten };
}
const scanned = {};  // name -> what leftIn found

async function shoot(page, name, clip) {
  const file = path.join(OUT, name + '.png');
  const found = await page.evaluate(leftIn, [SCRUB, clip || null]);
  scanned[name] = found;
  if (found.left.length) console.log('LEFT', name + ':', found.left.join(' | '));
  await page.screenshot(clip ? { path: file, clip, fullPage: true } : { path: file });
  console.log('wrote', path.relative(REPO, file), found.rewritten ? `(${found.rewritten} rewritten)` : '', found.notices.length ? `(license line x${found.notices.length})` : '');
}

async function task(page, name, tab = '') {
  await page.goto(`${BOARD}/task/${name}${tab ? '#' + tab : ''}`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await sleep(1800);
}

async function fillNewTask(page, name, words) {
  await page.goto(BOARD + '/');
  await sleep(1500);
  await page.getByRole('button', { name: 'New task' }).click();
  const dialog = page.locator('.new-wide');
  await dialog.waitFor();
  await sleep(1200);  // the options (kinds, models) come from the server
  await dialog.locator('input[type=text]').first().fill(name);
  await dialog.locator('select').first().selectOption('dev');
  await dialog.locator('textarea').fill(words);
  await dialog.locator('.new-grill input[type=checkbox]').check();
  await sleep(800);
  return dialog;
}

// name: [what it shows, how to take it]
const SCREENS = {
  'enter': ['The Enter screen: every line under Harness & Local green, From the company optional, the Enter button', null],  // taken while pairing, before Enter
  'lobby': ['The board as a Lobby: Off work, Back to work, Lobby | List, New task; the tasks as robots, those waiting for you first', async (page) => {
    await page.goto(BOARD + '/');
    await sleep(1500);
    await page.getByRole('button', { name: 'Lobby', exact: true }).click();
    await sleep(1500);
    return region(page, { top: 0, to: page.getByText('At work', { exact: false }) , pad: 200 });
  }],
  'list': ['The board as a List: one line per task, what it waits for, the Do column with the next button', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });  // wide enough for the task names
    await page.goto(BOARD + '/');
    await sleep(1500);
    await page.getByRole('button', { name: 'List', exact: true }).click();
    await sleep(1500);
    const table = await box(page, page.locator('table').first());
    const shot = await region(page, { top: 0, to: page.locator('tr', { hasText: 'raise-stock-timeout' }), x: table.x - 14, right: table.x + table.width + 14 });
    return { ...shot, after: async () => page.getByRole('button', { name: 'Lobby', exact: true }).click() };  // leave the board as a person opens it
  }],
  'new-task': ['The New task form filled in: Name, Kind development, What to do, Ask me first ticked; the first message beside it', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1060 });
    const dialog = await fillNewTask(page, 'show-delivery-date', 'Show the expected delivery date in the order confirmation of orders-service. Done when the confirmation has delivery_date, three working days after the order.');
    const shot = await box(page, dialog);
    await page.keyboard.press('Escape');
    return { x: shot.x - 1, y: shot.y - 1, width: shot.width + 2, height: shot.height + 2 };
  }],
  'live-waiting': ['A task that waits for you, Live tab: the agent asked its first questions; Answer...', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1500 });  // the Say something bar stays at the bottom of the window, below the crop
    await task(page, CHAT_TASK, 'live');
    return region(page, { top: 0, to: page.getByText('You can also type your own answer.').first(), pad: 24 });  // the card and the agent's first question
  }],
  'intake': ['The Intake tab: Add documents (drop or Choose files), and pasting a table', async (page) => {
    await task(page, 'import-price-list', 'intake');
    return region(page, { top: 0, to: page.getByText('Add documents').locator('xpath=following::*[contains(@class,"drop") or contains(text(),"Choose files")][1]'), pad: 60 });
  }],
  'intake-files': ['The Intake tab after the drop: the files the agent reads, the reports, Create INTAKE.md, Tell the agent with Copy message', async (page) => {
    await task(page, 'import-price-list', 'intake');
    return region(page, { from: page.getByText('Files of the requirement (REQ/)'), to: page.getByRole('button', { name: 'Copy message' }) });
  }],
  'requirement': ['Requirement tab of a development task: the card “the requirement waits for your confirmation” with Confirm requirement', async (page) => {
    await task(page, 'fix-total-rounding', 'req');
    return region(page, { top: 0, to: page.getByText('Shown by the task files').locator('xpath=following::ul[1]') });
  }],
  'approve-code': ['The approval window of Confirm requirement: the file it is for and the six-character code to type', async (page) => {
    await task(page, 'fix-total-rounding', 'req');
    await page.getByRole('button', { name: 'Confirm requirement' }).first().click();
    const dialog = page.locator('.shade .dialog').last();
    await dialog.waitFor();
    await sleep(800);
    const shot = await box(page, dialog);
    return { x: shot.x - 1, y: shot.y - 1, width: shot.width + 2, height: shot.height + 2, after: async () => page.keyboard.press('Escape') };
  }],
  'plan': ['Plan tab: “the plan waits for your approval”, Approve plan, the plan (files, steps, checks, risks)', async (page) => {
    await task(page, 'add-order-notes', 'plan');
    return region(page, { top: 0, to: page.getByRole('heading', { name: 'Risks' }).locator('xpath=following::*[1]') });
  }],
  'todo': ['TODO tab of a task at work: the steps, two ticked, the one in progress', async (page) => {
    demo('touch', 'retry-stock-calls');
    await task(page, 'retry-stock-calls', 'todo');
    return region(page, { top: 0, to: page.getByText('Dry run of the write-back').last(), pad: 40 });
  }],
  'run': ['A task that waits for your run (DEV): the card with what to run, and the Give the results here form', async (page) => {
    await task(page, 'cache-stock-counts');
    return region(page, { top: 0, to: page.getByRole('button', { name: /Save (and send to the agent|to the task)/ }) });
  }],
  'review': ['Review tab: two checks in a row asked; round-001 FAIL with its findings, then two PASS', async (page) => {
    await task(page, 'validate-sku-format', 'review');
    return region(page, { top: 0, to: page.getByText('What the reviewer was given').last(), pad: 26 });
  }],
  'changes-promote': ['Changes tab: “the promote (write-back repo) waits for your approval”, Approve promote, the diff side by side', async (page) => {
    await task(page, 'limit-order-items', 'changes');
    return region(page, { top: 0 });
  }],
  'commit-message': ['A closed development task, Changes tab: “Promoted: commit it with this message”, Copy commit message, Copy commands', async (page) => {
    await task(page, 'raise-stock-timeout', 'changes');
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Copy commands' }).first(), pad: 6 });
  }],
  'accept': ['A task “to accept”: What the agent delivered, Accept and close, Not yet', async (page) => {
    await task(page, 'why-orders-slow');
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Not yet' }).first(), pad: 18 });
  }],
  'go-on-new-chat': ['A task page whose chat is gone: the card “Waiting for you” with Go on in a new chat', async (page) => {
    await task(page, 'validate-sku-format');
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Go on in a new chat' }).first(), pad: 30 });
  }],
};

// --- the tour (tutorial 2) and the screens of tutorials 3 to 5 (demo.py extra makes their tasks) ---------------------------------------------
// An entry is [what it shows, how to take it, options]. `pack: true`: taken with the demo tool pack on (demo.py pack on), after the others; the
// Enter screen then says Not ready (the VS Code that runs here was not started with the pack's folder), so it is passed by, as a task page opened
// from a link would be. None of these presses a button that sends to a chat or spends a request: they open windows and menus and close them.

const pad = (found, by = 1) => ({ x: found.x - by, y: found.y - by, width: found.width + 2 * by, height: found.height + 2 * by });
async function dialogBox(page) {  // the window over the page (SERVE.dialog)
  const dialog = page.locator('.shade .dialog').last();
  await dialog.waitFor();
  await sleep(900);
  return pad(await box(page, dialog));
}
async function smallest(page, texts) {  // the smallest element on view that holds all these words: a panel whose class is not known
  const found = await page.evaluate((words) => {
    let best = null;
    for (const node of document.querySelectorAll('body *')) {
      const rect = node.getBoundingClientRect();
      if (!rect.width || !rect.height || !node.innerText) continue;
      if (!words.every((word) => node.innerText.includes(word))) continue;
      if (!best || rect.width * rect.height < best.width * best.height) best = { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    }
    return best;
  }, texts);
  if (!found) throw new Error('no panel with ' + texts.join(', '));
  return pad(found, 6);
}
const escape = (page) => async () => { await page.keyboard.press('Escape'); await sleep(400); };
async function board(page, view = 'Lobby') {
  await page.goto(BOARD + '/');
  await sleep(1600);
  await page.getByRole('button', { name: view, exact: true }).click();
  await sleep(1400);
}
async function listTo(page, last) {  // the List view down to the row of `last`, across the table
  const table = await box(page, page.locator('table').first());
  return region(page, { top: 0, to: page.locator('tr', { hasText: last }).first(), x: table.x - 14, right: table.x + table.width + 14 });
}
const head = (page) => region(page, { top: 0, to: page.locator('.tk-link-add').first(), pad: 14 });  // the head of a task page: name, state, stages, the chips
async function kbWindow(page, tab) {
  await board(page);
  await page.locator('.dock-book').click();
  await sleep(2200);
  if (tab !== 'overview') {
    await page.locator(`.shade .chip[data-key="${tab}"]`).click();
    await sleep(2200);
  }
  return { ...(await dialogBox(page)), after: escape(page) };
}
async function menuItem(page, task, item) {  // an item of the task's … menu
  await page.goto(`${BOARD}/task/${task}`);
  await sleep(1800);
  await page.locator('.tk-morebtn').click();
  await sleep(600);
  await page.getByText(item, { exact: true }).first().click();
}

Object.assign(SCREENS, {
  // the Enter screen and the board
  'tour-enter': ['Enter, everything ready: the lines fold to one per block (Harness & Local 5 of 5, From the company)', null],
  'tour-enter-open': ['Enter with the blocks opened (pointer on them): each line of Harness & Local and From the company', null],
  'tour-lobby': ['The board as a Lobby: Off work, Back to work, Lobby | List, New task; robots by state (waiting, at work, resting, closed)', async (page) => {
    await board(page);
    return region(page, { top: 0, to: page.getByText(/^Closed, resting on the dock/).first(), pad: 160 });
  }],
  'tour-list': ['The board as a List: the numbers on top, the filters (All, Waiting for you, Working, Quiet, No session, Paused, Closed), kinds, search, one row per task', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });
    await board(page, 'List');
    return { ...(await listTo(page, 'raise-stock-timeout')), after: async () => page.getByRole('button', { name: 'Lobby', exact: true }).click() };
  }],
  'tour-list-closed': ['The List filtered to Closed: the closed tasks, each with Archive; a tick for several', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });
    await board(page, 'List');
    await page.getByRole('button', { name: /^Closed \d/ }).click();
    await sleep(1000);
    return { ...(await listTo(page, 'raise-stock-timeout')), after: async () => { await page.getByRole('button', { name: /^All \d/ }).click(); await page.getByRole('button', { name: 'Lobby', exact: true }).click(); } };
  }],
  'tour-list-search': ['The List with “stock” in the search box: only the tasks whose name or state has it', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });
    await board(page, 'List');
    await page.locator('input.search').fill('stock');
    await sleep(1000);
    return { ...(await listTo(page, 'retry-stock-calls')), after: async () => { await page.locator('input.search').fill(''); await page.getByRole('button', { name: 'Lobby', exact: true }).click(); } };
  }],
  'tour-list-kind': ['The List with the kind menu on “knowledge base”: the kb tasks only', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });
    await board(page, 'List');
    await page.locator('select.kinds').selectOption({ index: await page.locator('select.kinds option').evaluateAll((items) => items.findIndex((item) => /knowledge/i.test(item.textContent))) });
    await sleep(1000);
    return { ...(await listTo(page, 'learn-orders')), after: async () => { await page.locator('select.kinds').selectOption({ index: 0 }); await page.getByRole('button', { name: 'Lobby', exact: true }).click(); } };
  }],
  'tour-off-work': ['After Off work: the tasks that were not at work are paused (Back to work takes them back; the capture presses it after)', async (page) => {
    await board(page, 'List');
    await page.getByRole('button', { name: /^Off work/ }).click();
    await sleep(2500);
    if (await page.locator('.shade .dialog').count()) { await page.locator('.shade .dialog').getByRole('button').first().click(); await sleep(2500); }
    await page.mouse.move(600, 820);  // no tip over the page
    await sleep(800);
    return { ...(await region(page, { top: 0, to: page.locator('tr', { hasText: 'limit-order-items' }).first(), pad: 14 })), after: async () => {
      await page.getByRole('button', { name: /^Back to work/ }).click();
      await sleep(2500);
      if (await page.locator('.shade .dialog').count()) { await page.locator('.shade .dialog').getByRole('button').first().click(); await sleep(2000); }
      await page.getByRole('button', { name: 'Lobby', exact: true }).click();
    } };
  }],
  'tour-search': ['Search (top right, or Cmd+K): go to a task, a view, a filter, a tab or the settings by name', async (page) => {
    await board(page);
    await page.locator('.sh-pill').click();
    await sleep(900);
    await page.keyboard.type('coupon');
    await sleep(900);
    return { ...pad(await box(page, page.locator('.pal').first()), 6), after: escape(page) };
  }],
  'tour-settings': ['The sliders button: Settings of this browser (theme, Glass or Lite, a background folder, language) and Restart board', async (page) => {
    await board(page);
    await page.locator('.sh-gear').click();
    await sleep(900);
    return { ...(await smallest(page, ['Theme', 'Restart board'])), after: escape(page) };
  }],
  'tour-help': ['The ? button: How can I help? (a question for a chat, How the harness works, First lesson, Everything you can ask for)', async (page) => {
    await board(page);
    await page.locator('.dock-ask').click();
    await sleep(900);
    return { ...pad(await box(page, page.locator('.dock-panel')), 6), after: async () => { await page.locator('.dock-ask').click(); await sleep(400); } };
  }],
  'tour-everything': ['Everything you can ask for: every skill a click can start, grouped (each starts a chat, so look only)', async (page) => {
    await board(page);
    await page.locator('.dock-ask').click();
    await sleep(700);
    await page.getByText('Everything you can ask for').click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  'tour-terminal': ['The >_ button: the Terminal window, with harness doctor run in it (a person’s own commands, no agent)', async (page) => {
    await board(page);
    await page.locator('.term-toggle').click();
    await sleep(900);
    await page.locator('section.term input').first().fill('harness doctor');
    await page.keyboard.press('Enter');
    await sleep(15000);
    return { ...pad(await box(page, page.locator('section.term')), 6), after: async () => { await page.locator('section.term .term-x').last().click().catch(() => {}); await sleep(400); } };
  }],
  'tour-setup-window': ['The gear button: Change the setup, cards 2 You and 3 From the company (knowledge base, instructions, skills, standards, tool packs, connections)', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1500 });
    await board(page);
    await page.locator('.dock-setup').click();
    await sleep(3000);
    const dialog = await dialogBox(page);
    const you = await box(page, page.locator('.shade .dialog').getByText('Your name').first());
    const last = await box(page, page.locator('.shade .dialog').getByText('Connections', { exact: true }).first());
    const top = you.y - 75;  // card 1 shows the path of this computer's harness command; the code repositories below card 3 show this computer's folders
    return { x: dialog.x, y: top, width: dialog.width, height: last.bottom + 24 - top, after: escape(page) };
  }],
  'tour-setup-local': ['Change the setup, card 4 Local: the programs, the network (CA bundle), MCP, and Save', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1500 });
    await board(page);
    await page.locator('.dock-setup').click();
    await sleep(3000);
    const dialog = await dialogBox(page);
    const programs = await box(page, page.locator('.shade .dialog').getByText('Programs', { exact: true }).first());
    const save = await box(page, page.locator('.shade .dialog').getByRole('button', { name: 'Save', exact: true }).first());
    const top = programs.y - 92;  // the card's head, 4 Local and its Open
    return { x: dialog.x, y: top, width: dialog.width, height: save.bottom + 24 - top, after: escape(page) };
  }],
  'tour-tools-local': ['Local (from card 4 of the setup): the programs the packs need, tool folders, the CA bundle, MCP', async (page) => {
    await page.goto(BOARD + '/setup');
    await sleep(2500);
    await page.getByRole('button', { name: 'Open', exact: true }).last().click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  'tour-report': ['A closed task’s report (… › Time and usage): time, prompts, checks, gate blocks, where the time went', async (page) => {
    await page.goto(`${BOARD}/tasks/raise-stock-timeout/report.html`);
    await sleep(2500);
    return region(page, { top: 0, to: page.getByText(/^Where the time went/).first(), pad: 120, x: 120, right: 1160 });
  }],
  'tour-performance': ['The Agent Performance Review page of a task (from its report): the accounts, the prompts, the findings', async (page) => {
    await page.goto(`${BOARD}/tasks/raise-stock-timeout/performance`);
    await sleep(2500);
    return region(page, { top: 0, x: 100, right: 1180 });
  }],
  // the task page
  'tour-task-head': ['The head of a task page: back, name, state, the stage strip, the checks, VS Code, …; the time, Independent review, VS Code linked, Paired, Link a ticket', async (page) => {
    await task(page, 'validate-sku-format');
    return head(page);
  }],
  'tour-task-more': ['The … menu of a task: Time and usage, Save as HTML, Autorun on, Pause, Close', async (page) => {
    await task(page, 'validate-sku-format');
    await page.locator('.tk-morebtn').click();
    await sleep(700);
    return { ...pad(await box(page, page.locator('.tk-menu:not([hidden])').first()), 6), after: escape(page) };
  }],
  'tour-close-dialog': ['… › Close: the window that asks why, before the task is closed (cancelled here)', async (page) => {
    await menuItem(page, 'design-order-events', 'Close');
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  'tour-archive-dialog': ['Archive on a closed task: where it is moved to, outside the repository (cancelled here)', async (page) => {
    await page.setViewportSize({ width: 1720, height: 900 });
    await board(page, 'List');
    await page.locator('tr', { hasText: 'raise-stock-timeout' }).getByRole('button', { name: 'Archive' }).click();
    return { ...(await dialogBox(page)), after: async () => { await page.keyboard.press('Escape'); await page.getByRole('button', { name: 'Lobby', exact: true }).click(); } };
  }],
  'tour-reply': ['Say something (R): the reply box of a task with a chat: text, files, language, the chat’s settings, drafts (nothing is sent here)', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1000 });
    await task(page, CHAT_TASK, 'live');
    await page.locator('.rp-pill').click();
    await sleep(1200);
    return { ...pad(await box(page, page.locator('.rp').first()), 6), after: escape(page) };
  }],
  'tour-tab-overview': ['Overview › Overview: TASK.md, the handover file (kind, tier, status, doing now, next step)', async (page) => {
    await task(page, 'add-order-notes', 'overview');
    return region(page, { top: 0, to: page.getByRole('heading', { name: /Open questions/ }).first(), pad: 60 });
  }],
  'tour-tab-log': ['Records › Log: LOG.md, the decisions and why', async (page) => {
    await task(page, 'raise-stock-timeout', 'log');
    return region(page, { top: 0 });
  }],
  'tour-tab-history': ['Records › Task Record: every event of the task, with its time (opened, confirmed, approved, written back, closed)', async (page) => {
    await task(page, 'raise-stock-timeout', 'history');
    return region(page, { top: 0 });
  }],
  'tour-tab-trace': ['Records › Agent actions: per prompt, the tool calls and the gate’s decisions; the numbers on top', async (page) => {
    await task(page, 'limit-order-items', 'trace');
    return region(page, { top: 0 });
  }],
  'tour-tab-files': ['Files: every file of the task folder, to open or download', async (page) => {
    await task(page, 'import-price-list', 'files');
    return region(page, { top: 0 });
  }],
  'tour-tab-test': ['Results › Test of a test task: the guide per environment (DEV passed, IST to run), the results by environment', async (page) => {
    await task(page, 'test-sku-check', 'test');
    return region(page, { top: 0, pad: 0 });
  }],
  'tour-tab-evidence': ['Results › Evidence: what the person gave back for each run', async (page) => {
    await task(page, 'test-sku-check', 'evidence');
    return region(page, { top: 0 });
  }],
  'tour-tab-design': ['Results › Design of a design task: DESIGN.md', async (page) => {
    await task(page, 'design-order-events', 'design');
    return region(page, { top: 0 });
  }],
  'tour-tab-rca': ['Results › RCA of an RCA task: RCA.md', async (page) => {
    await task(page, 'why-orders-slow', 'rca');
    return region(page, { top: 0 });
  }],
  // tutorial 3: when the agent is stopped
  'stop-agent-actions': ['Records › Agent actions of a task whose agent was refused: blocked by a hook 5, the edit of the repository, git push, git checkout with its code, a ticket delete', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1300 });
    await task(page, 'add-order-export', 'trace');
    return region(page, { top: 0, to: page.getByText(/^Blocked and failed/).locator('xpath=..'), pad: 10 });
  }],
  'stop-git-code': ['A git command the gate refused with a code: the person runs harness approve-command in a terminal and types it', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1300 });
    await task(page, 'add-order-export', 'trace');
    const row = page.getByText('checkout -b try-export').first();
    await page.getByText(/^The git command in this command changes the repository/).first().click();  // opens the whole reason
    await sleep(800);
    return region(page, { from: row, to: page.getByText(/do not run approve-command yourself/).first(), pad: 22 });
  }],
  // tutorial 4: independent checks
  'checks-chip': ['The Independent review chip opened: how many checks in a row (off, 1 to 5), only the person sets it', async (page) => {
    await task(page, 'validate-sku-format');
    await page.evaluate(() => [...document.querySelectorAll('.rv-btn')].find((item) => item.textContent.includes('Independent review')).click());  // in one go: the head is drawn again every few seconds
    await sleep(500);
    const chip = await box(page, page.locator('.rv-btn', { hasText: 'Independent review' }).first());
    const pop = await box(page, page.locator('.rv-pop:not([hidden])').first());
    const x = Math.min(chip.x, pop.x) - 8, y = chip.y - 8;
    return { x, y, width: Math.max(chip.x + chip.width, pop.x + pop.width) + 8 - x, height: pop.bottom + 8 - y, after: escape(page) };
  }],
  'checks-used-up': ['The checks are used up: More checks, Waive checks, Dismiss check', async (page) => {
    await task(page, 'check-coupon-codes');
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Dismiss check' }), pad: 30 });
  }],
  'checks-used-review': ['Review tab of that task: 1 asked, three FAIL, 3 of 3 used', async (page) => {
    await page.setViewportSize({ width: WIDTH, height: 1300 });
    await task(page, 'check-coupon-codes', 'review');
    return region(page, { top: 0, to: page.getByText('What the reviewer was given').last(), pad: 26 });
  }],
  'checks-more': ['More checks: the window with the code (cancelled here)', async (page) => {
    await task(page, 'check-coupon-codes');
    await page.getByRole('button', { name: 'More checks' }).first().click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  'checks-waive': ['Waive checks: the window with the code (cancelled here)', async (page) => {
    await task(page, 'check-coupon-codes');
    await page.getByRole('button', { name: 'Waive checks' }).first().click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  'checks-dismiss': ['Dismiss check: the window that asks why the reviewer was wrong (cancelled here)', async (page) => {
    await task(page, 'check-coupon-codes');
    await page.getByRole('button', { name: 'Dismiss check' }).first().click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }],
  // tutorial 6: the knowledge base
  'kb-overview': ['The book button: Knowledge base › Overview: the eight steps, Next, the numbers, each domain with its cards, stale, requests, last read', async (page) => kbWindow(page, 'overview')],
  'kb-map': ['Knowledge base › Map: how the domains hang together', async (page) => kbWindow(page, 'atlas')],
  'kb-company': ['Knowledge base › Company: what this company’s agent can do (instructions, skills, packs, connections)', async (page) => kbWindow(page, 'company')],
  'kb-domains': ['Knowledge base › Domains: each domain, learned or not, cards, stale, requests, last read by a task', async (page) => kbWindow(page, 'domains')],
  'kb-lookup': ['Knowledge base › Look up: one object (usp_load_orders), what it uses and what uses it, from the map', async (page) => {
    const shot = await kbWindow(page, 'lookup');
    await page.locator('.shade input.code').fill('sp:Shop.dbo.usp_load_orders');
    await page.locator('.shade input.code').press('Enter');
    await sleep(2000);
    return { ...(await dialogBox(page)), after: shot.after };
  }],
  'kb-health': ['Knowledge base › Health: the audit, the form of the cards, Stale cards (the source changed), gaps of the map', async (page) => kbWindow(page, 'health')],
  'kb-changes-promote': ['A knowledge base task, Changes: the card change, and Approve promote (it commits on the knowledge base’s main branch)', async (page) => {
    await task(page, 'fix-orders-card', 'changes');
    return region(page, { top: 0, to: page.getByText(/^This is also what goes into/).first(), pad: 20 });
  }],
  // tutorial 5: outside systems (the demo pack on)
  'outside-enter-not-ready': ['Enter with the pack on and VS Code started without its folder: VS Code “no settings”, Restart VS Code, Not ready', null, { pack: true }],
  'outside-held-card': ['A held outside call on the task page: Add a comment to ticket T-7, the text, View, the code box, Approve, Do not approve', async (page) => {
    await task(page, 'answer-ticket-t7');
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Do not approve' }).first(), pad: 30 });
  }, { pack: true }],
  'outside-held-view': ['View on the held call: what exactly runs, before it can be approved', async (page) => {
    await task(page, 'answer-ticket-t7');
    await page.getByRole('button', { name: 'View', exact: true }).first().click();
    await sleep(1000);
    if (await page.locator('.shade .dialog').count()) return { ...(await dialogBox(page)), after: escape(page) };
    return region(page, { top: 0, to: page.getByRole('button', { name: 'Do not approve' }).first(), pad: 30 });
  }, { pack: true }],
  'outside-open-to-agent': ['The Open to the agent chip opened, after Open on its linked items row: linked items open for this task, with Close (closed again here)', async (page) => {
    await task(page, 'answer-ticket-t7');
    const pop = () => page.evaluate(() => {  // in one go: the page draws its head again every few seconds
      const chip = [...document.querySelectorAll('.rv-btn')].find((item) => item.textContent.includes('Open to the agent'));
      if (chip.nextElementSibling.hidden) chip.click();
      return chip.nextElementSibling;
    });
    await page.evaluate(() => {
      const chip = [...document.querySelectorAll('.rv-btn')].find((item) => item.textContent.includes('Open to the agent'));
      chip.click();
      chip.nextElementSibling.querySelector('.open-row[data-conn="links"] button').click();  // Open linked items for this task: nothing is sent, no chat
    });
    await sleep(2500);
    await pop();
    await sleep(300);
    return { ...pad(await box(page, page.locator('.rv-pop:not([hidden])').first()), 6), after: async () => {
      await page.evaluate(() => {  // Close: back as it was
        const chip = [...document.querySelectorAll('.rv-btn')].find((item) => item.textContent.includes('Open to the agent'));
        if (chip.nextElementSibling.hidden) chip.click();
        chip.nextElementSibling.querySelector('.open-row[data-conn="links"] button').click();
      });
      await sleep(1500);
      await page.keyboard.press('Escape');
    } };
  }, { pack: true }],
  'outside-link': ['Link a ticket with the pack on: the link types (demo) and the box for the id', async (page) => {
    await task(page, 'answer-ticket-t7');
    await page.locator('.tk-link-add').click();
    await sleep(900);
    if (await page.locator('.shade .dialog').count()) return { ...(await dialogBox(page)), after: escape(page) };
    return { ...(await region(page, { top: 0, pad: 0 })), height: 300, after: escape(page) };
  }, { pack: true }],
  'outside-task-head': ['The head of a task linked to ticket T-7: the link chip, Open to the agent none', async (page) => {
    await task(page, 'answer-ticket-t7');
    return head(page);
  }, { pack: true }],
  'outside-tools-packs': ['Tool packs (setup, card 3 › Open): the packs the company uses (demotracker) and what each needs', async (page) => {
    await page.goto(BOARD + '/setup');
    await sleep(2500);
    await page.getByRole('button', { name: 'Open', exact: true }).first().click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }, { pack: true }],
  'outside-tools-connections': ['Connections & sign-ins: the company’s connection demo (Demo tracker), its sign-in and Test', async (page) => {
    await page.goto(BOARD + '/setup');
    await sleep(2500);
    await page.getByRole('button', { name: 'Open', exact: true }).nth(1).click();
    return { ...(await dialogBox(page)), after: escape(page) };
  }, { pack: true }],
});

async function main() {
  const asked = process.argv.slice(2).filter((item) => !item.startsWith('--'));
  const makeChat = process.argv.includes('--make-chat');
  const unknown = asked.filter((name) => !(name in SCREENS));
  if (unknown.length) throw new Error('no such screen: ' + unknown.join(', ') + '\nscreens: ' + Object.keys(SCREENS).join(', '));
  const wanted = asked.length ? asked : Object.keys(SCREENS);
  fs.mkdirSync(OUT, { recursive: true });
  const failed = [];

  demo('pack', 'off');  // the state the demo is kept in: every line of the Enter screen green
  demo('pair');
  const link = fs.readFileSync(path.join(DEMO, 'pair-url.txt'), 'utf8').trim();
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 860 }, deviceScaleFactor: 2, reducedMotion: 'reduce', colorScheme: 'light', locale: 'en-US' });
  await context.addInitScript(scrubber, SCRUB);
  const page = await context.newPage();
  try {
    await page.goto(link);
    const enter = page.getByRole('button', { name: /^Enter/ });
    for (let i = 0; i < 90 && !(await enter.isEnabled().catch(() => false)); i++) await sleep(1000);  // doctor runs at the start: Enter is on when every required line is green
    await sleep(2500);  // the lines light up one after another
    if (wanted.includes('enter') && !makeChat) await shoot(page, 'enter', null);
    if (wanted.includes('tour-enter') && !makeChat) await shoot(page, 'tour-enter', null);
    if (wanted.includes('tour-enter-open') && !makeChat) {
      await page.getByText(/Harness & Local/).first().hover();
      await sleep(1500);
      await shoot(page, 'tour-enter-open', null);
    }
    await page.keyboard.press('Enter');
    await sleep(2500);
    demo('touch', 'retry-stock-calls');

    if (makeChat) {
      await page.setViewportSize({ width: WIDTH, height: 1060 });
      const dialog = await fillNewTask(page, CHAT_TASK, 'Let a customer ask for gift wrap on an order in orders-service. Done when an order can carry gift_wrap: true and the confirmation says so.');
      await dialog.getByRole('button', { name: 'Create and send' }).click();
      await sleep(5000);
      console.log('asked the board for a chat for', CHAT_TASK, '- its agent opens the task and asks; then run capture.mjs again');
      return;
    }

    const take = async (name) => {  // one screen; a screen that fails is said and left, the others go on
      try {
        await page.setViewportSize({ width: WIDTH, height: 860 });
        const clip = await SCREENS[name][1](page);
        const after = clip && clip.after;
        if (clip) delete clip.after;
        await shoot(page, name, clip);
        if (after) await after();
      } catch (error) {
        failed.push(name);
        console.log('FAILED', name + ':', String(error.message || error).split('\n')[0]);
        await page.keyboard.press('Escape').catch(() => {});
      }
    };
    const packed = wanted.filter((name) => (SCREENS[name][2] || {}).pack);
    for (const name of wanted) {
      if (['enter', 'tour-enter', 'tour-enter-open'].includes(name) || packed.includes(name)) continue;
      if (name === 'live-waiting' && !fs.existsSync(path.join(DEMO, 'harness/.workspace/sandbox/tasks', CHAT_TASK))) {
        console.log('skipped live-waiting: no task', CHAT_TASK, '(run capture.mjs --make-chat once)');
        continue;
      }
      await take(name);
    }
    if (packed.length) {  // the demo pack on: its screens, then off again
      demo('pack', 'on');
      demo('hold');  // a held call lives 10 minutes: made again for these screens
      try {
        await sleep(4000);
        if (packed.includes('outside-enter-not-ready')) {
          const fresh = await context.newPage();  // a new tab: the Enter screen again, for this browser that is paired already
          await fresh.goto(BOARD + '/');
          await sleep(9000);
          await shoot(fresh, 'outside-enter-not-ready', null);
          await fresh.close();
        }
        for (const name of packed) if (name !== 'outside-enter-not-ready') await take(name);
      } finally {
        demo('pack', 'off');
      }
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(path.join(DEMO, 'scan.json'), JSON.stringify(scanned, null, 1));  // per screen: what was rewritten, what is left (not in git)
  const left = Object.keys(scanned).filter((name) => scanned[name].left.length);
  if (left.length) failed.push(...left.map((name) => name + ' (a name or a path is left)'));
  if (failed.length) throw new Error('not taken: ' + failed.join(', '));
}

main().catch((error) => { console.error(error.message || error); process.exit(1); });
