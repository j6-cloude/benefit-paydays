"""Generate favicon (SVG, 32px PNG, 180px apple-touch-icon) and 1200x630 og image into gen/static/."""
import os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(OUT, exist_ok=True)
BG, INK, ACC, PAPER, LINE = "#faf7f2", "#2b2622", "#b45309", "#ffffff", "#e4dccf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect x="4" y="8" width="56" height="52" rx="10" fill="#ffffff" stroke="#2b2622" stroke-width="4"/>
<path d="M4 18a10 10 0 0 1 10-10h36a10 10 0 0 1 10 10v8H4z" fill="#b45309"/>
<rect x="16" y="2" width="6" height="14" rx="3" fill="#2b2622"/><rect x="42" y="2" width="6" height="14" rx="3" fill="#2b2622"/>
<path d="M20 43l8 8 16-17" fill="none" stroke="#b45309" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""
open(os.path.join(OUT, "favicon.svg"), "w").write(SVG)

def icon(n, bg=None):
    s = 8; W = n * s
    im = Image.new("RGBA", (W, W), bg or (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    u = W / 64
    R = lambda *a: [v * u for v in a]
    d.rounded_rectangle(R(4, 8, 60, 60), radius=10*u, fill=PAPER, outline=INK, width=int(4*u))
    d.rounded_rectangle(R(4, 8, 60, 28), radius=10*u, fill=ACC); d.rectangle(R(6, 18, 58, 26), fill=ACC)
    d.rounded_rectangle(R(4, 8, 60, 60), radius=10*u, outline=INK, width=int(4*u))
    d.rounded_rectangle(R(16, 2, 22, 16), radius=3*u, fill=INK); d.rounded_rectangle(R(42, 2, 48, 16), radius=3*u, fill=INK)
    d.line(R(20, 43, 28, 51, 44, 34), fill=ACC, width=int(6*u), joint="curve")
    return im.resize((n, n), Image.LANCZOS)

icon(32).save(os.path.join(OUT, "favicon-32.png"))
a = Image.new("RGBA", (180, 180), BG); ic = icon(140); a.paste(ic, (20, 20), ic); a.convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))

# og image 1200x630
W, H = 1200, 630
im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
# calendar motif on right
cx, cy, cw, ch = 810, 120, 340, 390
d.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=28, fill=PAPER, outline=INK, width=6)
d.rounded_rectangle([cx, cy, cx+cw, cy+90], radius=28, fill=ACC); d.rectangle([cx+3, cy+50, cx+cw-3, cy+90], fill=ACC)
d.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=28, outline=INK, width=6)
for x in (cx+80, cx+cw-96): d.rounded_rectangle([x, cy-30, x+18, cy+40], radius=9, fill=INK)
gx, gy, step = cx+34, cy+120, 56
for r in range(4):
    for c in range(5):
        x, y = gx + c*step + 14, gy + r*step + 14
        if (r, c) == (2, 2):
            d.ellipse([x-24, y-24, x+40, y+40], fill=ACC)
        else:
            d.ellipse([x, y, x+14, y+14], fill=LINE)
# text
d.text((70, 120), "Benefit", font=ImageFont.truetype(FB, 92), fill=INK)
d.text((70, 222), "Paydays", font=ImageFont.truetype(FB, 92), fill=ACC)
f2 = ImageFont.truetype(FR, 34)
d.text((72, 350), "When is my next payment?", font=f2, fill=INK)
d.text((72, 396), "Social Security · SSI · VA · SNAP", font=f2, fill="#5c534a")
fn = ImageFont.truetype(FB, 26); t = "Independent site · not a government agency"
tw = d.textlength(t, font=fn)
d.rounded_rectangle([70, 480, 70 + tw + 44, 548], radius=14, fill="#fff3d6", outline=ACC, width=3)
d.text((92, 496), t, font=fn, fill="#7c2d12")
im.save(os.path.join(OUT, "og-image.png"), optimize=True)
print("ok")
