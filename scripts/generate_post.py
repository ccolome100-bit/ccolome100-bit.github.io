#!/usr/bin/env python3
"""
Escribe automáticamente el siguiente artículo de la cola (keywords.csv) usando la API de Claude.

- Toma la primera palabra clave con estado "pendiente".
- Pide a Claude un artículo útil, original y estructurado para SEO.
- Lo guarda en content/posts/AAAA-MM-DD-slug.md y marca la palabra clave como "hecho".
- Si AUTO_PUBLISH=false, el artículo se guarda como borrador (draft: true) para revisarlo antes.
- Si la cola se queda con pocas palabras clave, pide a Claude ideas nuevas y las añade.

Variables de entorno:
  ANTHROPIC_API_KEY   (obligatoria)
  CLAUDE_MODEL        (opcional, por defecto claude-sonnet-5-5)
  AUTO_PUBLISH        (opcional, "true" por defecto)
  POSTS_PER_RUN       (opcional, 1 por defecto)
"""
import csv, json, os, re, sys, unicodedata, urllib.request, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
KW_FILE = ROOT / "keywords.csv"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
AUTO_PUBLISH = os.environ.get("AUTO_PUBLISH", "true").lower() == "true"
PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))


def claude(prompt: str, max_tokens=8000) -> str:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({"model": MODEL, "max_tokens": max_tokens,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    return "".join(b.get("text", "") for b in data["content"])


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70]


def extract_json(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0))


def read_queue():
    with KW_FILE.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_queue(rows):
    with KW_FILE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["keyword", "category", "status"])
        w.writeheader()
        w.writerows(rows)


def existing_titles():
    out = []
    for f in POSTS.glob("*.md"):
        m = re.search(r"^title:\s*(.+)$", f.read_text(encoding="utf-8"), re.M)
        if m:
            out.append((m.group(1).strip().strip('"'), f.stem))
    return out


ARTICLE_PROMPT = """Eres el editor jefe de «{site}», un blog en español de España sobre tecnología práctica ({tagline}).
Escribe un artículo para la búsqueda: «{kw}» (categoría: {cat}).

OBJETIVO: que sea la mejor respuesta de Internet para esa búsqueda. Google y AdSense premian el contenido útil y original, y penalizan el relleno.

REGLAS DE CALIDAD
- Responde a la intención de búsqueda en las 2-3 primeras frases (sin introducciones vacías tipo «En el mundo actual...»).
- Pasos numerados concretos, con los nombres exactos de menús y botones (Android, iPhone, Windows o Mac cuando aplique).
- Añade un consejo propio, un error común a evitar y una sección «Preguntas frecuentes» con 3-4 preguntas (### cada una).
- Entre 1.100 y 1.800 palabras. Párrafos cortos (2-4 líneas). Usa ## para secciones y ### para subsecciones. Una tabla si ayuda a comparar.
- Tono cercano, tuteo, claro, sin exagerar ni prometer cosas imposibles. Nada de clickbait.
- No inventes datos, precios ni versiones concretas si no estás seguro; si algo cambia a menudo, dilo («los menús pueden variar según la versión»).
- No temas sensibles (política, salud, contenido adulto, armas, piratería, cracks o métodos para saltarse protecciones).
- Si recomiendas un producto físico, puedes insertar como mucho 2 enlaces con el formato [[amazon:búsqueda en amazon|Texto del botón]].
- Enlaza de forma natural a 1-3 artículos existentes del blog si encajan, con enlaces markdown a /slug/. Artículos existentes:
{existing}

Devuelve SOLO un objeto JSON válido, sin texto adicional, con estas claves:
{{"title": "título SEO de 50-65 caracteres, atractivo y honesto",
  "description": "meta descripción de 140-158 caracteres",
  "slug": "url-corta-sin-acentos",
  "emoji": "un emoji que represente el tema",
  "tags": ["3-5 etiquetas"],
  "body": "artículo completo en Markdown, SIN repetir el título como H1"}}"""


IDEAS_PROMPT = """Eres experto en SEO para un blog de tecnología práctica en español de España («{site}»).
Propón 30 búsquedas NUEVAS con mucho volumen y evergreen (que la gente busque todo el año), del tipo
«cómo...», «por qué...», «mejores... gratis», «qué es...», que se puedan responder con una guía práctica.
Categorías permitidas: {cats}. Evita temas sensibles, piratería y noticias de actualidad.
No repitas ninguna de estas: {used}
Devuelve SOLO JSON: {{"ideas": [{{"keyword": "...", "category": "clave_de_categoria"}}]}}"""


def refill_queue(rows):
    pending = [r for r in rows if r["status"] == "pendiente"]
    if len(pending) >= 10:
        return rows
    print("ℹ️  Pocas palabras clave pendientes: pidiendo ideas nuevas a Claude…")
    used = "; ".join(r["keyword"] for r in rows)
    data = extract_json(claude(IDEAS_PROMPT.format(site=CFG["site_name"], cats=", ".join(CFG["categories"]), used=used), 4000))
    known = {r["keyword"].lower() for r in rows}
    for i in data.get("ideas", []):
        if i["keyword"].lower() not in known and i.get("category") in CFG["categories"]:
            rows.append({"keyword": i["keyword"], "category": i["category"], "status": "pendiente"})
    return rows


def write_article(row):
    existing = existing_titles()
    date_prefix = re.compile(r"^\d{4}-\d{2}-\d{2}-")
    ex_txt = "\n".join("- %s → /%s/" % (t, date_prefix.sub("", s)) for t, s in existing[-60:]) or "(ninguno todavía)"
    cat_name = CFG["categories"][row["category"]]["name"]
    raw = claude(ARTICLE_PROMPT.format(site=CFG["site_name"], tagline=CFG["tagline"], kw=row["keyword"], cat=cat_name, existing=ex_txt))
    data = extract_json(raw)
    slug = slugify(data.get("slug") or data["title"])
    if any(s.endswith(slug) for _, s in existing):
        slug += "-" + dt.date.today().strftime("%m%d")
    words = len(re.findall(r"\w+", data["body"]))
    if words < 700:
        raise RuntimeError(f"Artículo demasiado corto ({words} palabras); no se guarda.")
    today = dt.date.today().isoformat()
    fm = (f'---\ntitle: "{data["title"].replace(chr(34), "")}"\n'
          f'description: "{data["description"].replace(chr(34), "")}"\n'
          f"date: {today}\ncategory: {row['category']}\nemoji: {data.get('emoji', '')}\n"
          f"tags: {', '.join(data.get('tags', []))}\nslug: {slug}\n"
          f"draft: {'false' if AUTO_PUBLISH else 'true'}\n---\n\n")
    path = POSTS / f"{today}-{slug}.md"
    path.write_text(fm + data["body"].strip() + "\n", encoding="utf-8")
    print(f"✍️  {'Publicado' if AUTO_PUBLISH else 'Borrador'}: {data['title']} ({words} palabras) → {path.name}")


def main():
    if not API_KEY:
        sys.exit("❌ Falta ANTHROPIC_API_KEY")
    rows = refill_queue(read_queue())
    done = 0
    for row in rows:
        if done >= PER_RUN:
            break
        if row["status"] != "pendiente":
            continue
        try:
            write_article(row)
            row["status"] = "hecho"
            done += 1
        except Exception as e:  # sigue con la siguiente si una falla
            print(f"⚠️  Error con «{row['keyword']}»: {e}")
            row["status"] = "error"
    save_queue(rows)
    if done == 0:
        sys.exit("❌ No se generó ningún artículo")


if __name__ == "__main__":
    main()
