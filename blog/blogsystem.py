"""
Blog build system for Rafaela Ornellas' site.

Shares the exact design tokens/CSS from the main landing page template so
every blog post looks like part of the same site. Maintains posts.json as
the source of truth; index.html and each post page are regenerated from it.

Usage (from repo root, i.e. the folder containing index.html and blog/):
    python3 blog/blogsystem.py add \
        --title "..." --pillar Educar --excerpt "..." \
        --content-file /path/to/post_body.html --date 2026-08-12

    python3 blog/blogsystem.py rebuild
"""
import base64
import json
import os
import re
import sys
import argparse
import unicodedata
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
MANIFEST_PATH = os.path.join(BLOG_DIR, "posts.json")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

PILLAR_LABELS = {
    "Educar": "Educar",
    "Inspirar": "Inspirar",
    "Vender": "Vender",
    "Entreter": "Entreter",
}


def slugify(title: str) -> str:
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_str).strip("-").lower()
    return slug[:80]


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(posts):
    os.makedirs(BLOG_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def b64_asset(name):
    path = os.path.join(ASSETS_DIR, name)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def extract_shared_style():
    """Pull the <style>...</style> block from the main template so blog pages
    stay pixel-identical to the landing page's design system."""
    template_path = os.path.join(REPO_ROOT, "_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    style = m.group(1)
    fraunces_normal = b64_asset("fraunces-normal.woff2")
    fraunces_italic = b64_asset("fraunces-italic.woff2")
    manrope = b64_asset("manrope.woff2")
    style = style.replace("{{FRAUNCES_NORMAL}}", fraunces_normal)
    style = style.replace("{{FRAUNCES_ITALIC}}", fraunces_italic)
    style = style.replace("{{MANROPE}}", manrope)
    return style


BLOG_EXTRA_CSS = """
  /* ===== Blog additions ===== */
  .blog-hero{padding-block:clamp(64px,9vw,100px) clamp(40px,6vw,64px);}
  .blog-hero h1{font-size:clamp(2.2rem,4.4vw,3.4rem); font-weight:500; margin-top:20px; line-height:1.12;}
  .blog-hero p{margin-top:18px; color:var(--text-soft); font-size:1.08rem; max-width:56ch;}

  .post-grid{margin-top:20px; display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:28px;}
  .post-card{
    background:var(--surface); border:1px solid var(--line); border-radius:12px; overflow:hidden;
    display:flex; flex-direction:column; text-decoration:none; color:var(--text);
    transition:transform .3s ease, box-shadow .3s ease, border-color .3s ease;
  }
  .post-card:hover{transform:translateY(-4px); box-shadow:var(--shadow); border-color:var(--gold);}
  .post-card-body{padding:26px 26px 30px; display:flex; flex-direction:column; gap:12px; flex:1;}
  .post-pillar{
    align-self:flex-start; font-size:.7rem; font-weight:800; letter-spacing:.09em; text-transform:uppercase;
    color:var(--accent-ink); background:color-mix(in srgb, var(--gold) 14%, transparent);
    padding:5px 12px; border-radius:999px;
  }
  .post-card h3{font-size:1.28rem; font-weight:600; line-height:1.28;}
  .post-card p{color:var(--text-soft); font-size:.94rem; line-height:1.6;}
  .post-date{margin-top:auto; padding-top:6px; font-size:.78rem; color:var(--text-soft); font-weight:600; letter-spacing:.03em;}

  .post-article{padding-block:clamp(56px,8vw,88px) clamp(64px,9vw,100px);}
  .post-article .wrap{max-width:740px;}
  .post-article-head .post-pillar{margin-bottom:18px;}
  .post-article-head h1{font-size:clamp(2rem,4vw,2.9rem); font-weight:500; line-height:1.16;}
  .post-article-meta{margin-top:16px; font-size:.86rem; color:var(--text-soft); font-weight:600;}
  .post-prose{margin-top:42px; font-size:1.12rem; line-height:1.85; color:var(--text);}
  .post-prose p{margin-top:22px;}
  .post-prose p:first-child{margin-top:0;}
  .post-prose h2{margin-top:44px; font-size:1.5rem; font-weight:600; line-height:1.3;}
  .post-prose h3{margin-top:34px; font-size:1.2rem; font-weight:600;}
  .post-prose ul, .post-prose ol{margin-top:20px; padding-left:1.3em; display:flex; flex-direction:column; gap:10px;}
  .post-prose blockquote{
    margin-top:28px; padding-left:22px; border-left:2px solid var(--gold);
    font-family:'Fraunces',serif; font-style:italic; font-weight:500; font-size:1.2rem; color:var(--accent-ink);
  }
  .post-cta{
    margin-top:56px; padding:32px; border-radius:12px; background:var(--surface-2); border:1px solid var(--line);
    display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:20px;
  }
  .post-cta p{font-family:'Fraunces',serif; font-size:1.15rem; font-weight:500; max-width:34ch;}
  .post-back{
    display:inline-flex; align-items:center; gap:8px; margin-top:36px; font-size:.9rem; font-weight:700;
    color:var(--accent-ink); text-decoration:none;
  }
"""


def header_html(depth=0):
    prefix = "../" * depth
    home = prefix if prefix else "./"
    return f"""<header id="site-header">
  <div class="header-inner">
    <a class="brandmark" href="{home}#top">
      <img src="data:image/png;base64,{{{{LOGO}}}}" alt="">
      <span class="wordmark">Rafaela Ornellas<small>Branding Estratégico</small></span>
    </a>
    <nav class="header-nav"><a href="{prefix}blog/">Blog</a></nav>
    <div class="header-cta">
      <span class="header-phone">(32) 99974-2205</span>
      <a class="btn btn-primary" href="{{{{WA_LINK_DEFAULT}}}}" target="_blank" rel="noopener">
        {{{{ICON_WHATSAPP}}}}
        Falar no WhatsApp
      </a>
    </div>
  </div>
</header>"""


def footer_html(depth=0):
    prefix = "../" * depth
    home = prefix if prefix else "./"
    return f"""<footer>
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="data:image/png;base64,{{{{LOGO}}}}" alt="">
        <span class="wordmark">Rafaela Ornellas<small>Branding Estratégico · Marcas e Eventos</small></span>
      </div>
      <div class="footer-links">
        <div class="footer-col">
          <h5>Contato</h5>
          <a href="{{{{WA_LINK_DEFAULT}}}}" target="_blank" rel="noopener">WhatsApp (32) 99974-2205</a>
          <a href="https://www.instagram.com/rafaelaornellas" target="_blank" rel="noopener">@rafaelaornellas</a>
        </div>
        <div class="footer-col">
          <h5>Formação</h5>
          <span>Comunicação · PUC Minas</span>
          <span>MBA Design Estratégico · ESPM Rio</span>
        </div>
        <div class="footer-col">
          <h5>Navegação</h5>
          <a href="{home}#sobre">Sobre</a>
          <a href="{home}#processo">Processo</a>
          <a href="{prefix}blog/">Blog</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year"></span> Rafaela Ornellas. Todos os direitos reservados.</span>
      <span>25 anos de experiência em Comunicação e Branding</span>
    </div>
  </div>
</footer>

<a class="float-wa" href="{{{{WA_LINK_DEFAULT}}}}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">
  {{{{ICON_WHATSAPP_WHITE}}}}
</a>

<script>
  document.getElementById('year').textContent = new Date().getFullYear();
  var header = document.getElementById('site-header');
  window.addEventListener('scroll', function(){{
    header.classList.toggle('scrolled', window.scrollY > 8);
  }}, {{passive:true}});
  var els = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){{
    var io = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{ if(e.isIntersecting){{ e.target.classList.add('in-view'); io.unobserve(e.target); }} }});
    }}, {{threshold:.12, rootMargin:'0px 0px -8% 0px'}});
    els.forEach(function(el){{ io.observe(el); }});
  }} else {{
    els.forEach(function(el){{ el.classList.add('in-view'); }});
  }}
</script>"""


def apply_common_tokens(html):
    import urllib.parse
    phone = "5532999742205"
    msg_default = "Olá Rafaela! Vim pelo blog e quero saber mais sobre o Branding Estratégico."
    wa_link = f"https://wa.me/{phone}?text=" + urllib.parse.quote(msg_default)
    icon_whatsapp = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.14c-.24.68-1.4 1.32-1.93 1.4-.49.08-1.11.11-1.79-.11-.41-.13-.95-.31-1.63-.6-2.87-1.24-4.74-4.14-4.89-4.33-.14-.19-1.17-1.56-1.17-2.98s.74-2.11 1-2.4c.26-.29.57-.36.76-.36h.55c.18 0 .42-.03.65.5.24.55.81 1.9.88 2.04.07.14.12.31.02.5-.09.19-.14.3-.28.46-.14.16-.29.36-.42.48-.14.13-.28.28-.12.55.16.28.72 1.19 1.55 1.93 1.06.95 1.96 1.24 2.24 1.38.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.28.36-.23.6-.14.24.1 1.55.73 1.82.86.27.13.44.19.51.3.07.11.07.63-.17 1.24z"/></svg>'
    icon_whatsapp_white = icon_whatsapp.replace('width="18" height="18"', 'width="28" height="28"')
    logo_b64 = b64_asset("logo.png")
    html = html.replace("{{WA_LINK_DEFAULT}}", wa_link)
    html = html.replace("{{ICON_WHATSAPP}}", icon_whatsapp)
    html = html.replace("{{ICON_WHATSAPP_WHITE}}", icon_whatsapp_white)
    html = html.replace("{{LOGO}}", logo_b64)
    return html


def render_post_page(post, content_html):
    style = extract_shared_style() + BLOG_EXTRA_CSS
    date_fmt = post["date"]
    page_url = f"https://rafaelaornellas.com.br/blog/posts/{post['slug']}.html"
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{post['title']} — Blog Rafaela Ornellas</title>
<meta name="description" content="{post['excerpt']}">
<link rel="icon" href="/assets/logo.png" type="image/png">
<link rel="canonical" href="{page_url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Rafaela Ornellas — Branding Estratégico">
<meta property="og:title" content="{post['title']}">
<meta property="og:description" content="{post['excerpt']}">
<meta property="og:image" content="https://rafaelaornellas.com.br/assets/og-image.jpg">
<meta property="og:url" content="{page_url}">
<meta property="og:locale" content="pt_BR">
<meta property="article:published_time" content="{post['date']}">
<meta property="article:author" content="Rafaela Ornellas">
<meta property="article:section" content="{post['pillar']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{post['title']}">
<meta name="twitter:description" content="{post['excerpt']}">
<meta name="twitter:image" content="https://rafaelaornellas.com.br/assets/og-image.jpg">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{post['title']}",
  "description": "{post['excerpt']}",
  "datePublished": "{post['date']}",
  "dateModified": "{post['date']}",
  "url": "{page_url}",
  "image": "https://rafaelaornellas.com.br/assets/og-image.jpg",
  "inLanguage": "pt-BR",
  "author": {{
    "@type": "Person",
    "name": "Rafaela Ornellas",
    "url": "https://rafaelaornellas.com.br/"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Rafaela Ornellas — Branding Estratégico",
    "url": "https://rafaelaornellas.com.br/"
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{page_url}"
  }}
}}
</script>
<style>
{style}
</style>
</head>
<body>

