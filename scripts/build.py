#!/usr/bin/env python3
"""
Generador estático del blog.
Lee content/posts/*.md + config.json y genera el sitio completo en /public:
portada, artículos, categorías, páginas legales, sitemap, RSS, robots, ads.txt y buscador.

Uso:  python scripts/build.py
"""
import json, re, shutil, html, math, datetime as dt
from pathlib import Path
from email.utils import format_datetime
import markdown

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "posts"
STATIC = ROOT / "static"
OUT = ROOT / "public"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
AD = CFG["adsense"]
CATS = CFG["categories"]
YEAR = dt.date.today().year

esc = lambda s: html.escape(str(s), quote=True)


# ───────────────────────── Contenido ─────────────────────────
def parse_post(path: Path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"Falta frontmatter en {path.name}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    if meta.get("draft", "false").lower() == "true":
        return None
    body_md = m.group(2)
    md = markdown.Markdown(extensions=["toc", "tables", "fenced_code", "sane_lists"],
                           extension_configs={"toc": {"permalink": False}})
    body_html = md.convert(body_md)
    words = len(re.findall(r"\w+", body_md))
    slug = meta.get("slug") or path.stem
    cat = meta.get("category", "apps")
    if cat not in CATS:
        cat = "apps"
    return {
        "slug": slug,
        "title": meta["title"],
        "description": meta.get("description", ""),
        "date": dt.date.fromisoformat(meta.get("date", str(dt.date.today()))),
        "updated": meta.get("updated"),
        "category": cat,
        "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "emoji": meta.get("emoji") or CATS[cat]["emoji"],
        "html": body_html,
        "toc": md.toc_tokens,
        "minutes": max(1, math.ceil(words / 220)),
        "url": f"/{slug}/",
    }


def load_posts():
    posts = [p for p in (parse_post(f) for f in CONTENT.glob("*.md")) if p]
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


# ───────────────────────── Anuncios ─────────────────────────
def ad_unit(position: str) -> str:
    """position: top | in_article | sidebar | bottom"""
    client = AD.get("client_id", "").strip()
    slot = AD.get(f"slot_{position}", "").strip()
    if client and slot:
        if position == "in_article":
            attrs = 'data-ad-layout="in-article" data-ad-format="fluid" style="display:block;text-align:center"'
        else:
            attrs = 'data-ad-format="auto" data-full-width-responsive="true" style="display:block"'
        return (f'<div class="ad ad-{position}"><span class="ad-label">Publicidad</span>'
                f'<ins class="adsbygoogle" {attrs} data-ad-client="{esc(client)}" data-ad-slot="{esc(slot)}"></ins>'
                f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>')
    if not client and AD.get("show_placeholders_when_empty", True):
        return f'<div class="ad ad-{position} ad-placeholder"><span class="ad-label">Publicidad</span><div>Espacio para anuncio · {position.replace("_", " ")}</div></div>'
    return ""  # con client_id y sin slot → lo gestionan los anuncios automáticos


def inject_in_article_ads(body: str) -> str:
    """Coloca anuncios justo antes de subtítulos H2 (no cortan listas ni párrafos):
    antes del 2.º H2 y, en artículos largos, antes de un H2 a mitad del texto."""
    parts = re.split(r"(?=<h2)", body)
    if len(parts) < 3:
        return body
    targets = {2}
    if len(parts) >= 6:
        targets.add(len(parts) // 2 + 1)
    return "".join((ad_unit("in_article") if i in targets else "") + p for i, p in enumerate(parts))


def amazon_links(body: str) -> str:
    """Convierte [[amazon:búsqueda|texto]] en enlace de afiliado."""
    tag = CFG.get("amazon_affiliate_tag", "").strip()
    def rep(m):
        q, txt = m.group(1), m.group(2) or m.group(1)
        url = f"https://www.amazon.es/s?k={q.replace(' ', '+')}" + (f"&tag={tag}" if tag else "")
        return f'<a class="aff" href="{esc(url)}" rel="sponsored nofollow noopener" target="_blank">{esc(txt)} →</a>'
    return re.sub(r"\[\[amazon:([^|\]]+)(?:\|([^\]]+))?\]\]", rep, body)


# ───────────────────────── Plantilla ─────────────────────────
def head(title, description, path, og_type="website", extra=""):
    client = AD.get("client_id", "").strip()
    ads = ""
    if client:
        ads = (f'<meta name="google-adsense-account" content="{esc(client)}">\n'
               f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(client)}" crossorigin="anonymous"></script>')
    ga = ""
    if CFG.get("google_analytics_id"):
        gid = esc(CFG["google_analytics_id"])
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{gid}');</script>")
    gsc = f'<meta name="google-site-verification" content="{esc(CFG["search_console_verification"])}">' if CFG.get("search_console_verification") else ""
    full_title = title if title == CFG["site_name"] else f"{title} | {CFG['site_name']}"
    return f"""<!DOCTYPE html>
<html lang="{CFG['language']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:site_name" content="{esc(CFG['site_name'])}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{esc(CFG['site_name'])}" href="/feed.xml">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚡</text></svg>">
<link rel="stylesheet" href="/style.css">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{gsc}
{ads}
{ga}
{extra}
</head>
<body>"""


def header():
    links = "".join(f'<a href="/categoria/{k}/">{v["emoji"]} {esc(v["name"])}</a>' for k, v in CATS.items())
    return f"""<header class="site-header">
  <div class="wrap nav">
    <a class="logo" href="/"><span class="logo-mark">⚡</span>{esc(CFG['site_name'])}</a>
    <nav class="cats">{links}</nav>
    <div class="nav-tools">
      <button class="icon-btn" id="searchBtn" aria-label="Buscar">🔍</button>
      <button class="icon-btn" id="themeBtn" aria-label="Cambiar tema">🌓</button>
    </div>
  </div>
  <div class="search-panel" id="searchPanel" hidden>
    <div class="wrap"><input id="searchInput" type="search" placeholder="¿Qué quieres solucionar hoy?" autocomplete="off"><div id="searchResults"></div></div>
  </div>
</header>
<div class="wrap">{ad_unit("top")}</div>"""


def footer():
    cats = "".join(f'<li><a href="/categoria/{k}/">{esc(v["name"])}</a></li>' for k, v in CATS.items())
    return f"""<footer class="site-footer">
  <div class="wrap footer-grid">
    <div><a class="logo" href="/"><span class="logo-mark">⚡</span>{esc(CFG['site_name'])}</a>
      <p>{esc(CFG['description'])}</p></div>
    <div><h4>Temas</h4><ul>{cats}</ul></div>
    <div><h4>Información</h4><ul>
      <li><a href="/sobre-nosotros/">Sobre nosotros</a></li>
      <li><a href="/contacto/">Contacto</a></li>
      <li><a href="/politica-de-privacidad/">Política de privacidad</a></li>
      <li><a href="/politica-de-cookies/">Política de cookies</a></li>
      <li><a href="/aviso-legal/">Aviso legal</a></li>
      <li><a href="/feed.xml">RSS</a></li></ul></div>
  </div>
  <div class="wrap copy">© {YEAR} {esc(CFG['site_name'])}. Algunos enlaces pueden ser de afiliado: si compras a través de ellos recibimos una pequeña comisión sin coste para ti.</div>
</footer>
<script src="/app.js" defer></script>
</body></html>"""


def cover(p, size=""):
    c = CATS[p["category"]]["color"]
    return f'<div class="cover {size}" style="--c:{c}"><span>{p["emoji"]}</span></div>'


def card(p):
    cat = CATS[p["category"]]
    return f"""<article class="card">
  <a href="{p['url']}" class="card-link" aria-label="{esc(p['title'])}"></a>
  {cover(p)}
  <div class="card-body">
    <span class="pill" style="--c:{cat['color']}">{esc(cat['name'])}</span>
    <h3>{esc(p['title'])}</h3>
    <p>{esc(p['description'])}</p>
    <div class="meta">{fmt_date(p['date'])} · {p['minutes']} min</div>
  </div>
</article>"""


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
fmt_date = lambda d: f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def write(path: str, content: str):
    f = OUT / path.strip("/") / "index.html" if not path.endswith((".xml", ".txt", ".json", ".html")) else OUT / path.strip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


# ───────────────────────── Páginas ─────────────────────────
def build_post(p, posts):
    cat = CATS[p["category"]]
    related = [x for x in posts if x["category"] == p["category"] and x["slug"] != p["slug"]][:3]
    if len(related) < 3:
        related += [x for x in posts if x not in related and x["slug"] != p["slug"]][: 3 - len(related)]
    toc = ""
    if len(p["toc"]) >= 3:
        items = "".join(f'<li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in p["toc"])
        toc = f'<details class="toc" open><summary>En este artículo</summary><ol>{items}</ol></details>'
    body = amazon_links(inject_in_article_ads(p["html"]))
    ld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": p["title"], "description": p["description"],
        "datePublished": p["date"].isoformat(), "dateModified": p["updated"] or p["date"].isoformat(),
        "author": {"@type": "Organization", "name": CFG["author"]},
        "publisher": {"@type": "Organization", "name": CFG["site_name"]},
        "mainEntityOfPage": f"{BASE}{p['url']}", "inLanguage": CFG["language"],
    }
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    rel_html = "".join(card(r) for r in related)
    share_url = f"{BASE}{p['url']}"
    tags = "".join(f'<span class="tag">#{esc(t)}</span>' for t in p["tags"])
    page = head(p["title"], p["description"], p["url"], "article", extra) + header() + f"""
<main class="wrap post-layout">
  <article class="post">
    <nav class="crumbs"><a href="/">Inicio</a> › <a href="/categoria/{p['category']}/">{esc(cat['name'])}</a></nav>
    <span class="pill" style="--c:{cat['color']}">{cat['emoji']} {esc(cat['name'])}</span>
    <h1>{esc(p['title'])}</h1>
    <p class="lead">{esc(p['description'])}</p>
    <div class="meta">Por {esc(CFG['author'])} · {fmt_date(p['date'])} · {p['minutes']} min de lectura</div>
    {cover(p, "cover-hero")}
    {toc}
    <div class="prose">{body}</div>
    <div class="tags">{tags}</div>
    <div class="share">Compartir:
      <a target="_blank" rel="noopener" href="https://wa.me/?text={esc(p['title'])}%20{share_url}">WhatsApp</a>
      <a target="_blank" rel="noopener" href="https://twitter.com/intent/tweet?url={share_url}&text={esc(p['title'])}">X</a>
      <a target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u={share_url}">Facebook</a>
      <a target="_blank" rel="noopener" href="https://t.me/share/url?url={share_url}">Telegram</a>
    </div>
    {ad_unit("bottom")}
  </article>
  <aside class="sidebar">
    <div class="sticky">
      {ad_unit("sidebar")}
      <div class="box"><h4>Más leídos</h4><ol class="popular">{''.join(f'<li><a href="{x["url"]}">{esc(x["title"])}</a></li>' for x in posts[:5])}</ol></div>
    </div>
  </aside>
</main>
<section class="wrap related"><h2>Te puede interesar</h2><div class="grid">{rel_html}</div></section>
""" + footer()
    write(p["url"], page)


def build_list(posts, path, title, description, hero=None):
    per = CFG.get("posts_per_page", 12)
    pages = max(1, math.ceil(len(posts) / per))
    for n in range(pages):
        chunk = posts[n * per:(n + 1) * per]
        url = path if n == 0 else f"{path}pagina/{n + 1}/"
        top = hero if (hero and n == 0) else f'<section class="list-head"><h1>{esc(title)}</h1><p>{esc(description)}</p></section>'
        cards = chunk
        featured = ""
        if hero and n == 0 and chunk:
            f = chunk[0]
            cat = CATS[f["category"]]
            featured = f"""<article class="featured"><a class="card-link" href="{f['url']}" aria-label="{esc(f['title'])}"></a>
              {cover(f, "cover-big")}<div class="featured-body"><span class="pill" style="--c:{cat['color']}">{esc(cat['name'])}</span>
              <h2>{esc(f['title'])}</h2><p>{esc(f['description'])}</p><div class="meta">{fmt_date(f['date'])} · {f['minutes']} min</div></div></article>"""
            cards = chunk[1:]
        grid = "".join(card(p) for p in cards[:6]) + ("" if len(cards) <= 6 else f'</div>{ad_unit("in_article")}<div class="grid">' + "".join(card(p) for p in cards[6:]))
        if not chunk:
            grid = '<p class="meta">Muy pronto publicaremos las primeras guías de esta sección. 🚀</p>'
        pager = ""
        if pages > 1:
            prev = f'<a href="{path if n == 1 else f"{path}pagina/{n}/"}">← Anteriores</a>' if n > 0 else "<span></span>"
            nxt = f'<a href="{path}pagina/{n + 2}/">Siguientes →</a>' if n < pages - 1 else "<span></span>"
            pager = f'<nav class="pager">{prev}<span>Página {n + 1} de {pages}</span>{nxt}</nav>'
        page = head(title, description, url) + header() + f"""<main class="wrap">{top}{featured}<div class="grid">{grid}</div>{pager}</main>""" + footer()
        write(url, page)


def build_home(posts):
    chips = "".join(f'<a class="chip" style="--c:{v["color"]}" href="/categoria/{k}/">{v["emoji"]} {esc(v["name"])}</a>' for k, v in CATS.items())
    hero = f"""<section class="hero">
  <h1>{esc(CFG['tagline'])}</h1>
  <p>{esc(CFG['description'])}</p>
  <div class="chips">{chips}</div>
</section>"""
    build_list(posts, "/", CFG["site_name"], CFG["description"], hero)


def static_page(slug, title, body_html):
    page = head(title, f"{title} de {CFG['site_name']}", f"/{slug}/") + header() + \
        f'<main class="wrap narrow"><article class="post"><h1>{esc(title)}</h1><div class="prose">{body_html}</div></article></main>' + footer()
    write(f"/{slug}/", page)


def build_legal():
    n, mail, owner = esc(CFG["site_name"]), esc(CFG["contact_email"]), esc(CFG["owner_legal_name"])
    static_page("sobre-nosotros", "Sobre nosotros", f"""
<p><strong>{n}</strong> nace con una idea sencilla: que cualquier persona pueda resolver sus problemas tecnológicos del día a día sin tener que entender jerga técnica.</p>
<p>Publicamos guías paso a paso sobre móviles, ordenadores, inteligencia artificial, seguridad digital y aplicaciones. Cada artículo se prueba y se revisa antes de publicarse, y lo actualizamos cuando cambian las apps o los sistemas.</p>
<h2>Cómo trabajamos</h2>
<ul><li>Usamos herramientas de IA para investigar y redactar borradores, y una persona del equipo revisa, comprueba y edita cada guía.</li>
<li>Si encuentras un error o algo ha cambiado, escríbenos y lo corregimos.</li>
<li>Nos financiamos con publicidad y enlaces de afiliado, que nunca influyen en nuestras recomendaciones.</li></ul>
<p>Contacto: <a href="mailto:{mail}">{mail}</a></p>""")
    static_page("contacto", "Contacto", f"""
<p>¿Tienes una duda, una sugerencia de artículo o has visto un error? Nos encanta leerte.</p>
<p>📧 Escríbenos a <a href="mailto:{mail}">{mail}</a> y te responderemos lo antes posible (normalmente en 48 horas laborables).</p>
<p>Para propuestas de colaboración o publicidad, indica «Colaboración» en el asunto.</p>""")
    static_page("politica-de-privacidad", "Política de privacidad", f"""
<p><em>Última actualización: {fmt_date(dt.date.today())}</em></p>
<h2>Responsable</h2><p>{owner} · Contacto: <a href="mailto:{mail}">{mail}</a>.</p>
<h2>Qué datos recogemos</h2><p>No pedimos registro. Si nos escribes por correo, usamos tu dirección y tu mensaje solo para responderte. Además, nosotros y terceros (como Google) utilizamos cookies y tecnologías similares para medir visitas y mostrar publicidad.</p>
<h2>Publicidad de Google</h2>
<p>Este sitio utiliza Google AdSense. Los proveedores externos, incluido Google, utilizan cookies para mostrar anuncios basados en las visitas anteriores del usuario a este u otros sitios web. Las cookies de publicidad permiten a Google y a sus socios mostrar anuncios basados en las visitas a este sitio y/o a otros sitios de Internet.</p>
<p>Puedes inhabilitar la publicidad personalizada en <a href="https://adssettings.google.com" rel="noopener" target="_blank">Configuración de anuncios de Google</a> o en <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. Más información sobre cómo usa Google los datos: <a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">policies.google.com/technologies/partner-sites</a>.</p>
<p>A los visitantes del Espacio Económico Europeo, Reino Unido y Suiza se les solicita su consentimiento mediante una plataforma de gestión del consentimiento certificada por Google antes de usar cookies publicitarias.</p>
<h2>Afiliados</h2><p>Participamos en programas de afiliados (por ejemplo, Amazon). Si compras a través de nuestros enlaces podemos recibir una comisión, sin coste adicional para ti.</p>
<h2>Base legal y derechos</h2><p>Tratamos los datos con tu consentimiento o por interés legítimo. Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a {mail}, y reclamar ante la autoridad de protección de datos competente.</p>""")
    static_page("politica-de-cookies", "Política de cookies", f"""
<p>Una cookie es un pequeño archivo que el sitio guarda en tu navegador.</p>
<h2>Cookies que usamos</h2>
<table><thead><tr><th>Tipo</th><th>Proveedor</th><th>Finalidad</th></tr></thead><tbody>
<tr><td>Técnicas</td><td>{n}</td><td>Recordar tu tema claro/oscuro (localStorage).</td></tr>
<tr><td>Consentimiento</td><td>Google (Privacidad y mensajes)</td><td>Guardar tus preferencias de cookies.</td></tr>
<tr><td>Publicidad</td><td>Google AdSense y socios</td><td>Mostrar y medir anuncios, personalizados o no según tu elección.</td></tr>
<tr><td>Analítica</td><td>Google Analytics (si está activo)</td><td>Estadísticas anónimas de visitas.</td></tr></tbody></table>
<h2>Cómo gestionarlas</h2><p>Puedes cambiar tu consentimiento en cualquier momento desde el enlace «Privacidad» del aviso de cookies, o borrar las cookies desde la configuración de tu navegador.</p>""")
    static_page("aviso-legal", "Aviso legal", f"""
<p>Titular del sitio: {owner}. Contacto: <a href="mailto:{mail}">{mail}</a>.</p>
<p>Los contenidos de {n} son informativos. Aunque los revisamos con cuidado, la tecnología cambia rápido y no garantizamos que toda la información esté siempre actualizada. Usa las guías bajo tu responsabilidad y haz copias de seguridad antes de hacer cambios importantes en tus dispositivos.</p>
<p>Los textos y diseños de este sitio están protegidos. Las marcas citadas pertenecen a sus respectivos propietarios y se mencionan solo con fines informativos.</p>""")
    page404 = head("Página no encontrada", "Error 404", "/404.html") + header() + \
        '<main class="wrap narrow center"><h1>404 · Esta página se ha ido de vacaciones 🏖️</h1><p><a class="btn" href="/">Volver al inicio</a></p></main>' + footer()
    write("/404.html", page404)


def build_feeds(posts):
    today = dt.date.today().isoformat()
    urls = [("/", today)] + [(f"/categoria/{k}/", today) for k in CATS] + [(p["url"], p["updated"] or p["date"].isoformat()) for p in posts]
    sm = "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{BASE}{p['url']}</link><guid>{BASE}{p['url']}</guid>"
        f"<pubDate>{format_datetime(dt.datetime.combine(p['date'], dt.time(8), dt.timezone.utc))}</pubDate>"
        f"<description>{esc(p['description'])}</description></item>" for p in posts[:30])
    write("/feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(CFG["site_name"])}</title>'
          f'<link>{BASE}/</link><description>{esc(CFG["description"])}</description><language>{CFG["language"]}</language>{items}</channel></rss>')
    client = AD.get("client_id", "").strip()
    if client:
        write("/ads.txt", f"google.com, {client.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
    index = [{"t": p["title"], "d": p["description"], "u": p["url"], "c": CATS[p["category"]]["name"]} for p in posts]
    write("/search.json", json.dumps(index, ensure_ascii=False))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    posts = load_posts()
    for p in posts:
        build_post(p, posts)
    build_home(posts)
    for k, v in CATS.items():
        build_list([p for p in posts if p["category"] == k], f"/categoria/{k}/", f"{v['emoji']} {v['name']}",
                   f"Guías y trucos de {v['name'].lower()} explicados paso a paso.")
    build_legal()
    build_feeds(posts)
    if "TU-DOMINIO" not in BASE and "github.io" not in BASE:
        (OUT / "CNAME").write_text(BASE.split("://", 1)[1] + "\n")
    print(f"✅ Sitio generado en {OUT} con {len(posts)} artículos")


if __name__ == "__main__":
    main()
