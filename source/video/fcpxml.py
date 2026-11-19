# Writes a Final Cut Pro XML (1.10 by default: FCP 10.6 and later import it; 1.11 needs FCP 10.6.6 or later).
# One event, one project: the frames as stills on the primary storyline, each sentence's audio connected below it (lane -1),
# and the room tone under the whole timeline below that (lane -2): with it, the gaps between clips are never digital silence.
# Between two stills, a Cross Dissolve transition on the primary storyline, centred on the edit point: the stills keep
# their places (a still has endless handles), the transition overlaps both by half its length.
# Every time is a whole number of frames, written as a rational number of seconds.
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

VERSION = 'x3'  # bump when the output changes, so build.py writes it again
CROSS_DISSOLVE = 'FxPlug:4731E73A-8DAC-4113-9A30-AE85B1761265'  # FCP's built-in Cross Dissolve (PAECrossDissolve)


def _url(path):
    return 'file://' + quote(str(Path(path).resolve()))


def write(out, *, title, event, fps, width, height, pictures, clips, total, version='1.10', captions=(), overlay=None,
          bed=None):
    """pictures: [dict(path, name, start, dur, xfade)] in frames, contiguous from 0 to total; xfade: frames of the
    cross-dissolve into this picture (even, 0 = a cut), centred on its start.
    clips: [dict(path, name, start, dur)] in frames, absolute; each must fall inside one picture.
    captions: [(lang, [(start, dur, rows)])]: SRT captions (role SRT?captionFormat=SRT.<lang>), one caption lane per language.
    overlay: dict(path, size, centre): a square video with alpha (the speaking avatar), the whole length, on the lane above the
    caption lanes, above the
    stills, at its own pixel size (adjust-conform none) with its centre moved to `centre` (x, y in pixels from the top left).
    adjust-transform's position is relative to the frame's centre, in per cent of the frame height, y up.
    bed: a mono 48 kHz wav as long as the timeline, the room tone between and under the clips' faded ends (build.room_bed)."""
    unit = {25: (100, 2500), 30: (100, 3000), 50: (100, 5000), 60: (100, 6000)}[fps]

    def t(frames):
        return '0s' if frames == 0 else f'{frames * unit[0]}/{unit[1]}s'

    root = ET.Element('fcpxml', version=version)
    res = ET.SubElement(root, 'resources')
    ET.SubElement(res, 'format', id='r1', name=f'FFVideoFormat1080p{fps}', frameDuration=t(1),
                  width=str(width), height=str(height), colorSpace='1-1-1 (Rec. 709)')
    ET.SubElement(res, 'format', id='r2', name='FFVideoFormatRateUndefined',
                  width=str(width), height=str(height), colorSpace='1-13-1')
    ids, n = {}, 3

    def asset(path, name, audio_frames=None):
        nonlocal n
        key = str(path)
        if key in ids:
            return ids[key]
        rid = f'r{n}'; n += 1; ids[key] = rid
        if audio_frames is None:
            a = ET.SubElement(res, 'asset', id=rid, name=name, start='0s', duration='0s',
                              hasVideo='1', format='r2', videoSources='1')
        else:
            a = ET.SubElement(res, 'asset', id=rid, name=name, start='0s', duration=t(audio_frames),
                              hasAudio='1', audioSources='1', audioChannels='1', audioRate='48000')
        ET.SubElement(a, 'media-rep', kind='original-media', src=_url(path))
        return rid

    for p in pictures:
        asset(p['path'], p['name'])
    if any(p.get('xfade') for p in pictures):
        ET.SubElement(res, 'effect', id='rfx', name='Cross Dissolve', uid=CROSS_DISSOLVE)
    if overlay:
        sz = str(overlay['size'])
        ET.SubElement(res, 'format', id='rov', frameDuration=t(1), width=sz, height=sz,
                      colorSpace='1-1-1 (Rec. 709)')
        a = ET.SubElement(res, 'asset', id='raov', name=Path(overlay['path']).stem, start='0s', duration=t(total),
                          hasVideo='1', format='rov', videoSources='1')
        ET.SubElement(a, 'media-rep', kind='original-media', src=_url(overlay['path']))
    for c in clips:
        asset(c['path'], c['name'], c['dur'])
    if bed:
        asset(bed, 'room tone', total)

    lib = ET.SubElement(root, 'library')
    ev = ET.SubElement(lib, 'event', name=event)
    proj = ET.SubElement(ev, 'project', name=title)
    seq = ET.SubElement(proj, 'sequence', format='r1', duration=t(total), tcStart='0s', tcFormat='NDF',
                        audioLayout='stereo', audioRate='48k')
    spine = ET.SubElement(seq, 'spine')
    # each still is used from an hour into its (endless) media, so a transition has frames on both sides of every cut;
    # a connected clip's offset is on the parent's own timeline, which starts at the parent's start
    base = 3600 * fps
    ci, ts = 0, 0
    caps = [(lane, lang, c) for lane, (lang, cl) in enumerate(captions, 1) for c in cl]
    for p in pictures:
        d = p.get('xfade') or 0
        if d and p['start']:
            assert d % 2 == 0 and d // 2 <= p['dur'], 'a transition must be an even number of frames, inside its clips'
            tr = ET.SubElement(spine, 'transition', name='Cross Dissolve', offset=t(p['start'] - d // 2), duration=t(d))
            ET.SubElement(tr, 'filter-video', ref='rfx', name='Cross Dissolve')
        v = ET.SubElement(spine, 'video', ref=ids[str(p['path'])], offset=t(p['start']), name=p['name'],
                          start=t(base), duration=t(p['dur']))
        end = p['start'] + p['dur']
        rel = lambda x: t(base + x - p['start'])
        if overlay and p['start'] == 0:  # connected to the first still, running past it to the end
            oc = ET.SubElement(v, 'asset-clip', ref='raov', lane=str(len(captions) + 1), offset=t(base), name='speaking avatar', start='0s',
                               duration=t(total))
            px = lambda d: f'{d / height * 100:.4f}'.rstrip('0').rstrip('.')
            ET.SubElement(oc, 'adjust-conform', type='none')
            ET.SubElement(oc, 'adjust-transform', position=f'{px(overlay["centre"][0] - width / 2)} {px(height / 2 - overlay["centre"][1])}')
        if bed and p['start'] == 0:  # connected to the first still, running past it to the end, under the voice
            ET.SubElement(v, 'asset-clip', ref=ids[str(bed)], lane='-2', offset=t(base), name='room tone', start='0s',
                          duration=t(total), audioRole='dialogue')
        while ci < len(clips) and clips[ci]['start'] < end:
            c = clips[ci]
            assert c['start'] >= p['start'], 'an audio clip starts before its picture'
            ET.SubElement(v, 'asset-clip', ref=ids[str(c['path'])], lane='-1', offset=rel(c['start']),
                          name=c['name'], start='0s', duration=t(c['dur']), audioRole='dialogue')
            ci += 1
        for lane, lang, (cs, cd, rows) in caps:
            if p['start'] <= cs < end:
                ts += 1
                cap = ET.SubElement(v, 'caption', lane=str(lane), offset=rel(cs), name=' '.join(rows)[:60],
                                    start='0s', duration=t(cd), role=f'SRT?captionFormat=SRT.{lang}')
                ET.SubElement(ET.SubElement(cap, 'text'), 'text-style', ref=f'ts{ts}').text = '\n'.join(rows)
                ET.SubElement(ET.SubElement(cap, 'text-style-def', id=f'ts{ts}'), 'text-style', font='.AppleSystemUIFont',
                              fontSize='13', fontFace='Regular', fontColor='1 1 1 1', backgroundColor='0 0 0 1')
    assert ci == len(clips), 'audio clips run past the last picture'
    ET.indent(root, space='  ')
    for tx in root.iter('text'):  # a caption's text is mixed content: no indentation whitespace inside it
        tx.text = None
        for c in tx:
            c.tail = None
    body = ET.tostring(root, encoding='unicode')
    Path(out).write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n\n' + body + '\n', encoding='utf-8')
