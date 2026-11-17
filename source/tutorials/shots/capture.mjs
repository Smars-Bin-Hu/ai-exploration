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
// The screen names are in SCREENS below, each with what it shows.

import { createRequire } from 'module';
import { execFileSync } from 'child_process';
import fs from 'fs';
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

async function shoot(page, name, clip) {
  const file = path.join(OUT, name + '.png');
  await page.screenshot(clip ? { path: file, clip, fullPage: true } : { path: file });
  console.log('wrote', path.relative(REPO, file));
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

async function main() {
  const asked = process.argv.slice(2).filter((item) => !item.startsWith('--'));
  const makeChat = process.argv.includes('--make-chat');
  const unknown = asked.filter((name) => !(name in SCREENS));
  if (unknown.length) throw new Error('no such screen: ' + unknown.join(', ') + '\nscreens: ' + Object.keys(SCREENS).join(', '));
  const wanted = asked.length ? asked : Object.keys(SCREENS);
  fs.mkdirSync(OUT, { recursive: true });

  demo('pair');
  const link = fs.readFileSync(path.join(DEMO, 'pair-url.txt'), 'utf8').trim();
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const context = await browser.newContext({ viewport: { width: WIDTH, height: 860 }, deviceScaleFactor: 2, reducedMotion: 'reduce', colorScheme: 'light', locale: 'en-US' });
  const page = await context.newPage();
  try {
    await page.goto(link);
    const enter = page.getByRole('button', { name: /^Enter/ });
    for (let i = 0; i < 90 && !(await enter.isEnabled().catch(() => false)); i++) await sleep(1000);  // doctor runs at the start: Enter is on when every required line is green
    await sleep(2500);  // the lines light up one after another
    if (wanted.includes('enter') && !makeChat) await shoot(page, 'enter', null);
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

    for (const name of wanted) {
      if (name === 'enter') continue;
      if (name === 'live-waiting' && !fs.existsSync(path.join(DEMO, 'harness/.workspace/sandbox/tasks', CHAT_TASK))) {
        console.log('skipped live-waiting: no task', CHAT_TASK, '(run capture.mjs --make-chat once)');
        continue;
      }
      await page.setViewportSize({ width: WIDTH, height: 860 });
      const clip = await SCREENS[name][1](page);
      const after = clip && clip.after;
      if (clip) delete clip.after;
      await shoot(page, name, clip);
      if (after) await after();
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error.message || error); process.exit(1); });
