# 💰 Plan de monetización de Bit a Bit

Este blog ya tiene colocados los huecos de anuncios, el código de AdSense listo para activarse, `ads.txt` automático, páginas legales y enlaces de afiliado. Lo que queda son los pasos que **solo puedes hacer tú** porque exigen tu identidad, tu cuenta bancaria y tu firma.

---

## Fase 0 · Antes de nada (día 1)

1. **Compra un dominio propio** (≈ 10-15 €/año en Namecheap, Cloudflare, Dinahosting o IONOS). AdSense no aprueba subdominios gratuitos tipo `usuario.github.io`.
   - Ideas: `bitabit.es`, `bitabitguias.com`, `bitabit.blog` (comprueba disponibilidad).
2. Rellena `config.json`:
   - `base_url` → `https://tudominio.com`
   - `contact_email` → un correo real que leas (por ejemplo, reenvío gratis desde Cloudflare Email Routing).
   - `owner_legal_name` → tu nombre o tu empresa (sale en el aviso legal y la privacidad).
3. Conecta el dominio a GitHub Pages (ver README, sección Despliegue).

## Fase 1 · Conseguir contenido y tráfico (semanas 1-6)

AdSense revisa a mano si el sitio aporta valor. Las guías del sector recomiendan entre 20 y 60 artículos de más de 600 palabras antes de solicitarlo.

- El bot publica **1 artículo al día**. En 3-4 semanas tendrás 25-30.
- ⚠️ **Revisa los artículos.** Google penaliza el «contenido masivo generado sin valor añadido». Recomendado: pon `AUTO_PUBLISH=false` al principio; el bot dejará borradores (`draft: true`) y tú los lees, añades algún detalle propio (una captura, un truco que hayas probado) y cambias a `draft: false`. 10 minutos por artículo marcan la diferencia en la aprobación y en el posicionamiento.
- **Google Search Console** (gratis): añade tu dominio, verifica (pega el código en `search_console_verification`) y envía `https://tudominio.com/sitemap.xml`.
- **Bing Webmaster Tools**: importa desde Search Console en 1 clic.
- Comparte cada artículo en Pinterest, grupos de Facebook, Reddit en español o un canal de WhatsApp/Telegram propio. Nada de comprar tráfico ni bots: AdSense lo detecta y cierra la cuenta.

## Fase 2 · Solicitar Google AdSense (cuando tengas ~25 artículos)

1. Entra en <https://adsense.google.com> con tu cuenta de Google y pulsa **Empezar**.
2. Escribe tu dominio y tus datos reales de pago (nombre, dirección). Tienes que ser mayor de 18 años.
3. AdSense te dará tu ID de editor, con formato `ca-pub-1234567890123456`.
4. Pégalo en `config.json` → `"adsense": {"client_id": "ca-pub-..."}` y haz push.
   - El generador añade automáticamente el script en el `<head>`, la meta de verificación y el archivo `/ads.txt`.
5. En AdSense: **Sitios › tu dominio › Solicitar revisión**. Tarda de unos días a 2-4 semanas. **Sigue publicando mientras esperas.**

### Si te rechazan
Lo más habitual es «contenido de poco valor». Solución: revisa y amplía artículos, elimina los flojos, espera ~2 semanas y vuelve a solicitarlo. Revisa también Search Console por errores.

## Fase 3 · Activar consentimiento de cookies (obligatorio en Europa)

Desde enero de 2024, Google exige una **plataforma de gestión de consentimiento (CMP) certificada** para mostrar anuncios personalizados en el EEE, Reino Unido y Suiza. Sin ella solo verás anuncios limitados o no personalizados y ganarás bastante menos.

La opción más sencilla y gratuita es la de Google:

1. AdSense › **Privacidad y mensajes › Mensajes del RGPD/Europa › Crear**.
2. Elige tu sitio, idioma español, marca «Gestionar opciones» y «No consentir».
3. Enlaza tu política de privacidad: `https://tudominio.com/politica-de-privacidad/`.
4. **Publicar.** No hace falta tocar código: se carga con el script de AdSense que ya tiene el blog.

