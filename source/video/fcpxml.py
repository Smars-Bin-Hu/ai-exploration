# Writes a Final Cut Pro XML (1.10 by default: FCP 10.6 and later import it; 1.11 needs FCP 10.6.6 or later).
# One event, one project: the frames as stills on the primary storyline, each sentence's audio connected below it (lane -1).
# Every time is a whole number of frames, written as a rational number of seconds.
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote


def _url(path):
    return 'file://' + quote(str(Path(path).resolve()))


def write(out, *, title, event, fps, width, height, pictures, clips, total, version='1.10'):
    """pictures: [dict(path, name, start, dur)] in frames, contiguous from 0 to total.
    clips: [dict(path, name, start, dur)] in frames, absolute; each must fall inside one picture."""
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
    for c in clips:
        asset(c['path'], c['name'], c['dur'])

    lib = ET.SubElement(root, 'library')
    ev = ET.SubElement(lib, 'event', name=event)
    proj = ET.SubElement(ev, 'project', name=title)
    seq = ET.SubElement(proj, 'sequence', format='r1', duration=t(total), tcStart='0s', tcFormat='NDF',
                        audioLayout='stereo', audioRate='48k')
    spine = ET.SubElement(seq, 'spine')
    ci = 0
    for p in pictures:
        v = ET.SubElement(spine, 'video', ref=ids[str(p['path'])], offset=t(p['start']), name=p['name'],
                          start='0s', duration=t(p['dur']))
        end = p['start'] + p['dur']
        while ci < len(clips) and clips[ci]['start'] < end:
            c = clips[ci]
            assert c['start'] >= p['start'], 'an audio clip starts before its picture'
            # a connected clip's offset is on the parent's own timeline, which starts at the parent's start (0s)
            ET.SubElement(v, 'asset-clip', ref=ids[str(c['path'])], lane='-1', offset=t(c['start'] - p['start']),
                          name=c['name'], start='0s', duration=t(c['dur']), audioRole='dialogue')
            ci += 1
    assert ci == len(clips), 'audio clips run past the last picture'
    ET.indent(root, space='  ')
    body = ET.tostring(root, encoding='unicode')
    Path(out).write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n\n' + body + '\n', encoding='utf-8')
