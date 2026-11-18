# Draws one 1920x1080 PNG per `@` line of a scenes file, in the look of the decks (source/tools/deck.py):
# white paper, Georgia for words, Arial bold capitals in the accent orange for the kicker, the accent orange for a highlight box.
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
INK, MUTED, LIGHT, ACCENT, PAPER = '#141414', '#6B6B6B', '#D6D6D2', '#E8590C', '#FFFFFF'
FONTS = '/System/Library/Fonts/Supplemental/'
SERIF, SANS_BOLD = FONTS + 'Georgia.ttf', FONTS + 'Arial Bold.ttf'
RENDER_VERSION = '1'  # bump when the look changes, so every frame is drawn again

MARGIN_X, MARGIN_Y = 96, 72
CAPTION_ZONE = 150  # height kept under the image for a caption
BOX_WIDTH = 7


def _font(path, size):
    return ImageFont.truetype(path, size)


def _wrap(draw, text, font, width):
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if draw.textlength(trial, font=font) <= width or not line:
            line = trial
        else:
            lines.append(line); line = word
    if line:
        lines.append(line)
    return lines


def _tracked(draw, xy, text, font, fill, tracking):
    """Text with letter spacing (Pillow has none), like the deck's kicker."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def card(out, title, kicker=''):
    """A plain title card: a small orange kicker over big serif words, left-aligned on white."""
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    left, width = 160, W - 320
    size = 104
    while True:
        tf = _font(SERIF, size)
        lines = _wrap(d, title, tf, width)
        if len(lines) <= 4 or size <= 60:
            break
        size -= 8
    line_h = int(size * 1.22)
    kf = _font(SANS_BOLD, 30)
    kick_h = 30 + 36 if kicker else 0
    rule_h = 6 + 34
    block = rule_h + kick_h + line_h * len(lines)
    y = (H - block) // 2
    d.rectangle([left, y, left + 72, y + 6], fill=ACCENT)  # the short orange line
    y += rule_h
    if kicker:
        _tracked(d, (left, y), kicker.upper(), kf, ACCENT, 4)
        y += kick_h
    for ln in lines:
        d.text((left, y), ln, font=tf, fill=INK)
        y += line_h
    img.save(out, optimize=False)


def picture(out, src, box=None, caption='', full_bleed=False, crop=None):
    """An image fitted on white with a margin; optional orange box (fractions of the source image) and a caption under it.
    full_bleed: the source is already a 16:9 page in the deck look, so it fills the frame when there is no caption.
    crop: show only this region (fractions of the source image), scaled to fill the frame with a margin."""
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    s = Image.open(src).convert('RGBA')
    page = full_bleed  # a deck page is white already: no hairline around it, cropped or not
    if crop:
        cx, cy, cw, ch = crop
        sw, sh = s.size
        s = s.crop((round(cx * sw), round(cy * sh), round((cx + cw) * sw), round((cy + ch) * sh)))
        full_bleed = False
        if box:  # the box is in source fractions: move it into the crop, cut to its edges, drop it if outside
            x0, y0 = max(box[0], cx), max(box[1], cy)
            x1, y1 = min(box[0] + box[2], cx + cw), min(box[1] + box[3], cy + ch)
            box = ((x0 - cx) / cw, (y0 - cy) / ch, (x1 - x0) / cw, (y1 - y0) / ch) if x1 > x0 and y1 > y0 else None
    iw, ih = s.size
    if full_bleed and not caption:
        ax, ay, aw, ah = 0, 0, W, H
    else:
        ax, ay = MARGIN_X, MARGIN_Y
        aw = W - 2 * MARGIN_X
        ah = H - 2 * MARGIN_Y - (CAPTION_ZONE if caption else 0)
    scale = min(aw / iw, ah / ih)
    dw, dh = round(iw * scale), round(ih * scale)
    dx, dy = ax + (aw - dw) // 2, ay + (ah - dh) // 2
    img.paste(s.resize((dw, dh), Image.LANCZOS), (dx, dy), s.resize((dw, dh), Image.LANCZOS))
    if not page:
        d.rectangle([dx - 1, dy - 1, dx + dw, dy + dh], outline=LIGHT, width=1)
    if box:
        bx, by, bw, bh = box
        pad = BOX_WIDTH  # stroke sits just outside the marked area
        x0, y0 = dx + bx * dw - pad, dy + by * dh - pad
        x1, y1 = dx + (bx + bw) * dw + pad, dy + (by + bh) * dh + pad
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, outline=ACCENT, width=BOX_WIDTH)
    if caption:
        cf = _font(SERIF, 46)
        lines = _wrap(d, caption, cf, W - 2 * MARGIN_X)[:2]
        line_h = 58
        top = dy + dh + (H - MARGIN_Y // 2 - (dy + dh) - line_h * len(lines)) // 2
        for i, ln in enumerate(lines):
            tw = d.textlength(ln, font=cf)
            d.text(((W - tw) / 2, top + i * line_h), ln, font=cf, fill=INK)
    img.save(out, optimize=False)