## Fase 4 · Colocar anuncios (tras la aprobación)

Tienes dos opciones (puedes combinarlas):

**A) Anuncios automáticos** (más fácil): AdSense › Anuncios › tu sitio › activar. Google decide dónde colocarlos.

**B) Bloques manuales** (más control, ya preparados en el diseño):

| Hueco en el blog | Tipo de bloque en AdSense | Clave en config.json |
|---|---|---|
| Debajo del menú | Display adaptable | `slot_top` |
| Dentro del artículo (tras el 3.er párrafo y a mitad) | In-article | `slot_in_article` |
| Barra lateral fija (escritorio) | Display adaptable vertical | `slot_sidebar` |
| Final del artículo | Display adaptable | `slot_bottom` |

Crea cada bloque en **Anuncios › Por bloque de anuncios**, copia el número `data-ad-slot` y pégalo en su clave. Los recuadros grises «Espacio para anuncio» desaparecen solos en cuanto pones tu `client_id`.

Consejo: empieza con anuncios automáticos + in-article. No satures: demasiados anuncios espantan a los lectores y a Google.

## Fase 5 · Cobrar

- Google paga **mensualmente** cuando superas el umbral de pago (en España, 70 €).
- Al llegar a 10 € te enviarán un **PIN por correo postal** para verificar tu dirección.
- Añade tu IBAN en **Pagos › Formas de pago** y completa la **información fiscal** (formulario W-8BEN para no residentes en EE. UU.).
- 🧾 En España, los ingresos por AdSense hay que declararlos en el IRPF; si son recurrentes puede ser necesario darse de alta como autónomo. Consulta con un gestor: no soy asesor fiscal y depende de tu caso (en Andorra el régimen es distinto).

## Fuentes de ingreso adicionales

1. **Amazon Afiliados** (ya integrado): date de alta en <https://afiliados.amazon.es>, pega tu ID en `amazon_affiliate_tag`. En los artículos se usa `[[amazon:búsqueda|Texto del botón]]` y el generador crea el enlace con tu ID. Comisión por compras de 1 % a 10 % según categoría. Recuerda: Amazon exige hacer al menos 3 ventas en los primeros 180 días.
2. **Otros afiliados de tecnología**: VPNs, gestores de contraseñas, hosting y software suelen pagar comisiones altas (Awin, Impact, programas propios).
3. **Cuando superes ~10.000-50.000 visitas/mes**: redes premium como Ezoic, Mediavine o Raptive suelen pagar bastante más que AdSense.
4. **Newsletter**: con una lista de correo puedes vender patrocinios.

## Cuánto se puede ganar (expectativas realistas)

En español, un blog de tecnología con AdSense suele generar del orden de **1-5 € por cada 1.000 visitas** (RPM), con mucha variación por país del visitante, tema y época del año. Orientativo:

| Visitas/mes | Ingresos AdSense aprox. |
|---|---|
| 5.000 | 5-25 € |
| 50.000 | 50-250 € |
| 300.000 | 300-1.500 € |

El tráfico orgánico de Google suele tardar **3-9 meses** en despegar en un dominio nuevo. La constancia (publicar a diario y actualizar lo que ya funciona) es lo que hace crecer el blog.

## Checklist rápida

- [ ] Dominio propio comprado y conectado
- [ ] `config.json` con dominio, email y nombre legal
- [ ] `ANTHROPIC_API_KEY` en los secretos de GitHub
- [ ] Search Console verificado + sitemap enviado
- [ ] 25+ artículos revisados
- [ ] AdSense solicitado y `client_id` en config
- [ ] Mensaje de consentimiento RGPD publicado en AdSense
- [ ] Bloques de anuncios creados (o auto ads activados)
- [ ] Amazon Afiliados con tu tag
- [ ] IBAN, PIN y datos fiscales en AdSense
