"""
Gera portfolio/index.html a partir de portfolio/clients.json.

Usa o mesmo design system do site (estilos extraídos de _template.html via
blogsystem.py), então a página fica idêntica à home e ao blog.

Uso (a partir da raiz do repositório):
    python3 portfolio/build.py

clients.json: lista de objetos {slug, name, cat, fit}
  - slug: nome do arquivo em assets/portfolio/<slug>.jpg
  - name: nome exibido no cartão (pode ficar vazio)
  - cat: chave da categoria (ver CATEGORIES)
  - fit: "cover" (foto/mockup) ou "contain" (logo/prancha em fundo liso)
"""
import html
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT_DIR = os.path.join(ROOT, "portfolio")

spec = importlib.util.spec_from_file_location("blogsystem", os.path.join(ROOT, "blog", "blogsystem.py"))
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)

CATEGORIES = [
    ("saude", "Saúde e bem-estar"),
    ("juridico", "Jurídico, contábil e financeiro"),
    ("negocios", "Negócios, consultoria e tecnologia"),
    ("varejo", "Varejo, gastronomia e serviços"),
    ("pessoal", "Marcas pessoais e projetos"),
]
CAT_LABEL = dict(CATEGORIES)

PORTFOLIO_CSS = """
  /* ===== Portfólio ===== */
  .pf-hero{padding-block:clamp(64px,9vw,100px) clamp(28px,4vw,44px);}
  .pf-hero h1{font-size:clamp(2.2rem,4.6vw,3.5rem); font-weight:500; margin-top:20px; line-height:1.12; max-width:20ch;}
  .pf-hero p{margin-top:18px; color:var(--text-soft); font-size:1.08rem; max-width:58ch;}
  .pf-count{margin-top:26px; display:flex; gap:28px; flex-wrap:wrap;}
  .pf-count b{display:block; font-family:'Manrope',sans-serif; font-weight:800; font-size:clamp(1.6rem,3vw,2.2rem); color:var(--accent-ink); line-height:1;}
  .pf-count span{display:block; margin-top:6px; font-size:.82rem; color:var(--text-soft); font-weight:600;}

  .pf-filters{display:flex; flex-wrap:wrap; gap:10px; margin-top:34px; padding-bottom:30px; border-bottom:1px solid var(--line);}
  .pf-chip{
    font-family:'Manrope',sans-serif; font-weight:700; font-size:.84rem; letter-spacing:.01em;
    color:var(--text-soft); background:transparent; border:1px solid var(--line);
    padding:9px 16px; border-radius:999px; cursor:pointer; transition:all .2s ease;
  }
  .pf-chip:hover{border-color:var(--gold); color:var(--accent-ink);}
  .pf-chip[aria-pressed="true"]{background:var(--btn-bg); color:var(--btn-text); border-color:var(--btn-bg);}

  .pf-group{margin-top:clamp(38px,5vw,60px);}
  .pf-group h2{font-size:clamp(1.3rem,2.4vw,1.7rem); font-weight:500; display:flex; align-items:baseline; gap:12px;}
  .pf-group h2 small{font-family:'Manrope',sans-serif; font-size:.78rem; font-weight:700; color:var(--text-soft); letter-spacing:.06em;}
  .pf-grid{margin-top:22px; display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:20px;}
  .pf-card{
    margin:0; background:var(--surface); border:1px solid var(--line); border-radius:12px; overflow:hidden;
    cursor:zoom-in; padding:0; text-align:left; font:inherit; color:inherit;
    transition:transform .3s ease, box-shadow .3s ease, border-color .3s ease;
  }
  .pf-card:hover{transform:translateY(-4px); box-shadow:var(--shadow); border-color:var(--gold);}
  .pf-card:focus-visible{outline:2px solid var(--gold); outline-offset:3px;}
  .pf-media{aspect-ratio:4/3; background:#F5EFE2; display:flex; align-items:center; justify-content:center; overflow:hidden;}
  .pf-media img{width:100%; height:100%; display:block;}
  .pf-media img.cover{object-fit:cover;}
  .pf-media img.contain{object-fit:contain;}
  .pf-cap{padding:14px 16px 16px; font-size:.92rem; font-weight:700; line-height:1.35; min-height:3.1em;}
  .pf-cap small{display:block; margin-top:2px; font-weight:600; font-size:.76rem; color:var(--text-soft);}

  .pf-dialog{border:none; padding:0; background:transparent; max-width:min(96vw,1000px); width:100%;}
  .pf-dialog::backdrop{background:rgba(8,20,14,.82);}
  .pf-dialog figure{margin:0; background:#F5EFE2; border-radius:12px; overflow:hidden; position:relative;}
  .pf-dialog img{display:block; width:100%; max-height:80vh; object-fit:contain; background:#F5EFE2;}
  .pf-dialog figcaption{padding:14px 18px; background:var(--surface); color:var(--text); font-weight:700;}
  .pf-close{
    position:absolute; top:10px; right:10px; width:40px; height:40px; border-radius:50%; border:none; cursor:pointer;
    background:rgba(14,42,31,.85); color:#EFE9DA; font-size:1.3rem; line-height:1;
  }

  .pf-cta{
    margin-top:clamp(56px,8vw,96px); padding:clamp(28px,5vw,48px); border-radius:16px;
    background:var(--surface-2); border:1px solid var(--line);
    display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:22px 32px;
  }
  .pf-cta h2{font-size:clamp(1.5rem,2.8vw,2.1rem); font-weight:500; max-width:24ch; line-height:1.2;}
  @media (max-width:560px){
    .pf-grid{grid-template-columns:repeat(2,1fr); gap:14px;}
    .pf-cap{padding:10px 12px 12px; font-size:.82rem;}
    .pf-cta .btn{width:100%; justify-content:center; white-space:normal;}
  }
"""