{header_html(depth=1)}

<main id="top">
  <section class="post-article">
    <div class="wrap">
      <a class="post-back" href="../">← Voltar para o blog</a>
      <div class="post-article-head reveal in-view" style="margin-top:22px;">
        <span class="post-pillar">{post['pillar']}</span>
        <h1>{post['title']}</h1>
        <div class="post-article-meta">{date_fmt} · Rafaela Ornellas</div>
      </div>
      <div class="post-prose reveal in-view">
{content_html}
      </div>
      <div class="post-cta reveal in-view">
        <p>Quer aplicar isso na sua marca?</p>
        <a class="btn btn-onbrand" href="{{{{WA_LINK_DEFAULT}}}}" target="_blank" rel="noopener">
          {{{{ICON_WHATSAPP}}}}
          Falar com a Rafaela
        </a>
      </div>
    </div>
  </section>
</main>

{footer_html(depth=1)}
</body>
</html>
"""
    return apply_common_tokens(html)


def render_index_page(posts):
    style = extract_shared_style() + BLOG_EXTRA_CSS
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    cards = []
    for p in posts_sorted:
        cards.append(f"""        <a class="post-card reveal in-view" href="posts/{p['slug']}.html">
          <div class="post-card-body">
            <span class="post-pillar">{p['pillar']}</span>
            <h3>{p['title']}</h3>
            <p>{p['excerpt']}</p>
            <span class="post-date">{p['date']}</span>
          </div>
        </a>""")
    cards_html = "\n".join(cards) if cards else '        <p style="color:var(--text-soft);">Em breve, novas matérias por aqui.</p>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog — Rafaela Ornellas | Branding Estratégico</title>
<meta name="description" content="Artigos sobre branding, posicionamento e estratégia de marca, publicados pela Rafaela Ornellas.">
<link rel="icon" href="/assets/logo.png" type="image/png">
<link rel="canonical" href="https://rafaelaornellas.com.br/blog/">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rafaela Ornellas — Branding Estratégico">
<meta property="og:title" content="Blog — Rafaela Ornellas | Branding Estratégico">
<meta property="og:description" content="Artigos sobre branding, posicionamento e estratégia de marca, publicados pela Rafaela Ornellas.">
<meta property="og:image" content="https://rafaelaornellas.com.br/assets/og-image.jpg">
<meta property="og:url" content="https://rafaelaornellas.com.br/blog/">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Blog — Rafaela Ornellas | Branding Estratégico">
<meta name="twitter:description" content="Artigos sobre branding, posicionamento e estratégia de marca.">
<meta name="twitter:image" content="https://rafaelaornellas.com.br/assets/og-image.jpg">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Blog",
  "name": "Blog — Rafaela Ornellas",
  "url": "https://rafaelaornellas.com.br/blog/",
  "inLanguage": "pt-BR",
  "publisher": {{
    "@type": "Organization",
    "name": "Rafaela Ornellas — Branding Estratégico",
    "url": "https://rafaelaornellas.com.br/"
  }}
}}
</script>
<style>
{style}
</style>
</head>
<body>

{header_html(depth=0)}

<main id="top">
  <section class="blog-hero">
    <div class="wrap">
      <div class="eyebrow reveal in-view">Blog</div>
      <h1 class="reveal in-view">Ideias sobre branding, marca e autoridade</h1>
      <p class="reveal in-view">Artigos curtos sobre estratégia de marca, posicionamento e identidade visual, publicados regularmente.</p>
    </div>
  </section>
  <section class="section" style="padding-top:0;">
    <div class="wrap">
      <div class="post-grid">
{cards_html}
      </div>
    </div>
  </section>
</main>

{footer_html(depth=0)}
</body>
</html>
"""
    return apply_common_tokens(html)


