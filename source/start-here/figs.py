# Figures for Start Here: SVG in fig/, then PNG (3x) for the PowerPoint. Run: ../../.venv/bin/python figs.py (needs Chrome).
import math, os, subprocess, json
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, 'fig')
os.makedirs(OUT, exist_ok=True)
INK = '#141414'; ACC = '#e8590c'

class Fig:
    def __init__(self, h=380, w=700): self.h=h; self.w=w; self.p=[]
    def box(self, x,y,w,h, lines, cls='box', dash=False, fs=17, tcls=None, rx=8):
        self.p.append(f'<rect class="{cls}{" dash" if dash else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')
        n=len(lines); lh=fs+6; y0 = y + h/2 - (n-1)*lh/2 + fs*0.35
        for i,t in enumerate(lines):
            k = tcls[i] if isinstance(tcls,list) else (tcls or '')
            self.p.append(f'<text class="{k}" x="{x+w/2}" y="{y0+i*lh:.1f}" text-anchor="middle" style="font-size:{fs}px">{t}</text>')
    def text(self, x,y,t, cls='', anchor='middle', fs=17):
        self.p.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{fs}px">{t}</text>')
    def arrow(self, x1,y1,x2,y2, acc=False, dash=False):
        cls = ('lna' if acc else 'ln') + (' dash' if dash else '')
        fill = ACC if acc else INK
        a = math.atan2(y2-y1, x2-x1); L=12; W=6
        bx, by = x2-L*math.cos(a), y2-L*math.sin(a); nx, ny = -math.sin(a), math.cos(a)
        self.p.append(f'<path class="{cls}" d="M{x1} {y1} L{bx:.1f} {by:.1f}"/>')
        self.p.append(f'<path d="M{x2} {y2} L{bx+W*nx:.1f} {by+W*ny:.1f} L{bx-W*nx:.1f} {by-W*ny:.1f}Z" fill="{fill}"/>')
    def raw(self, s): self.p.append(s)
    def save(self, name):
        open(f'{OUT}/{name}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">\n  '+'\n  '.join(self.p)+'\n</svg>\n')

def chain():
    f=Fig(400, 760)
    steps=['Read the requirement','Find the code','Write the code','Run tests on DEV','Check the data','Check the pipeline','Update the ticket','Review every line']
    for i,s in enumerate(steps):
        x=10+(i%4)*188; y=40 if i<4 else 200
        ai = (i==2)
        words=s.split(' '); lines=[' '.join(words[:2]),' '.join(words[2:])] if len(words)>2 else [s]
        f.box(x,y,172,96,lines,cls='lit' if ai else 'box',tcls='a' if ai else '')
        f.raw(f'<rect class="{"litf" if ai else "inkf"}" x="{x+120}" y="{y-12}" width="44" height="24" rx="12"/>')
        f.text(x+142,y+5,'AI' if ai else 'You','inv',fs=14)
    f.raw('<rect class="soft" x="10" y="326" width="740" height="60" rx="10"/>')
    f.text(380,362,'Copilot writes the code. Everything else is still yours.',fs=18)
    f.save('chain')

def axes():
    f=Fig(470, 740)
    f.arrow(150,420,150,20); f.arrow(150,420,730,420)
    f.text(138,40,'Vertical','a','end',18); f.text(138,64,'what it can do','m','end',15); f.text(138,84,'and knows','m','end',15)
    f.text(730,452,'Horizontal: how safe and easy it is to use','a','end',18)
    f.box(170,318,250,86,['Chat','answers you;','you do the rest'],fs=16,tcls=['a','',''])
    f.box(170,150,250,96,['Agent alone','does more by itself, but','you watch every step'],fs=16,tcls=['a','',''])
    f.box(470,36,250,96,['Agent + harness','takes the whole task,','and you can trust it'],cls='lit',tcls=['a','',''],fs=16)
    f.arrow(295,318,295,250,dash=True); f.arrow(420,170,470,110,acc=True)
    f.save('axes')

def outside():
    # Agent = Model + Harness, as three boxes
    f=Fig(400, 760)
    f.box(10,40,180,250,['Model','','thinks and writes','','Opus, Sonnet,','GPT …'],tcls=['a','','','','m','m'],fs=17)
    f.text(212,176,'+','a',fs=34)
    f.raw('<rect class="lit" x="236" y="40" width="300" height="250" rx="10"/>')
    f.text(386,74,'Harness','a',fs=18)
    f.text(386,112,'Vertical:','a',fs=16); f.text(386,136,'what the agent can','',fs=16); f.text(386,158,'reach and know','',fs=16)
    f.text(386,204,'Horizontal:','a',fs=16); f.text(386,228,'what keeps it','',fs=16); f.text(386,250,'safe and easy to use','',fs=16)
    f.text(560,176,'=','a',fs=34)
    f.box(584,40,166,250,['An agent','you can hand','a whole task to'],tcls=['a','',''],fs=17)
    f.raw('<rect class="soft" x="10" y="318" width="740" height="66" rx="10"/>')
    f.text(380,346,'A bigger model changes only the first box.',fs=17)
    f.text(380,370,'The bill goes up; the problems stay.','m',fs=16)
    f.save('outside')

