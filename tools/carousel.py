"""Ava Rose elegant-but-fun carousel renderer.
Usage: python3 carousel.py data.json outdir
data.json: {"name": {"photo": "/abs/photo.jpg", "slides": [["cover", hook, sub], ["content", num, title, body, box_or_null], ["cta", line, keyword?]]}}
Renders 1080x1350 PNGs at 2x then downsamples (crisp text)."""
import asyncio, json, sys, html, pathlib, base64
from playwright.async_api import async_playwright
from PIL import Image

import os
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + '/'
def F(n, mime):
    return f"url(data:{mime};base64,{base64.b64encode(open(FONTS+n,'rb').read()).decode()})"
E = lambda s: html.escape(html.unescape(s))
HANDLE = '@avarose.digital'
CSS = f"""
@font-face{{font-family:Disp;src:{F('cormorant-garamond-latin-500-normal.ttf','font/ttf')}}}
@font-face{{font-family:DispI;src:{F('cormorant-garamond-latin-500-italic.ttf','font/ttf')}}}
@font-face{{font-family:Body;src:{F('dm-sans-latin-400-normal.woff','font/woff')};font-weight:400}}
@font-face{{font-family:Body;src:{F('dm-sans-latin-500-normal.woff','font/woff')};font-weight:500}}
*{{box-sizing:border-box;margin:0}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:Body,sans-serif;color:#2A211B;background:#FBF6EE}}
.s{{width:1080px;height:1350px;position:relative;overflow:hidden;padding:92px 96px}}
.brand{{font-family:Body;font-weight:500;letter-spacing:9px;font-size:22px;text-transform:uppercase}}
.disp{{font-weight:500;font-family:Disp;line-height:1.04;letter-spacing:-.5px}}
.it{{font-family:DispI;font-weight:500}}
h1,h2{{font-weight:500}}
.foot{{position:absolute;left:96px;right:96px;bottom:64px;display:flex;justify-content:space-between;align-items:center;font-size:23px;letter-spacing:2px;font-weight:500}}
.pill{{border:1.5px solid currentColor;border-radius:99px;padding:9px 24px;font-family:DispI;font-size:28px;letter-spacing:.5px}}
.dot{{position:absolute;border-radius:50%}}
"""

def page(inner, n, total, dark=False):
    right = f"<span class='pill'>swipe &nbsp;&rarr;</span>" if n == 1 else (f"<span class='pill'>{n}/{total}</span>" if n < total else "<span class='pill'>save this &#9825;</span>")
    col = '#FBF6EE' if dark else '#6b5d53'
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='s'>{inner}"
            f"<div class='foot' style='color:{col}'><span>{HANDLE}</span>{right}</div></div></body></html>")

def cover(hook, sub, photo):
    b64 = base64.b64encode(pathlib.Path(photo).read_bytes()).decode()
    size = 104 if len(hook) < 34 else 92 if len(hook) < 52 else 80
    return (f"<div style='position:absolute;inset:0;background:url(data:image/jpeg;base64,{b64}) center/cover'></div>"
            "<div style='position:absolute;inset:0;background:rgba(42,33,27,.12)'></div>"
            "<div style='position:absolute;left:0;right:0;bottom:0;height:78%;background:linear-gradient(to bottom,rgba(42,33,27,0),rgba(42,33,27,.55) 45%,rgba(42,33,27,.86))'></div>"
            "<div class='brand' style='position:relative;color:#FBF6EE'>Ava Rose</div>"
            f"<div style='position:absolute;left:96px;right:96px;bottom:170px;color:#FBF6EE'>"
            f"<h1 class='disp' style='font-size:{size}px'>{E(hook)}</h1>"
            f"<div class='it' style='font-size:44px;margin-top:30px;color:#F7E4E2'>{E(sub)}</div></div>")

def content(num, title, body, box):
    b = (f"<div style='margin-top:46px;background:#F7E4E2;border-radius:28px;padding:38px 44px;font-size:34px;line-height:1.45;color:#2A211B;"
         f"border-left:6px solid #C9858B'>{E(box)}</div>") if box else ''
    numsize = 210 if len(num) <= 2 else 150
    return ("<div class='dot' style='right:-140px;top:-140px;width:440px;height:440px;background:#F7E4E2'></div>"
            "<div class='dot' style='right:150px;top:250px;width:34px;height:34px;background:#EADBCB'></div>"
            "<div class='brand' style='position:relative;color:#A8646B'>Ava Rose</div>"
            "<div style='position:absolute;left:96px;right:96px;top:0;bottom:150px;display:flex;flex-direction:column;justify-content:center'>"
            f"<div class='it' style='font-size:{numsize}px;line-height:.9;color:#C9858B'>{E(num)}</div>"
            f"<h2 class='disp' style='font-size:84px;margin-top:26px'>{E(title)}</h2>"
            "<div style='width:90px;height:2px;background:#C9858B;margin-top:34px'></div>"
            f"<p style='font-size:38px;line-height:1.5;margin-top:32px;color:#6b5d53'>{E(body)}</p>{b}</div>")

def cta(line, kw='KIT'):
    return ("<div style='position:absolute;inset:0;background:#F7E4E2'></div>"
            "<div class='dot' style='left:-180px;bottom:-200px;width:620px;height:620px;background:#EFD2D0'></div>"
            "<div class='dot' style='right:120px;top:210px;width:40px;height:40px;background:#C9858B'></div>"
            "<div class='brand' style='position:relative;color:#A8646B'>Want the full system?</div>"
            "<div style='position:absolute;left:96px;right:96px;top:0;bottom:150px;display:flex;flex-direction:column;justify-content:center'>"
            "<div class='it' style='font-size:96px;color:#2A211B'>comment</div>"
            f"<div class='disp' style='font-size:300px;line-height:.86;color:#A8646B;letter-spacing:6px'>{E(kw)}</div>"
            f"<p style='font-size:38px;line-height:1.5;margin-top:44px;color:#2A211B;max-width:820px'>{E(line)}</p>"
            "<div class='it' style='font-size:44px;margin-top:34px;color:#A8646B'>and I&rsquo;ll DM you the link &#9825;</div></div>")

async def main(data, out):
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path':'/usr/bin/google-chrome'} if __import__('os').path.exists('/usr/bin/google-chrome') else {}))
        pg = await b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=2)
        for name, c in data.items():
            d = out / name; d.mkdir(exist_ok=True); sl = c['slides']; total = len(sl)
            for n, s in enumerate(sl, 1):
                if s[0] == 'cover': h, dark = cover(s[1], s[2], c['photo']), True
                elif s[0] == 'content': h, dark = content(s[1], s[2], s[3], s[4] if len(s) > 4 else None), False
                else: h, dark = cta(s[1], s[2] if len(s) > 2 else 'KIT'), False
                await pg.set_content(page(h, n, total, dark)); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(150)
                tmp = d / f'_s{n}.png'; await pg.screenshot(path=str(tmp))
                Image.open(tmp).convert('RGB').resize((1080, 1350), Image.LANCZOS).save(d / f'slide{n}.jpg', quality=95); tmp.unlink()
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(json.load(open(sys.argv[1])), pathlib.Path(sys.argv[2])))
