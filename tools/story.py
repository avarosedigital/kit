"""Ava Rose story frames, 1080x1920 at 2x.
Usage: python3 story.py stories.json outdir
stories.json: {"name": {"photo": "/abs.jpg", "kicker": "start here", "title": "...", "body": "...", "cta": "reply KIT"}}"""
import asyncio, json, sys, html, pathlib, base64
from playwright.async_api import async_playwright
from PIL import Image
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from carousel import F

E = lambda s: html.escape(html.unescape(s or ''))
CSS = f"""
@font-face{{font-family:Disp;src:{F('cormorant-garamond-latin-500-normal.ttf','font/ttf')}}}
@font-face{{font-family:DispI;src:{F('cormorant-garamond-latin-500-italic.ttf','font/ttf')}}}
@font-face{{font-family:Body;src:{F('dm-sans-latin-500-normal.woff','font/woff')}}}
*{{margin:0;box-sizing:border-box}} body{{width:1080px;height:1920px;overflow:hidden;font-family:Body;color:#FBF6EE}}
"""

def frame(s):
    b64 = base64.b64encode(pathlib.Path(s['photo']).read_bytes()).decode()
    cta = (f"<div style='display:inline-block;margin-top:56px;background:#F7E4E2;color:#A8646B;border-radius:99px;padding:22px 52px;"
           f"font-family:DispI;font-size:58px'>{E(s['cta'])}</div>") if s.get('cta') else ''
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div style='position:absolute;inset:0;background:url(data:image/jpeg;base64,{b64}) center/cover'></div>"
            "<div style='position:absolute;inset:0;background:linear-gradient(to bottom,rgba(42,33,27,.25),rgba(42,33,27,.05) 22%,rgba(42,33,27,.62) 46%,rgba(42,33,27,.9))'></div>"
            "<div style='position:absolute;top:250px;left:0;right:0;text-align:center;letter-spacing:10px;font-size:26px'>AVA ROSE</div>"
            "<div style='position:absolute;left:100px;right:100px;bottom:430px;text-align:center'>"
            f"<div style='font-family:DispI;font-size:72px;color:#F7E4E2'>{E(s.get('kicker'))}</div>"
            f"<div style='font-family:Disp;font-size:104px;line-height:1.05;margin-top:24px'>{E(s['title'])}</div>"
            f"<div style='font-size:38px;line-height:1.5;margin-top:36px;opacity:.92'>{E(s.get('body'))}</div>{cta}</div></body></html>")

async def main(data, out):
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(**({'executable_path':'/usr/bin/google-chrome'} if __import__('os').path.exists('/usr/bin/google-chrome') else {}))
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=2)
        for name, s in data.items():
            await pg.set_content(frame(s)); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(150)
            t = out / f'_{name}.png'; await pg.screenshot(path=str(t))
            Image.open(t).convert('RGB').resize((1080, 1920), Image.LANCZOS).save(out / f'{name}.jpg', quality=94); t.unlink()
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(json.load(open(sys.argv[1])), pathlib.Path(sys.argv[2])))