def mapping():
    W=1100; FS=18; LH=28
    rows=[('1. AI only writes code',[('Vertical',['It reads and updates tickets','It finds why a pipeline failed','It runs tests on DEV and IST'])]),
          ('2. It does not know our systems',[('Vertical',['It learns our systems once and keeps what it learned']),
                                              ('Horizontal',['You start a task from a short form, not a long prompt'])]),
          ('3. I do not dare to let go',[('Horizontal',['You approve the plan and the result','You approve every write to a ticket or a database','Code blocks dangerous actions','A second agent checks the work'])]),
          ('4. The boss gets no answers',[('Horizontal',['One page shows every task','Reports show where the time and money went'])])]
    y=56; parts=[]
    for prob,subs in rows:
        y0=y
        for ab,items in subs:
            h=max(56, 22+len(items)*LH)
            parts.append(('sub',y,h,ab,items)); y+=h+10
        parts.append(('prob',y0,y-10-y0,prob)); y+=14
    f=Fig(y, W)
    f.text(150,30,'The problem','m',fs=16); f.text(410,30,'The ability','m',fs=16); f.text(790,30,'In my harness','m',fs=16)
    for p in parts:
        if p[0]=='prob':
            _,y0,h,prob=p; f.box(10,y0,290,h,[prob],fs=FS)
        else:
            _,ys,h,ab,items=p
            f.arrow(300,ys+h/2,340,ys+h/2)
            f.box(340,ys,140,h,[ab],cls='lit',tcls='a',fs=FS)
            f.arrow(480,ys+h/2,520,ys+h/2,acc=True)
            f.raw(f'<rect class="box" x="520" y="{ys}" width="{W-530}" height="{h}" rx="8"/>')
            t0=ys+h/2-(len(items)-1)*LH/2+FS*0.35
            for i,it in enumerate(items):
                f.raw(f'<circle class="litf" cx="544" cy="{t0+i*LH-FS*0.33:.1f}" r="4"/>')
                f.text(558,f'{t0+i*LH:.1f}',it,'','start',FS)
    f.save('mapping')

def envs():
    f=Fig(330, 900)
    f.text(450,32,'What the agent may do on each database','a',fs=19)
    f.box(10,56,420,190,['DEV and IST','','Reads run.','Changes wait for your approval,','or run after you open it','for this task.'],cls='lit',tcls=['a','','','','',''],fs=18)
    f.box(450,56,215,190,['QAT','','Not opened','by default.'],tcls=['a','','',''],fs=18)
    f.box(685,56,205,190,['PROD','','Read only.','Never opened','for changes.'],tcls=['a','','','',''],fs=18)
    f.raw('<rect class="soft" x="10" y="266" width="880" height="52" rx="10"/>')
    f.text(450,299,'Every command and what it returned is kept in the task.',fs=17)
    f.save('envs')

def what():
    # what the harness is, physically
    f=Fig(450, 760)
    f.box(10,20,130,60,['You'],tcls='a',fs=18)
    f.arrow(140,50,300,50); f.text(220,38,'start tasks · approve','m',fs=14)
    f.box(300,20,450,60,['The board: a page in your browser'],fs=17)
    f.raw('<rect class="lit" x="10" y="120" width="740" height="150" rx="10"/>')
    f.text(380,150,'Harness: a folder on your computer','a',fs=18)
    for i,(a,b) in enumerate([('Rules','Copilot reads'),('Checks before and after','every step'),('One folder','per task')]):
        f.box(30+i*240,168,220,82,[a,b],fs=16)
    f.arrow(640,120,640,82,acc=True); f.text(652,106,'shows each task','m','start',14)
    f.arrow(160,270,160,312,acc=True); f.text(172,296,'rules and checks','m','start',14)
    f.box(10,312,300,70,['Copilot agent','in VS Code'],tcls=['a',''],fs=17)
    f.arrow(310,347,470,347); f.text(390,326,'reads and writes,','m',fs=14); f.text(390,370,'through the checks','m',fs=14)
    f.box(470,312,280,70,['Azure DevOps · DEV and IST','your code'],fs=16)
    f.raw('<rect class="soft" x="10" y="400" width="740" height="40" rx="10"/>')
    f.text(380,426,'No server. It needs only Python.',fs=17)
    f.save('what')

