# The phone preview of the English slides: the PDF twin's page images, one after another. Run after build.py: python3 preview_html.py <out.html>
import base64, glob, os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
pages = sorted(glob.glob(f'{H}/_pages/p*.png'))
figs = []
with tempfile.TemporaryDirectory() as t:
    for i, p in enumerate(pages, 1):
        out = f'{t}/p.jpg'
        subprocess.run(['sips', '-Z', '1600', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', p, '--out', out], check=True, capture_output=True)
        figs.append(f'<figure><img src="data:image/jpeg;base64,{base64.b64encode(open(out, "rb").read()).decode()}" alt="Slide {i}"><figcaption>{i:02d}</figcaption></figure>')
head = open(sys.argv[1]).read().split('<main>')[0] if os.path.exists(sys.argv[1]) else ''
page = head + f'<main><h1>Why AI-assisted development has not taken off · {len(pages)} slides</h1><p>Preview of the PowerPoint (the PDF twin, page by page).</p>' + ''.join(figs) + '</main>\n'
open(sys.argv[1], 'w').write(page)
print(sys.argv[1], len(page) // 1024, 'KB')