SCRIPT = """
<script>
(function(){
  var chips = document.querySelectorAll('.pf-chip');
  var groups = document.querySelectorAll('.pf-group');
  chips.forEach(function(c){
    c.addEventListener('click', function(){
      var k = c.getAttribute('data-cat');
      chips.forEach(function(x){ x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
      groups.forEach(function(g){ g.hidden = !(k === 'todos' || g.getAttribute('data-cat') === k); });
    });
  });
  var dlg = document.getElementById('pf-dialog');
  var img = dlg.querySelector('img'), cap = dlg.querySelector('figcaption');
  document.querySelectorAll('.pf-card').forEach(function(card){
    card.addEventListener('click', function(){
      var im = card.querySelector('img');
      img.src = im.currentSrc || im.src; img.alt = im.alt;
      cap.textContent = card.getAttribute('data-name') || '';
      cap.hidden = !cap.textContent;
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open','');
    });
  });
  dlg.addEventListener('click', function(e){ if (e.target === dlg) dlg.close(); });
  dlg.querySelector('.pf-close').addEventListener('click', function(){ dlg.close(); });
})();
</script>
"""


def build():
    with open(os.path.join(PORT_DIR, "clients.json"), encoding="utf-8") as f:
        clients = json.load(f)

    present = []
    for c in clients:
        if os.path.exists(os.path.join(ROOT, "assets", "portfolio", c["slug"] + ".jpg")):
            present.append(c)
    total = len(present)

    chips = ['<button class="pf-chip" type="button" data-cat="todos" aria-pressed="true">Todos</button>']
    groups = []
    for key, label in CATEGORIES:
        items = [c for c in present if c["cat"] == key]
        if not items:
            continue
        chips.append(f'<button class="pf-chip" type="button" data-cat="{key}" aria-pressed="false">{html.escape(label)}</button>')
        cards = []
        for c in items:
            name = c.get("name", "").strip()
            alt = name or "Identidade visual"
            fit = "contain" if c.get("fit") == "contain" else "cover"
            cap = f"<div class=\"pf-cap\">{html.escape(name)}</div>" if name else "<div class=\"pf-cap\"><small>Identidade visual</small></div>"
            cards.append(
                f'<button class="pf-card" type="button" data-name="{html.escape(name, quote=True)}">'
                f'<div class="pf-media"><img class="{fit}" src="/assets/portfolio/{c["slug"]}.jpg" '
                f'alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async"></div>{cap}</button>'
            )
        groups.append(
            f'<section class="pf-group" data-cat="{key}"><h2>{html.escape(label)} <small>{len(items)}</small></h2>'
            f'<div class="pf-grid">{"".join(cards)}</div></section>'
        )

    style = bs.extract_shared_style() + bs.BLOG_EXTRA_CSS + PORTFOLIO_CSS
    page_url = "https://rafaelaornellas.com.br/portfolio/"
    title = "Portfólio de identidades visuais e branding"
    desc = (f"Mais de {total} marcas que ganharam identidade, posicionamento e presença com a "
            "Rafaela Ornellas: logotipos, identidades visuais e aplicações.")
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "CollectionPage", "name": title,
        "url": page_url, "inLanguage": "pt-BR", "description": desc,
        "author": {"@type": "Person", "name": "Rafaela Ornellas", "url": "https://rafaelaornellas.com.br/"},
    }, ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfólio | Rafaela Ornellas, Branding Estratégico</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="icon" href="/assets/logo.png" type="image/png">
<link rel="canonical" href="{page_url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rafaela Ornellas, Branding Estratégico">
<meta property="og:title" content="Portfólio | Rafaela Ornellas">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:image" content="https://rafaelaornellas.com.br/assets/og-image.jpg">
<meta property="og:url" content="{page_url}">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<style>
{style}
</style>
</head>
<body>

{bs.header_html(depth=0)}

<main id="top">
  <section class="pf-hero">
    <div class="wrap">
      <div class="eyebrow">Portfólio</div>
      <h1>Marcas que ganharam identidade e posicionamento</h1>
      <p>Uma seleção de identidades visuais criadas ao longo de 25 anos de Comunicação e Branding. Cada marca nasce de um diagnóstico e termina em símbolos, cores e formas com significado.</p>
      <div class="pf-count">
        <div><b>+{total}</b><span>marcas e identidades visuais</span></div>
        <div><b>25 anos</b><span>de experiência em branding</span></div>
      </div>
      <div class="pf-filters" role="group" aria-label="Filtrar por segmento">
        {"".join(chips)}
      </div>
    </div>
  </section>

  <section class="section" style="padding-top:0;">
    <div class="wrap">
      {"".join(groups)}
      <div class="pf-cta">
        <h2>Quer ver a sua marca aqui?</h2>
        <a class="btn btn-onbrand" href="{{{{WA_LINK_DEFAULT}}}}" target="_blank" rel="noopener">
          {{{{ICON_WHATSAPP}}}}
          Falar com a Rafaela
        </a>
      </div>
    </div>
  </section>
</main>

<dialog class="pf-dialog" id="pf-dialog" aria-label="Imagem ampliada">
  <figure>
    <button class="pf-close" type="button" aria-label="Fechar">&times;</button>
    <img alt="" src="">
    <figcaption hidden></figcaption>
  </figure>
</dialog>

{bs.footer_html(depth=0)}
{SCRIPT}
</body>
</html>
"""
    page = bs.apply_common_tokens(page)
    out = os.path.join(PORT_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Portfólio gerado: {total} marcas em {len(groups)} segmentos -> {out}")


if __name__ == "__main__":
    build()