def reviews():
    # the two reviews behind the report
    f=Fig(440, 760)
    f.box(10,14,740,58,['One task’s records: every action, what the gate said, the thinking before each step'],fs=16)
    f.arrow(160,72,160,110); f.arrow(540,72,540,110,acc=True)
    f.raw('<rect class="box" x="10" y="110" width="300" height="220" rx="8"/>')
    f.text(160,146,'/harness-task-report','a',fs=17)
    for i,t in enumerate(['reads the numbers, and says','where the time and usage','went, and why']): f.text(160,190+i*26,t,fs=16)
    f.raw('<rect class="lit" x="330" y="110" width="420" height="220" rx="8"/>')
    f.text(540,146,'Agent Performance Review','a',fs=17)
    for i,t in enumerate(['1. A program marks spots that look like detours.','2. An agent judges each one with evidence:','    harness limit · agent mistake · environment ·','    missing knowledge · guardrails working','3. It names the file to change.']):
        f.text(350,182+i*28,t,'m' if t.startswith('    ') else '','start',15.5)
    f.raw('<rect class="soft" x="10" y="352" width="740" height="72" rx="10"/>')
    f.text(380,382,'Only you can start either one. Neither changes the task it reviews.',fs=16)
    f.text(380,406,'A cause in the harness goes to the person who maintains it.','m',fs=15)
    f.save('reviews')

def tree():
    f=Fig(420, 820)
    rows=[(0,'AI Exploration/','a',''),(1,'Start Here','','you are here'),(1,'Harness Engineering 101/','','short courses: Basic, Advanced, Mindset'),
          (1,'Showcase/','',''),(2,'Real Tasks/','','real task pages, each with a one-page note'),(2,'Lessons/','','wrong turns I took on the way'),
          (1,'Harness/','','install package, our knowledge base,'),(2,'','','the programs it needs, and the guides')]
    for i,(d,t,c,note) in enumerate(rows):
        y=40+i*50; x=30+d*40
        if d and t: f.raw(f'<path class="lnm" d="M{x-24} {y-34} V{y-6} H{x-8}"/>')
        if t: f.raw(f'<rect class="{"litf" if d<2 else "soft"}" x="{x}" y="{y-15}" width="18" height="14" rx="2"/>')
        tx=x+28
        if t: f.text(tx,y,t,c or ('' if d<2 else ''),'start',18)
        if note:
            nx = 330 if t else 330
            f.text(nx,y,note,'m','start',16)
    f.save('tree')

CSS = '''text{font-family:Georgia,"Times New Roman",serif;fill:#141414}
.m{fill:#6b6b6b;font-style:italic}.a{fill:#e8590c;font-weight:bold}.inv{fill:#fff;font-family:Arial,sans-serif;font-weight:bold}
.box{fill:#fff;stroke:#141414;stroke-width:1.5}.soft{fill:#f2f1ec}.lit{fill:#fff;stroke:#e8590c;stroke-width:2.2}
.litf{fill:#e8590c}.inkf{fill:#141414}.ln{stroke:#141414;stroke-width:1.5;fill:none}.lna{stroke:#e8590c;stroke-width:2;fill:none}
.lnm{stroke:#cfcfca;stroke-width:1.5;fill:none}.dash{stroke-dasharray:5 5}'''

def main():
    names=[]
    for fn in (chain, axes, outside, what, mapping, envs, reviews, tree): fn(); names.append(fn.__name__)
    # inline the CSS so each SVG stands alone, then render PNGs with Chrome
    for n in names:
        p=f'{OUT}/{n}.svg'; s=open(p).read()
        s=s.replace('>\n',f'>\n  <style>{CSS}</style>\n',1); open(p,'w').write(s)
    js = os.path.join(H, '_render.mjs')
    open(js,'w').write('''import { createRequire } from 'node:module';
const { chromium } = createRequire(process.env.HOME + '/Developer/smarshu.com/package.json')('playwright-core');
const [dir, ...names] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const p = await b.newPage({ deviceScaleFactor: 3 });
for (const n of names) { await p.goto('file://' + dir + '/' + n + '.svg'); const e = await p.$('svg'); await e.screenshot({ path: dir + '/' + n + '.png', omitBackground: false }); }
await b.close();''')
    subprocess.run(['node', js, OUT, *names], check=True); os.remove(js)
    print('figures:', ' '.join(names))
main()