def write_sitemap(posts):
    base = "https://rafaelaornellas.com.br"
    urls = [
        (f"{base}/", "1.0"),
        (f"{base}/blog/", "0.9"),
    ]
    for p in sorted(posts, key=lambda p: p["date"], reverse=True):
        urls.append((f"{base}/blog/posts/{p['slug']}.html", "0.7"))

    entries = "\n".join(
        f"""  <url>
    <loc>{url}</loc>
    <priority>{priority}</priority>
  </url>"""
        for url, priority in urls
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    with open(os.path.join(REPO_ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_robots():
    content = """User-agent: *
Allow: /

Sitemap: https://rafaelaornellas.com.br/sitemap.xml
"""
    with open(os.path.join(REPO_ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(content)


def rebuild(posts=None):
    if posts is None:
        posts = load_manifest()
    os.makedirs(POSTS_DIR, exist_ok=True)
    index_html = render_index_page(posts)
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    for p in posts:
        content_path = os.path.join(POSTS_DIR, p["slug"] + ".content.html")
        if not os.path.exists(content_path):
            continue
        with open(content_path, "r", encoding="utf-8") as f:
            content_html = f.read()
        post_html = render_post_page(p, content_html)
        with open(os.path.join(POSTS_DIR, p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(post_html)
    write_sitemap(posts)
    write_robots()
    print(f"Rebuilt index + {len(posts)} post(s). Sitemap and robots.txt updated.")


def add_post(title, pillar, excerpt, content_html, post_date=None):
    assert pillar in PILLAR_LABELS, f"pillar must be one of {list(PILLAR_LABELS)}"
    post_date = post_date or date.today().isoformat()
    slug = slugify(title)
    posts = load_manifest()
    if any(p["slug"] == slug for p in posts):
        slug = f"{slug}-{post_date}"
    post = {"title": title, "pillar": pillar, "excerpt": excerpt, "date": post_date, "slug": slug}
    posts.append(post)
    save_manifest(posts)
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(os.path.join(POSTS_DIR, slug + ".content.html"), "w", encoding="utf-8") as f:
        f.write(content_html)
    rebuild(posts)
    print(f"Added post: {slug}")
    return slug


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--pillar", required=True)
    p_add.add_argument("--excerpt", required=True)
    p_add.add_argument("--content-file", required=True)
    p_add.add_argument("--date", default=None)

    sub.add_parser("rebuild")

    args = parser.parse_args()
    if args.cmd == "add":
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()
        add_post(args.title, args.pillar, args.excerpt, content, args.date)
    elif args.cmd == "rebuild":
        rebuild()
    else:
        parser.print_help()
