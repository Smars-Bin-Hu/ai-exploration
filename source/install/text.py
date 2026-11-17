# The words of "Install the harness": one step per page, for a colleague on a company Windows computer who has never used it.
# Facts follow the harness at tag 1.7.45 (docs/01-quickstart.md, docs/03-configure.md, docs/13, docs/08, the skill
# harness-rookie-quick-start, and the words the board shows). build.py lays it out.
#
# Markup inside a string: **bold** for what you see on screen (buttons, labels), `code` for what you type.
# A block is one of:
#   'a paragraph'                 plain text
#   ('code', 'line\nline')        a box with what to type, one command per line
#   ('co', ['[Company: ...]'])    a grey box the author rewrites for the company; every one starts with "[Company:"
#   ('small', 'text')             a small grey line
# A page: kicker, title, left (blocks), and one of: pic (an image in img/ and a crop box), shot (a screenshot still to take),
# or right (a second column of blocks). wide=True puts the picture across the page under the text.

VERSION = '1.7.45'
REPO = 'https://github.com/Smars-Bin-Hu/copilot-agentic-harness'
FOOTER = 'AI Exploration · Install the harness'

COVER = dict(kicker='AI Exploration', title='Install the harness',
    sub='On a company Windows computer, from nothing to your first task. At the end the board runs in your browser, '
        'Copilot in VS Code works by the harness’s rules, and you can hand it a task.',
    how=['Harness version ' + VERSION + '. One step per page: do them in order.',
         '**Bold** is what you see on the screen. A grey box with Courier text is what you type, exactly as written.',
         'Grey italic text starting with “[Company:” is for our company and will be filled in.'])

