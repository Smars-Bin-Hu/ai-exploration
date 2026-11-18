# Writes a Final Cut Pro XML (1.10 by default: FCP 10.6 and later import it; 1.11 needs FCP 10.6.6 or later).
# One event, one project: the frames as stills on the primary storyline, each sentence's audio connected below it (lane -1).
# Every time is a whole number of frames, written as a rational number of seconds.
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote


def _url(path):
    return 'file://' + quote(str(Path(path).resolve()))


def write(out, *, title, event, fps, width, height, pictures, clips, total, version='1.10', captions=(), overlay=None):
    """pictures: [dict(path, name, start, dur)] in frames, contiguous from 0 to total.
    clips: [dict(path, name, start, dur)] in frames, absolute; each must fall inside one picture.
    captions: [(lang, [(start, dur, rows)])]: SRT captions (role SRT?captionFormat=SRT.<lang>), one caption lane per language.
    overlay: dict(path, size, centre): a square video with alpha (the speaking avatar), the whole length, on the lane above the
    caption lanes, above the
    stills, at its own pixel size (adjust-conform none) with its centre moved to `centre` (x, y in pixels from the top left).
    adjust-transform's position is relative to the frame's centre, in per cent of the frame height, y up."""
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
    if overlay:
        sz = str(overlay['size'])
        ET.SubElement(res, 'format', id='rov', frameDuration=t(1), width=sz, height=sz,
                      colorSpace='1-1-1 (Rec. 709)')
        a = ET.SubElement(res, 'asset', id='raov', name=Path(overlay['path']).stem, start='0s', duration=t(total),
                          hasVideo='1', format='rov', videoSources='1')
        ET.SubElement(a, 'media-rep', kind='original-media', src=_url(overlay['path']))
    for c in clips:
        asset(c['path'], c['name'], c['dur'])

    lib = ET.SubElement(root, 'library')
    ev = ET.SubElement(lib, 'event', name=event)
    proj = ET.SubElement(ev, 'project', name=title)
    seq = ET.SubElement(proj, 'sequence', format='r1', duration=t(total), tcStart='0s', tcFormat='NDF',
                        audioLayout='stereo', audioRate='48k')
    spine = ET.SubElement(seq, 'spine')
    ci, ts = 0, 0
    caps = [(lane, lang, c) for lane, (lang, cl) in enumerate(captions, 1) for c in cl]
    for p in pictures:
        v = ET.SubElement(spine, 'video', ref=ids[str(p['path'])], offset=t(p['start']), name=p['name'],
                          start='0s', duration=t(p['dur']))
        end = p['start'] + p['dur']
        if overlay and p['start'] == 0:  # connected to the first still, running past it to the end
            oc = ET.SubElement(v, 'asset-clip', ref='raov', lane=str(len(captions) + 1), offset='0s', name='speaking avatar', start='0s',
                               duration=t(total))
            px = lambda d: f'{d / height * 100:.4f}'.rstrip('0').rstrip('.')
            ET.SubElement(oc, 'adjust-conform', type='none')
            ET.SubElement(oc, 'adjust-transform', position=f'{px(overlay["centre"][0] - width / 2)} {px(height / 2 - overlay["centre"][1])}')
        while ci < len(clips) and clips[ci]['start'] < end:
            c = clips[ci]
            assert c['start'] >= p['start'], 'an audio clip starts before its picture'
            # a connected clip's offset is on the parent's own timeline, which starts at the parent's start (0s)
            ET.SubElement(v, 'asset-clip', ref=ids[str(c['path'])], lane='-1', offset=t(c['start'] - p['start']),
                          name=c['name'], start='0s', duration=t(c['dur']), audioRole='dialogue')
            ci += 1
        for lane, lang, (cs, cd, rows) in caps:
            if p['start'] <= cs < end:
                ts += 1
                cap = ET.SubElement(v, 'caption', lane=str(lane), offset=t(cs - p['start']), name=' '.join(rows)[:60],
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
