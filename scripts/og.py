#!/usr/bin/env python3
"""
Genera una imagen para compartir (1200x630) por cada artículo y la añade a sus
etiquetas Open Graph / Twitter, para que salga una vista previa bonita al
compartir en WhatsApp, Facebook, X o Telegram.

Se ejecuta después de build.py:  python scripts/og.py
"""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # reutiliza config, categorías y lectura de artículos

OUT = build.OUT
OG_DIR = OUT / "og"
W, H = 1200, 630

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wrap(draw, text, fnt, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def make_image(title, label, color_hex, path):
    c1 = hex_rgb(color_hex)
    c2 = hex_rgb("#0ea5e9")
    a, b = mix(c1, (20, 20, 43), 0.35), mix(c2, (20, 20, 43), 0.45)
    small = Image.new("RGB", (24, 13))
    for y in range(13):
        for x in range(24):
            small.putpixel((x, y), mix(a, b, (x / 23) * 0.7 + (y / 12) * 0.3))
    img = small.resize((W, H), Image.BILINEAR)
    d = ImageDraw.Draw(img)
    # tarjeta blanca
    d.rounded_rectangle((60, 60, W - 60, H - 60), radius=36, fill=(255, 255, 255))
    # logo
    d.rounded_rectangle((110, 110, 170, 170), radius=14, fill=c1)
    d.polygon([(146, 118), (124, 146), (138, 146), (132, 164), (156, 134), (142, 134)], fill=(255, 255, 255))
    d.text((188, 140), build.CFG["site_name"], font=font(40), fill=(20, 20, 43), anchor="lm")
    # etiqueta de categoría
    lf = font(26)
    lw = d.textlength(label.upper(), font=lf)
    d.rounded_rectangle((110, 200, 110 + lw + 36, 246), radius=23, fill=mix(c1, (255, 255, 255), 0.85))
    d.text((128, 223), label.upper(), font=lf, fill=c1, anchor="lm")
    # título (ajusta el tamaño para que quepa)
    for size in (64, 58, 52, 46, 40):
        tf = font(size)
        lines = wrap(d, title, tf, W - 220)
        if len(lines) <= 4:
            break
    y = 280
    for ln in lines[:4]:
        d.text((110, y), ln, font=tf, fill=(20, 20, 43))
        y += int(size * 1.22)
    # dominio
    dom = build.BASE.split("://", 1)[-1]
    d.text((W - 110, H - 105), dom, font=font(28), fill=(110, 110, 130), anchor="rm")
    img.save(path, "PNG", optimize=True)


def inject(html_file, img_url, alt):
    html = html_file.read_text(encoding="utf-8")
    if 'property="og:image"' in html:
        return
    tags = (f'<meta property="og:image" content="{img_url}">\n'
            f'<meta property="og:image:width" content="{W}">\n'
            f'<meta property="og:image:height" content="{H}">\n'
            f'<meta property="og:image:alt" content="{build.esc(alt)}">\n'
            f'<meta name="twitter:image" content="{img_url}">\n')
    html = html.replace('<meta name="twitter:card"', tags + '<meta name="twitter:card"', 1)
    html_file.write_text(html, encoding="utf-8")


def main():
    OG_DIR.mkdir(parents=True, exist_ok=True)
    posts = build.load_posts()
    for p in posts:
        cat = build.CATS[p["category"]]
        make_image(p["title"], cat["name"], cat["color"], OG_DIR / f"{p['slug']}.png")
        f = OUT / p["slug"] / "index.html"
        if f.exists():
            inject(f, f"{build.BASE}/og/{p['slug']}.png", p["title"])
    # imagen por defecto para portada, categorías y páginas legales
    make_image(build.CFG["tagline"], "Guías prácticas", "#6d28d9", OG_DIR / "default.png")
    for f in OUT.rglob("index.html"):
        inject(f, f"{build.BASE}/og/default.png", build.CFG["site_name"])
    print(f"🖼️  Imágenes para compartir generadas: {len(posts) + 1}")


if __name__ == "__main__":
    main()