PAGES = [
 dict(kicker='Before you start', title='Have these programs on your computer',
  left=[
   '**1. Python 3.9 or later**, from python.org. In its installer, tick **Add python.exe to PATH**. The harness runs `python`, not `py`.',
   '**2. git.** Needed to get the harness and to work on code repositories.',
   '**3. VS Code**, installed with the option **Add to PATH** on (the default), so the `code` command works. The board starts VS Code with it.',
   '**4. GitHub Copilot Chat** in VS Code, signed in. In the chat box, set the Session Target to **Copilot**: the harness supports only this kind of session.',
   '**5. A short folder that does not sync**, for example `C:\\dev`. Not under OneDrive.',
   'Open **Windows PowerShell** (press the Windows key, type PowerShell) and check each one. Each line must print a version:',
   ('code', 'python --version\ngit --version\ncode --version'),
  ],
  right=[
   'If `python` opens the Microsoft Store, or only `py` works: turn off **python.exe** and **python3.exe** in **Settings > Apps > Advanced app settings > App execution aliases**, then open a new PowerShell.',
   'git needs your name and email once (the knowledge base step makes a commit):',
   ('code', 'git config --global user.name "Your Name"\ngit config --global user.email "you@company.com"'),
   ('co', ['[Company: where to get each program here (Software Center, or the folder AI Exploration > 4 Install the harness > programs), and the versions we use.]',
           '[Company: the access to request before you start: the GitHub Copilot licence, and anything else, with the link and how long it takes.]',
           '[Company: whether git, Python and pip work as they are behind our proxy (Zscaler), or need the certificate steps on the next page.]']),
  ],
  notes='Source: docs/01-quickstart.md, Requirements; docs/03-configure.md, Getting ready (the Python Store stub, git name and email).'),

 dict(kicker='Step 1 · Get the harness', title='Clone it with git',
  top=[
   '**1.** Open **Windows PowerShell**.',
   '**2.** Type this as one line and press Enter. It puts version ' + VERSION + ' in `C:\\dev\\harness`:',
   ('code', 'git clone --branch ' + VERSION + ' ' + REPO + ' C:\\dev\\harness'),
  ],
  left=[
   '**3.** git says **You are in \'detached HEAD\' state**. That is normal: you have exactly version ' + VERSION + '.',
   '**4.** Open `C:\\dev\\harness` in File Explorer. You see **Start Harness.cmd**, **docs** and **README.md**.',
   'Keep the path short: Windows stops at 260 characters, and a task adds more than a hundred. `harness doctor` warns when the path is too long.',
  ],
  right=[
   ('co', ['[Company: proxy and certificate (Zscaler). Confirm which of these we need, then run the clone again.]',
           '[Company: if git says “SSL certificate problem: unable to get local issuer certificate”, let git use the Windows certificate store, which already trusts the company root:]',
           ('mcode', 'git config --global http.sslBackend schannel'),
           '[Company: or point git at the company root certificate:]',
           ('mcode', 'git config --global http.sslCAInfo C:\\certs\\root.pem'),
           '[Company: if git cannot reach github.com at all, set the proxy:]',
           ('mcode', 'git config --global http.proxy http://proxy:8080')]),
  ],
  notes='Source: docs/01-quickstart.md (git clone or zip; a short path such as C:\\dev\\harness). The git proxy and certificate settings are not in the harness docs: the author confirms them.'),

 dict(kicker='Step 1 · Or, without git', title='Download the zip instead',
  top=[
   'Use this only when git does not work for you. A copy from a zip has no .git folder, which does no harm.',
   '**1.** Open this address in your browser. The file **copilot-agentic-harness-' + VERSION + '.zip** downloads:',
   ('code', REPO + '/archive/refs/tags/' + VERSION + '.zip'),
  ],
  left=[
   '**2.** Right-click the zip, choose **Extract All...**, type `C:\\dev` and press **Extract**.',
   '**3.** You get the folder `C:\\dev\\copilot-agentic-harness-' + VERSION + '`. Rename it to `harness`.',
   '**4.** Check: **Start Harness.cmd** must be directly in `C:\\dev\\harness`, not one folder deeper.',
   ('co', ['[Company: if Windows blocks files from the internet here: right-click the zip > Properties > tick Unblock > OK, before Extract All. Confirm.]',
           '[Company: if the download is blocked, where to get the zip instead.]']),
  ],
  shot='File Explorer with C:\\dev\\harness open: Start Harness.cmd, docs, README.md',
  notes='Source: docs/01-quickstart.md, Common cases: "The zip from GitHub has one more folder".'),

 dict(kicker='Step 2 · Start the harness', title='Double-click Start Harness.cmd',
  left=[
   '**1.** In `C:\\dev\\harness`, double-click **Start Harness.cmd**.',
   '**2.** A black window opens and says it is starting the board. **Keep this window open while you work.** Closing it stops the board.',
   '**3.** Your browser opens on the board. It is a page on your own computer, already paired with the program.',
   '**4.** From now on, start it with the **Start Harness** shortcut that appeared beside it, with the robot icon. (A .cmd file cannot hold an icon, so the first start makes the shortcut.)',
   '**5.** A new copy says **A new copy. Press Get ready**. Press **Get ready**.',
   'If the double-click is blocked, run it in PowerShell:',
   ('code', 'cd C:\\dev\\harness\n.harness\\bin\\harness.cmd task board'),
  ],
  pic=('enter', None), caption='The board, here already set up. The robot is the icon of the Start Harness shortcut.',
  notes='Source: docs/01-quickstart.md step 1; docs/03-configure.md, Getting ready; Start Harness.cmd at 1.7.45.'),

 dict(kicker='Get ready · Card 1 of 4', title='The short command',
  left=[
   'The form has four numbered cards. Fill them from top to bottom.',
   'Every command the agent is given starts with `harness`, so every terminal must find it. Card 1 does this once.',
   '**1.** Press **Set it up**. The board runs one line for you: it makes the folder `C:\\Users\\<you>\\bin`, copies **harness.cmd** into it, and adds that folder to the Path of your account.',
   '**2.** Press **Test it**. It runs `harness --version` the way a new terminal would. You see the HARNESS banner and the version.',
   '**3.** If the card says **Now quit VS Code and open it again**, do it. The page waits.',
   '**4.** The card gets a green tick and shows where it found `harness`.',
   'If **Set it up** fails because the computer does not let you change Path, go to the next page.',
  ],
  pic=('get-ready', (126, 148, 874, 507)), caption='From a test copy on a Mac. On Windows the path reads C:\\Users\\<you>\\bin\\harness.cmd.',
  notes='Source: docs/03-configure.md, Getting ready ("The short command"); .harness/engine/core/shortcmd.py (the Windows line).'),

 dict(kicker='Get ready · Card 1, by hand', title='If Set it up is not allowed',
  left=[
   '**1.** Make a folder outside the harness: `C:\\Users\\<you>\\bin`.',
   '**2.** Copy `C:\\dev\\harness\\.harness\\bin\\harness.cmd` into it. A copy, not a shortcut or a link: a link needs administrator rights.',
   '**3.** Press the Windows key, type **environment variables**, open **Edit environment variables for your account**.',
   '**4.** Under **User variables**, select **Path**, press **Edit**, then **New**, type `C:\\Users\\<you>\\bin`, and press **OK** twice.',
   '**5.** If the computer does not let you change Path, ask the helpdesk to add this one entry: “Please add `C:\\Users\\<you>\\bin` to the Path of my account.”',
   'You do this once. A later version needs no Path change. Do not use an alias or a PowerShell function instead: they work only in your own terminal, not in the agent’s.',
   ('co', ['[Company: how to ask the helpdesk (portal or ticket type), and how long it takes.]']),
  ],
  shot='Edit environment variables for your account, with C:\\Users\\<you>\\bin in Path',
  notes='Source: docs/01-quickstart.md step 1, Windows.'),

 dict(kicker='Get ready · After card 1', title='Reopen the terminal and VS Code',
  left=[
   'A terminal or a VS Code that was open before the change still has the old Path. Copilot’s terminal uses the Path VS Code had when it started.',
   '**1.** Close every PowerShell window.',
   '**2.** If VS Code is open, quit it (**File > Exit**) and open it again.',
   '**3.** Check in a new PowerShell window:',
   ('code', 'cd C:\\dev\\harness\nharness --version'),
   'It prints the HARNESS banner and **version ' + VERSION + '**.',
   'Still **not recognized**? Type `echo $env:Path`: it must show `C:\\Users\\<you>\\bin`. If it does not, the Path change did not take. Then run the harness by its full path; it says what is wrong:',
   ('code', '.harness\\bin\\harness.cmd doctor'),
  ],
  shot='A new PowerShell window after harness --version, showing the banner and the version',
  notes='Source: docs/01-quickstart.md step 1 and step 2; docs/03-configure.md, Getting ready (issue table).'),

 dict(kicker='Get ready · Card 2 of 4', title='You',
  left=[
   '**1. Your name.** Type it. The agent knows you by it.',
   '**2. Preferred language.** Press **English** or **中文 [ZH]**. The form changes to that language at once and keeps what you typed.',
   'The language covers what the commands print, the task files and the language the agent answers and writes in.',
   'You can change both later: the sliders button at the bottom right of the board opens the same form, **Change the setup**.',
  ],
  pic=('get-ready', (126, 505, 874, 686)),
  notes='Source: docs/01-quickstart.md step 1 (card 2); docs/03-configure.md, Language and Getting ready.'),

 dict(kicker='Get ready · Card 3 of 4', title='From the company: the knowledge base',
  left=[
   'Card 3 is optional: none of it stops you. Without a knowledge base every row is yellow **not found**, and the agent does local work only.',
   '**1.** Choose how the knowledge base comes: **Package (zip)** for a file a colleague packed, **Folder** for a folder (with git), or **Keep it** when one is already in place.',
   '**2.** Type the path of the zip or the folder, or press **Browse**. For a package the form says what it holds: **Package <version>: N new, N changed, N removed files.**',
   '**3.** The form checks the layout. What is right is green; what is marked will not reach the agent.',
   ('co', ['[Company: which way we use and where it is. For example: the package <word>-kb-<date>-<time>.zip in the OneDrive folder AI Exploration > 4 Install the harness. Copy it to your computer first.]',
           '[Company: who to ask when it is missing or old.]']),
  ],
  pic=('get-ready', (126, 684, 874, 822)), caption='Here Keep it: a knowledge base with 3 domains is already in place.',
  notes='Source: docs/01-quickstart.md step 1 (card 3); docs/03-configure.md, Knowledge base and Company content.'),

 dict(kicker='Get ready · Card 3 of 4', title='From the company: what comes with it',
  left=[
   'These rows come with the knowledge base. You do not set them one by one: each says found or not found. The **?** beside a row explains it.',
   '**Instructions:** what the company tells the agent.',
   '**Company skills:** the company’s own procedures, and which are not named by the rules.',
   '**Skill prefix:** the word company skills start with.',
   '**Code standards:** the company’s rules for code.',
   '**Code repositories:** this one you set. Add the folder that holds your git repositories and tick the ones to add, or add one repository. You can leave it empty and set it later.',
   ('co', ['[Company: what our instructions, skills and code standards are, and our skill prefix.]',
           '[Company: which repositories to clone first, and where (for example C:\\dev\\repos, a short path too).]']),
  ],
  pic=('get-ready', (126, 822, 874, 990)),
  notes='Source: docs/01-quickstart.md step 1 (card 3); docs/03-configure.md, Getting ready (Code repositories), Company content, Skills, Code standards.'),

 dict(kicker='Get ready · Card 3 of 4', title='Tool packs, connections and sign-ins',
  left=[
   'A **tool pack** is how the agent reaches one tool, such as Azure DevOps or SQL Server. A **connection** is one place it reaches with your sign-in.',
   '**1.** On **Tool packs**, press **Open**. Each pack shows whether the company uses it and the programs it needs. Leave **Turn on** and **Turn off** to the owner of the knowledge base: they change it.',
   '**2.** On **Connections & sign-ins**, press **Open**. For each connection press **Sign in**: type your account and password (or token). It is kept only when its test passes. For a program that keeps its own sign-in (such as az), **Sign in** runs its login.',
   '**3.** A failed **Test** shows **Program → Sign-in → Account access → Address**, marks the first that broke, and says what to do.',
   'The agent has your rights, no more. Reads run; writes wait for your approval.',
   ('co', ['[Company: which tool packs we use, which connections to sign in to, with which account, and the access to request first.]']),
  ],
  pic=('tools', (170, 77, 990, 737)),
  notes='Source: docs/03-configure.md, Tools: tool packs, connections, local; docs/13-tool-packs-and-mcp.md.'),

 dict(kicker='Get ready · Card 4 of 4', title='Local: programs, network, MCP',
  left=[
   'Card 4 is what belongs to this computer. **Open** shows the **Local** window.',
   '**Programs:** the programs the tool packs need, for example `az` or `sqlcmd`. Not found: type the folder that holds it and press **Use**.',
   '**Network:** behind a company proxy that inspects TLS, tools with their own list of roots (az, pip) fail with **CERTIFICATE_VERIFY_FAILED**. Press **Make**: it builds a certificate bundle from what this computer trusts, and keeps it only when a check passes. Certificate checks stay on.',
   '**MCP:** **Blocked** unless you allow it. Every tool pack still works without it.',
   ('co', ['[Company: the programs to install, and from where.]',
           '[Company: whether we need Make, and the address and proxy to type (they may be filled in already, marked “from the company”).]',
           '[Company: whether MCP is allowed here.]']),
  ],
  pic=('tools', (216, 742, 944, 800)), caption='The last two rows of card 4 on a computer with no proxy.',
  shot='Card 4 on our computer, with the Local window open',
  notes='Source: docs/03-configure.md, Local: programs, network, MCP; MCP is optional.'),

 dict(kicker='Get ready · Card 4 of 4', title='More: the Python install command',
  left=[
   'Word and .xlsx files are read with nothing installed. Old Excel (.xls) and PDF files need two small Python packages, xlrd and pypdf.',
   '**1.** Under card 4, open **More: Python install command, paths the agent must not touch**.',
   '**2.** In **Python install command**, type the command your company allows, with `{package}` where the name goes. Empty means `pip install`.',
   'The harness never runs an install by itself and never guesses the command. The command must install into the Python the harness runs on.',
   ('co', ['[Company: our approved command, for example:]',
           ('mcode', 'py -m pip install {package} --proxy http://proxy.example.com:8080 --trusted-host pypi.org --trusted-host files.pythonhosted.org'),
           '[Company: or our own package index, if we have one.]']),
  ],
  shot='The More fold of card 4 with the Python install command filled in',
  notes='Source: docs/03-configure.md, Python packages; the board text "Behind a company proxy, for example: ...".'),

 dict(kicker='Get ready · Finish', title='Press Finish setup',
  left=[
   '**1.** Press **Finish setup** below card 4. It stays off until card 1 is done. It saves your choices in your own settings, never in the harness’s files.',
   '**2.** It runs a few steps: Python, the knowledge base, its repository, the company content, and `harness doctor`. It says **Still setting up. Do not close this window.** Many repositories take a while.',
   '**3.** **Setup finished.** The board goes to the Enter screen.',
   'If it says **Setup stopped at:** a step, mend the reason it shows, then press **Retry setup**.',
   'The most common stop: the knowledge base step fails on the first commit, because git has no name or email. Set them (page 2), then press it again.',
  ],
  shot='Setup finished, with the steps it ran',
  notes='Source: docs/03-configure.md, Getting ready (issue table); the board texts of Get ready.'),

 dict(kicker='Check', title='Run harness doctor',
  left=[
   '`harness` works on the copy of the folder you are in, the way git does. So go into the folder first. In a new PowerShell window:',
   ('code', 'cd C:\\dev\\harness\nharness doctor'),
   'Each line starts with one of three words:',
   '**[OK]** is fine.',
   '**[WARN]** is a reminder. It stops nothing.',
   '**[ERROR]** must be fixed first. The message says which file and which item.',
   'A last line of `{"errors": 0}` means it passed. On the Enter screen, the line **harness doctor** is then green.',
  ],
  right=[
   '**Common lines, and what to do**',
   '**The path of the harness has N characters** or **The harness is under OneDrive:** use `C:\\dev\\harness` (page 3).',
   '**The short command is not on PATH:** pages 6 to 8.',
   '**`python` does not run** (the Store placeholder): page 2.',
   '**Optional Python packages not installed:** set the install command (page 14).',
   '**The `code` command was not found:** install VS Code again with **Add to PATH** on.',
   '**`harness` on PATH is not this copy’s:** there is another copy on this computer. It works.',
  ],
  shot='harness doctor in PowerShell, ending with {"errors": 0}',
  notes='Source: docs/01-quickstart.md step 2; the doctor messages at 1.7.45 (target.windows.long, doctor.short.missing, doctor.vscode.nocli).'),

 dict(kicker='Enter', title='What must be green before you enter',
  left=[
   'At the bottom left of the Enter screen are two blocks. Hold the pointer on one, or click it, to open it.',
   '**Harness & Local** is required. All five lines must be green, or **Enter** stays off: **This copy is set up**, **Browser paired**, **harness doctor** (no errors), **VS Code** (open), **Copilot** (connected).',
   '**From the company** is optional: the knowledge base, instructions, company skills, code standards, tool packs, connections and sign-ins, code repositories. It never stops Enter. What is missing is a short yellow note with a link to where it is mended.',
   'When everything is green, each block folds to one line. Then press **Enter**.',
  ],
  pic=('enter', (0, 655, 1280, 770)), wide=True,
  shot='The Harness & Local block opened, with its five green lines',
  notes='Source: docs/01-quickstart.md step 1 (the Enter screen).'),

 dict(kicker='Enter', title='Open VS Code from the board',
  left=[
   'Start VS Code with the button beside **Enter**, not from the Start menu. The board starts it with this computer’s settings, such as the tool folders and the certificate bundle.',
   '**Open VS Code:** VS Code is not running.',
   '**Open VS Code with identities:** a connection has a saved sign-in. Tick the identities and press **Open VS Code**.',
   '**Restart VS Code:** it runs without this computer’s settings. It quits VS Code the normal way and opens it again; it never kills it. If VS Code asks whether to save a file or stop a chat, answer it in VS Code.',
   'No button means VS Code already runs with the right settings.',
   'In VS Code, sign in to GitHub Copilot if it asks. The **Copilot** line turns green when it is connected.',
  ],
  pic=('enter', (455, 690, 915, 770)),
  shot='Open VS Code with identities, with our connections ticked',
  notes='Source: docs/01-quickstart.md step 1; docs/03-configure.md, Connections and your identities; Local.'),

 dict(kicker='Your first task', title='Take the first lesson',
  left=[
   '**1.** On the board, press the **?** button at the bottom right. **How can I help?** opens.',
   '**2.** Press **First lesson**, then **Start**. A Copilot chat opens in VS Code.',
   '**3.** The agent takes you through one true story, the board, and one practice task that changes no repository. It stops after each part for your questions. About 20 minutes.',
   'You can also type `/harness-rookie-quick-start` in a Copilot chat.',
   'After that, a task is one sentence: what to do, and in which repository. The agent asks the rest.',
   'To look something up, ask the **Harness Guide** agent in Microsoft 365 Copilot. Its file **Start a task and give it the requirement** shows how a task begins.',
   ('co', ['[Company: the link to the Harness Guide agent, and who to ask for help.]']),
  ],
  pic=('how-can-i-help', None),
  notes='Source: the skill harness-rookie-quick-start (board label "First lesson"); docs/01-quickstart.md steps 3 and 7; AI Exploration > 2 Ask the Harness Guide.'),

 dict(kicker='When something goes wrong', title='Common problems, and their fixes',
  left=[
   '**`harness` is not recognized.** Reopen the terminal and VS Code. Then `echo $env:Path` must show `C:\\Users\\<you>\\bin` (pages 6 to 8).',
   '**`python` opens the Microsoft Store, or only `py` works.** Install Python from python.org with **Add python.exe to PATH**, then turn off python.exe and python3.exe in **App execution aliases** (page 2).',
   '**`harness doctor` warns that the path is too long, or under OneDrive.** Put the harness at `C:\\dev\\harness`. Already set up? Get a new copy there and use **Coming from an older copy?** at the top of Get ready.',
   '**Start Harness.cmd does nothing, or is blocked.** In PowerShell: `cd C:\\dev\\harness`, then `.harness\\bin\\harness.cmd task board`.',
  ],
  right=[
   '**CERTIFICATE_VERIFY_FAILED** (az, pip, a sign-in test). Card 4, **Network**, **Make**. Then **Restart VS Code** from the board.',
   '**git: SSL certificate problem.** See page 3.',
   '**The board says the port is in use.** It is running already: open `http://127.0.0.1:8765/`.',
   '**The board says it is not paired, and an approval is refused.** Press Enter in the black window of the board and open the new link it prints.',
   ('co', ['[Company: other problems people met here, with their fixes.]']),
  ],
  notes='Source: docs/03-configure.md, Getting ready (issue table), Encoding and long paths; docs/01-quickstart.md step 3; the skill harness-rookie-quick-start, Troubleshooting.'),

 dict(kicker='When something goes wrong', title='More problems, and their fixes',
  left=[
   '**The knowledge base step fails on the first commit.** git has no name or email: set `user.name` and `user.email` (page 2), then press **Finish setup** again.',
   '**The Copilot line is red.** Sign in to Copilot in VS Code, then wait a moment.',
   '**The VS Code line says the `code` command was not found.** Install VS Code again with **Add to PATH** on, then start the board again.',
  ],
  right=[
   '**After an upgrade, the agent’s commands are refused: a guardrail file is not what you accepted.** Start the board once: it accepts the new version when it starts.',
   '**`harness doctor` says `harness` on PATH is not this copy’s.** There is another copy on this computer. It works; Path had better point at the copy you use most.',
   '**Chinese text from a command is garbage.** Create `.harness\\policies\\cli.override.json` with `{"output": {"encoding": "native"}}`.',
  ],
  notes='Source: docs/03-configure.md, Getting ready (issue table); docs/01-quickstart.md, Common cases (upgrading); the board texts for Copilot and VS Code.'),

 dict(kicker='Later', title='Upgrade to a new version',
  left=[
   '**1.** Stop the board: Ctrl+C in its black window, or close the window.',
   '**2.** Get the new version into the same folder. If you cloned with git, type these, with the new version number (for example 1.7.46) in place of `<new version>`:',
   ('code', 'cd C:\\dev\\harness\ngit fetch --tags\ngit checkout <new version>'),
   'If you used a zip: download the new one, **Extract All** to a temporary folder, and copy what is inside **copilot-agentic-harness-<version>** over `C:\\dev\\harness`, letting it overwrite.',
   '**3.** Start the harness again. At its first start of a new version the board accepts the new guardrail files.',
   '**4.** In `C:\\dev\\harness`, run `harness doctor`. If it warns that `harness` on PATH differs from this copy’s, copy it again (no helpdesk):',
   ('code', 'Copy-Item .harness\\bin\\harness.cmd $env:USERPROFILE\\bin\\'),
  ],
  right=[
   '**What stays:** your knowledge base, tasks, settings (the *.override.json files) and .harness\\runtime are not part of the harness, so an upgrade does not touch them.',
   '**What is replaced:** AGENTS.md, .github\\copilot-instructions.md, .github\\instructions, the harness’s skills and policies. If you changed one yourself, back it up first and put your change back after. The company’s copies need nothing: the board puts them back when it starts.',
   '**A new folder instead?** Use **Coming from an older copy?** at the top of Get ready, or type `/harness-reinstall` in the new copy. Do not copy by hand.',
   ('co', ['[Company: confirm before people rely on it. If git refuses with “Your local changes ... would be overwritten”, the files it names are usually the company’s copies in .github, which the board puts back. If you changed none yourself:]',
           ('mcode', 'git checkout --force <new version>')]),
  ],
  notes='Source: docs/01-quickstart.md step 1 (a changed launcher: copy it again) and Common cases (upgrading in the same folder, the zip from GitHub, a new copy in another folder). The git commands are the author\'s choice; the docs describe the zip.'),
]
