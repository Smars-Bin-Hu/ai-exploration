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
    steps=['Read the requirement','Find the code','Write the code','Run tests on DEV','Check the data','Update the ticket','Check the pipeline','Review every line']
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
    f=Fig(470, 720)
    f.arrow(150,420,150,20); f.arrow(150,420,710,420)
    f.text(138,40,'Vertical','a','end',18); f.text(138,64,'what it can do','m','end',15); f.text(138,84,'and knows','m','end',15)
    f.text(710,452,'Horizontal: how safe and easy it is to use','a','end',18)
    f.box(170,330,230,70,['Chat AI','writes code you paste in'],fs=16,tcls=['a',''])
    f.box(170,150,240,96,['An agent alone','does more, but you','watch every step'],fs=16,tcls=['a','',''])
    f.box(460,36,240,96,['Agent + harness','takes the whole task,','and you can trust it'],cls='lit',tcls=['a','',''],fs=16)
    f.arrow(285,330,288,250,dash=True); f.arrow(410,170,460,110,acc=True)
    f.save('axes')

def outside():
    f=Fig(470, 720)
    f.box(10,150,170,120,['Model','Opus, Sonnet,','GPT ...'],tcls=['a','m','m'])
    f.text(205,218,'+','a',fs=34)
    f.raw('<rect class="lit" x="230" y="20" width="480" height="380" rx="14"/>')
    f.text(470,50,'Harness: the layer around the model','a',fs=18)
    f.text(350,84,'Vertical','a',fs=17); f.text(350,104,'what it can reach and know','m',fs=14)
    for i,t in enumerate(['our domain knowledge','tickets and pipelines','DEV and IST databases','finding the cause']):
        f.box(250,120+i*62,200,48,[t],fs=15)
    f.text(590,84,'Horizontal','a',fs=17); f.text(590,104,'what controls and checks it','m',fs=14)
    for i,t in enumerate(['short task forms','approvals','guardrails','independent review','board and reports']):
        f.box(490,118+i*54,200,42,[t],fs=15)
    f.text(360,448,'A bigger model changes only the left box. The bill goes up; the problems stay.','m',fs=15)
    f.save('outside')

def mapping():
    f=Fig(430, 1200)
    f.text(140,24,'The problem','m',fs=16); f.text(430,24,'The ability','m',fs=16); f.text(860,24,'In my harness','m',fs=16)
    rows=[('AI only writes code','Vertical','Tickets and pipelines · finding the cause · tests on DEV and IST'),
          ('It does not know our domain','Vertical','Our domain and the requirement'),
          ('A long prompt for every task','Horizontal','Start a task from a form'),
          ('I do not dare to let go','Horizontal','Two approvals · approval before outside writes · guardrails · independent review'),
          ('The boss gets no answers','Horizontal','The board · auditability')]
    for i,(a,b,c) in enumerate(rows):
        y=44+i*76
        f.box(10,y,260,58,[a],fs=16)
        f.arrow(270,y+29,330,y+29)
        f.box(330,y,200,58,[b],cls='lit',tcls='a',fs=17)
        f.arrow(530,y+29,590,y+29,acc=True)
        f.box(590,y,600,58,[c],fs=16)
    f.save('mapping')

def tree():
    f=Fig(430, 700)
    rows=[(0,'AI Exploration/','a'),(1,'Start Here  (you are here)','m'),(1,'Harness Engineering 101/',''),(2,'Basic/   Advanced/   Mindset/','m'),
          (1,'Showcase/',''),(2,'Real Tasks/   Lessons/','m'),(1,'Harness/',''),(2,'install package · knowledge base · programs/ · guides','m')]
    for i,(d,t,c) in enumerate(rows):
        y=40+i*48; x=30+d*40
        if d: f.raw(f'<path class="lnm" d="M{x-24} {y-32} V{y-6} H{x-8}"/>')
        if d<2: f.raw(f'<rect class="{"litf" if c=="" or d==0 else "soft"}" x="{x}" y="{y-15}" width="18" height="14" rx="2"/>')
        f.text(x+(28 if d<2 else 0),y,t,c,'start',18)
    f.save('tree')

CSS = '''text{font-family:Georgia,"Times New Roman",serif;fill:#141414}
.m{fill:#6b6b6b;font-style:italic}.a{fill:#e8590c;font-weight:bold}.inv{fill:#fff;font-family:Arial,sans-serif;font-weight:bold}
.box{fill:#fff;stroke:#141414;stroke-width:1.5}.soft{fill:#f2f1ec}.lit{fill:#fff;stroke:#e8590c;stroke-width:2.2}
.litf{fill:#e8590c}.inkf{fill:#141414}.ln{stroke:#141414;stroke-width:1.5;fill:none}.lna{stroke:#e8590c;stroke-width:2;fill:none}
.lnm{stroke:#cfcfca;stroke-width:1.5;fill:none}.dash{stroke-dasharray:5 5}'''

def main():
    names=[]
    for fn in (chain, axes, outside, mapping, tree): fn(); names.append(fn.__name__)
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
