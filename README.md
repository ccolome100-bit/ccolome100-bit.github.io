# ⚡ Bit a Bit — blog automático de tecnología e IA

Blog estático en español que **escribe y publica un artículo nuevo cada día** con la API de Claude, con diseño moderno (modo oscuro, buscador, portada destacada) y monetización preparada (Google AdSense + Amazon Afiliados).

Coste mensual aproximado: **0 € de hosting** (GitHub Pages) + el dominio (~1 €/mes) + la API de Claude (unos céntimos por artículo; consulta los precios actuales en anthropic.com/pricing).

## Qué incluye

- `scripts/build.py` · genera todo el sitio en `public/`: portada, artículos, categorías con paginación, buscador, sitemap.xml, RSS, robots.txt, ads.txt, 404 y páginas legales (privacidad con cláusula de AdSense, cookies, aviso legal, sobre nosotros, contacto).
- `scripts/generate_post.py` · escribe el siguiente artículo de `keywords.csv` con Claude. Cuando quedan pocas palabras clave, pide ideas nuevas y rellena la cola sola.
- `.github/workflows/publicar.yml` · todos los días a las 06:17 UTC escribe un artículo, lo guarda en el repositorio, reconstruye la web y la publica.
- SEO: títulos y descripciones optimizados, canonical, Open Graph, datos estructurados `Article`, tabla de contenidos, enlaces internos y artículos relacionados.
- Anuncios: huecos arriba, dentro del artículo (2), barra lateral fija y al final. Mientras no tengas AdSense se ven como recuadros grises de ejemplo.

## Puesta en marcha (15 minutos)

1. **Crea un repositorio en GitHub** (puede ser privado si tienes plan que lo permita con Pages; si no, público) y sube esta carpeta:
   ```bash
   git init && git add . && git commit -m "Blog inicial"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/bitabit.git
   git push -u origin main
   ```
2. **Activa GitHub Pages:** repositorio › Settings › Pages › *Source*: **GitHub Actions**.
3. **Añade tu clave de Claude:** Settings › Secrets and variables › Actions › *New repository secret*
   - Nombre: `ANTHROPIC_API_KEY` · Valor: tu clave de <https://console.anthropic.com>
4. (Opcional) En la pestaña *Variables* de esa misma pantalla:
   - `AUTO_PUBLISH` = `false` → los artículos se guardan como borrador para revisarlos (recomendado al principio).
   - `POSTS_PER_RUN` = `2` → dos artículos al día.
5. **Pruébalo:** Actions › *Publicar artículo y desplegar* › **Run workflow**.

### Dominio propio
Settings › Pages › *Custom domain* → `tudominio.com`, y en tu proveedor de dominio crea los registros DNS que indica GitHub. Pon el mismo dominio en `config.json` → `base_url` (el generador crea el archivo `CNAME` solo).

## Uso diario

| Quiero… | Haz esto |
|---|---|
| Cambiar los temas que se escriben | Edita `keywords.csv` (columna `status` = `pendiente`) |
| Revisar un borrador | Abre el `.md` en `content/posts/`, edítalo y cambia `draft: true` → `false` |
| Escribir un artículo a mano | Copia uno existente en `content/posts/` y cámbialo |
| Cambiar nombre, colores o categorías | `config.json` y `static/style.css` |
| Ver el blog en mi ordenador | `pip install markdown && python scripts/build.py && python -m http.server -d public 8000` → http://localhost:8000 |

## Monetización

Todo el proceso (AdSense, consentimiento de cookies, bloques de anuncios, afiliados, cobros e impuestos) está en **[MONETIZACION.md](MONETIZACION.md)**.
