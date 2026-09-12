from pathlib import Path
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE_FILE = ROOT / "data" / "site.json"
LOCATIONS_FILE = ROOT / "data" / "locations.json"
FAQ_FILE = ROOT / "data" / "faq.json"
ASSETS = ROOT / "assets"

site = json.loads(SITE_FILE.read_text(encoding="utf-8"))
locations = json.loads(LOCATIONS_FILE.read_text(encoding="utf-8"))
faqs = json.loads(FAQ_FILE.read_text(encoding="utf-8"))
region = locations["region"]
districts = locations["districts"]
services = site["services"]


def esc(value):
    return html.escape(str(value), quote=True)


def root_prefix(depth):
    return "../" * depth


def route_url(path=""):
    clean = path.strip("/")
    return "/" if not clean else "/" + clean + "/"


def canonical(path=""):
    return site["domain"].rstrip("/") + route_url(path)


def href(path, depth):
    return root_prefix(depth) + path.strip("/") + ("/" if path.strip("/") else "")


def icon_for(slug):
    return {
        "fayans-ustasi": "▦",
        "duvar-ustasi": "▤",
        "cati-ustasi": "⌂",
        "alci-ustasi": "◈",
        "boya-badana-ustasi": "◒",
    }.get(slug, "＋")


def tel_href(value):
    return "".join(ch for ch in str(value) if ch.isdigit() or ch == "+")


def whatsapp_href(value):
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if digits.startswith("0"):
        digits = "90" + digits[1:]
    return digits


def contact_block(depth):
    phone = site.get("phone", "").strip()
    whatsapp = site.get("whatsapp", "").strip()
    email = site.get("email", "").strip()
    items = []
    if phone:
        items.append(f'<a class="button orange" href="tel:{esc(tel_href(phone))}">Telefonla Ara</a>')
    if whatsapp:
        items.append(f'<a class="button secondary" href="https://wa.me/{esc(whatsapp_href(whatsapp))}" target="_blank" rel="noopener">WhatsApp</a>')
    if email:
        items.append(f'<a class="button secondary" href="mailto:{esc(email)}">E-posta Gönder</a>')
    if not items:
        items.append('<span class="button secondary">İletişim bilgileri hazırlanıyor</span>')
    return "".join(items)


def floating_contact(depth):
    phone = site.get("phone", "").strip()
    whatsapp = site.get("whatsapp", "").strip()
    items = []
    if whatsapp and whatsapp_href(whatsapp):
        items.append(f'<a class="floating-button floating-whatsapp" href="https://wa.me/{esc(whatsapp_href(whatsapp))}" target="_blank" rel="noopener" aria-label="WhatsApp ile iletişim">☏ <span>WhatsApp</span></a>')
    if phone and tel_href(phone):
        items.append(f'<a class="floating-button floating-phone" href="tel:{esc(tel_href(phone))}" aria-label="Telefonla ara">☎ <span>Ara</span></a>')
    return f'<div class="floating-contact" aria-label="Hızlı iletişim">{"".join(items)}</div>' if items else ""


def faq_items(limit=None):
    items = faqs if limit is None else faqs[:limit]
    return "".join(
        f'<details class="faq-item"><summary>{esc(item["question"])}</summary><div class="faq-answer"><p>{esc(item["answer"])}</p></div></details>'
        for item in items
    )


def faq_schema():
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in faqs
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")}</script>'


def page(title, description, content, path="", depth=0, extra_head=""):
    prefix = root_prefix(depth)
    robots = "index, follow" if site.get("indexable") else "noindex, nofollow"
    service_links = "".join(
        f'<a href="{href(s["slug"] + "/" + region["slug"], depth)}">{esc(s["name"])}</a>'
        for s in services
    )
    return f'''<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{esc(canonical(path))}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="tr_TR">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical(path))}">
  <link rel="stylesheet" href="{prefix}styles.css">
  {extra_head}
</head>
<body>
  <div class="site-top"><div class="container"><span><strong>{esc(region["name"])}</strong> ve ilçelerinde yapı dekorasyon hizmetleri</span><span>Pilot site altyapısı</span></div></div>
  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="{prefix}">
        <span class="brand-mark">YD</span>
        <span class="brand-copy"><strong>{esc(site["brand"])}</strong><span>Sağlam işçilik, temiz teslim.</span></span>
      </a>
      <button class="menu-button" data-menu-button aria-label="Menüyü aç" aria-expanded="false">☰</button>
      <nav class="nav-links" data-nav-links>
        <a href="{prefix}#hizmetler">Hizmetler</a>
        <a href="{href("sss", depth)}">SSS</a>
        <a href="{prefix}#bolgeler">Hizmet Bölgeleri</a>
        <a href="{prefix}#surec">Süreç</a>
        <a href="{prefix}#iletisim">İletişim</a>
      </nav>
    </div>
  </header>
  {content}
  <footer class="footer">
    <div class="container footer-inner">
      <span>© <span data-year></span> {esc(site["brand"])}</span>
      <span>Fayans · Duvar · Çatı · Alçı · Boya</span>
    </div>
  </footer>
  {floating_contact(depth)}
  <script src="{prefix}script.js" defer></script>
</body>
</html>'''


def service_cards(depth):
    return "".join(
        f'''<a class="card" href="{href(s["slug"] + "/" + region["slug"], depth)}">
          <span class="card-icon">{icon_for(s["slug"])}</span>
          <span><h3>{esc(s["name"])}</h3><p>{esc(s["short"])}</p></span>
          <span class="card-link">Hizmeti incele →</span>
        </a>'''
        for s in services
    )


def location_cards(depth, service_slug=None):
    return "".join(
        f'''<a class="location-link" href="{href((service_slug + "/" if service_slug else "") + region["slug"] + "/" + d["slug"], depth)}">
          <span>{esc(d["name"])}</span><span>↗</span>
        </a>'''
        for d in districts
    )


def build_home():
    cards = service_cards(0)
    locations_html = location_cards(0, services[0]["slug"])
    content = f'''
  <main>
    <section class="hero">
      <div class="container hero-grid">
        <div>
          <div class="eyebrow">Eskişehir yapı dekorasyon</div>
          <h1>Sağlam işçilik, <span>temiz teslim.</span></h1>
          <p class="lead">Eskişehir ve ilçelerinde fayans, duvar, çatı, alçı ve boya işleri için planlı, anlaşılır ve güven veren hizmet yaklaşımı.</p>
          <div class="actions">
            <a class="button primary" href="#hizmetler">Hizmetleri incele</a>
            <a class="button secondary" href="#iletisim">Teklif sürecini öğren</a>
          </div>
        </div>
        <div class="hero-card">
          <div class="blueprint"></div>
          <div class="hero-card-content">
            <div><span class="small-label">Yerel hizmet ağı</span><h2>Eskişehir’in ilçelerinde yapı işleri.</h2></div>
            <div class="hero-card-footer"><span>Keşif · planlama · uygulama</span><span class="hero-card-number">14</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="hizmetler">
      <div class="container">
        <div class="section-head"><div><div class="section-kicker">Hizmetlerimiz</div><h2>İhtiyaca göre, işin başından teslimine.</h2></div><p>Hizmet başlıklarını gerçek çalışma kapsamına göre güncelleyeceğiz. Her sayfa, ilgili hizmet ve bölge için ayrı bir başvuru noktası olacak.</p></div>
        <div class="cards">{cards}</div>
      </div>
    </section>

    <section class="section" id="surec">
      <div class="container split">
        <div><div class="section-kicker">Çalışma yaklaşımı</div><h2>Önce ne yapılacağını netleştirir, sonra işe başlarız.</h2><p class="lead">İyi bir yapı işi; doğru keşif, açık kapsam ve temiz uygulama ile başlar.</p></div>
        <div class="panel"><h3>Basit ve anlaşılır süreç</h3><p>İşin kapsamı, kullanılacak malzemeler ve uygulama planı baştan konuşulur.</p><ul class="check-list"><li>İhtiyacın ve alanın değerlendirilmesi</li><li>İş kapsamının ve malzemenin netleştirilmesi</li><li>Uygulama planının oluşturulması</li><li>Temiz ve kontrollü teslim</li></ul></div>
      </div>
    </section>

    <section class="section" id="bolgeler">
      <div class="container">
        <div class="section-head"><div><div class="section-kicker">Hizmet bölgeleri</div><h2>Eskişehir ve 14 ilçesi.</h2></div><p>İlçe sayfalarını gerçek hizmet kapsamına göre genişleteceğiz. Mahalle seviyesine geçmeden önce her bölgede hizmet verildiğini doğrulayacağız.</p></div>
        <div class="location-grid">{locations_html}</div>
      </div>
    </section>

    <section class="section faq-teaser" id="sss">
      <div class="container faq-teaser-grid">
        <div>
          <div class="section-kicker">Sıkça sorulanlar</div>
          <h2>İşe başlamadan önce merak edilenler.</h2>
          <p class="lead">Hizmet kapsamı, teklif süreci ve uygulama öncesi hazırlıklarla ilgili kısa cevapları bir araya getirdik.</p>
          <div class="actions"><a class="button primary" href="sss/">Tüm SSS sayfasını incele</a></div>
        </div>
        <div class="faq-preview">{faq_items(3)}</div>
      </div>
    </section>

    <section class="section" id="iletisim">
      <div class="container"><div class="cta"><div><div class="section-kicker">Teklif ve keşif</div><h2>Yapılacak işi birlikte netleştirelim.</h2><p>İletişim bilgileri ve gerçek proje detayları eklendiğinde bu alan doğrudan teklif talebine dönüşecek.</p></div><div class="actions">{contact_block(0)}</div></div></div>
    </section>
  </main>'''
    html_text = page(
        f'{site["brand"]} | Fayans, Duvar, Çatı, Alçı ve Boya',
        site["description"],
        content,
        "",
        0,
    )
    (DIST / "index.html").write_text(html_text, encoding="utf-8")


def build_service(service):
    slug = service["slug"]
    city_path = f'{slug}/{region["slug"]}'
    district_links = location_cards(2, slug)
    content = f'''
  <main>
    <div class="container breadcrumb"><a href="{href("", 2)}">Ana sayfa</a> / <a href="{href(city_path, 2)}">{esc(service["name"])}</a> / {esc(region["name"])}</div>
    <section class="page-hero"><div class="container"><div class="eyebrow">{esc(region["name"])} hizmet sayfası</div><h1>{esc(region["name"])} {esc(service["name"])}</h1><p class="lead">{esc(service["short"])} {esc(", ".join(service["aliases"]))} arayanlar için hizmet kapsamını ve çalışma sürecini inceleyin.</p></div></section>
    <section class="section"><div class="container service-layout"><article class="content-card"><h2>{esc(region["name"])} bölgesinde {esc(service["name"])} hizmeti</h2><p>Eskişehir’de {esc(service["name"].lower())} hizmeti arayanlar için önceliğimiz, yapılacak işi yerinde ve açık biçimde değerlendirmektir. Alanın durumu, uygulama kapsamı ve kullanılacak malzemeler netleştirilerek plan oluşturulur.</p><h3>Hizmet süreci</h3><ul class="check-list"><li>İhtiyacın ve uygulama alanının değerlendirilmesi</li><li>İş kapsamı ve malzeme seçeneklerinin açıklanması</li><li>Uygulama planının oluşturulması</li><li>Kontrollü ve temiz teslim</li></ul><h3>Eskişehir ilçelerinde hizmet</h3><p>Hizmet verilen ilçeler aşağıda listelenmiştir. İlçe ve mahalle sayfaları, gerçek çalışma alanı doğrulandıkça genişletilecektir.</p><div class="location-grid">{district_links}</div></article><aside class="info-box"><h3>Teklif almak ister misiniz?</h3><p>İşin türünü, yaklaşık alanı ve bulunduğunuz ilçeyi belirterek iletişim bilgileri eklendiğinde doğrudan ulaşabilirsiniz.</p><div class="actions">{contact_block(2)}</div><div class="mini-links">{service_links_for(service, 2)}</div></aside></div></section>
  </main>'''
    html_text = page(
        f'{region["name"]} {service["name"]} | {site["brand"]}',
        f'{region["name"]} ve ilçelerinde {service["name"].lower()} hizmeti. İş kapsamı, süreç ve hizmet bölgeleri.',
        content,
        city_path,
        2,
    )
    out = DIST / city_path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")


def service_links_for(current_service, depth):
    return "".join(
        f'<a href="{href(s["slug"] + "/" + region["slug"], depth)}">{esc(s["name"])} →</a>'
        for s in services
        if s["slug"] != current_service["slug"]
    )


def build_district(service, district):
    slug = service["slug"]
    district_path = f'{slug}/{region["slug"]}/{district["slug"]}'
    city_path = f'{slug}/{region["slug"]}'
    other_services = "".join(
        f'<a href="{href(s["slug"] + "/" + region["slug"] + "/" + district["slug"], 3)}">{esc(s["name"])} →</a>'
        for s in services
        if s["slug"] != service["slug"]
    )
    content = f'''
  <main>
    <div class="container breadcrumb"><a href="{href("", 3)}">Ana sayfa</a> / <a href="{href(city_path, 3)}">{esc(region["name"])} {esc(service["name"])}</a> / {esc(district["name"])}</div>
    <section class="page-hero"><div class="container"><div class="eyebrow">{esc(district["name"])} · {esc(region["name"])}</div><h1>{esc(district["name"])} {esc(service["name"])}</h1><p class="lead">{esc(district["name"])}, {esc(region["name"])} bölgesinde {esc(service["name"].lower())} hizmeti arayanlar için çalışma kapsamı, süreç ve iletişim bilgileri.</p></div></section>
    <section class="section"><div class="container service-layout"><article class="content-card"><h2>{esc(district["name"])} {esc(service["name"])} hizmeti</h2><p>{esc(district["name"])} ve çevresinde {esc(service["name"].lower())} ihtiyacınız varsa, işe başlamadan önce alanın durumunu ve yapılacak uygulamaları netleştirmek önemlidir. Fayansçı, duvarcı, çatı ustası, alçı ustası veya boya ustası ararken yalnızca fiyatı değil; iş kapsamını, malzemeyi ve teslim planını da birlikte değerlendirmek gerekir.</p><h3>Bu sayfada neleri netleştireceğiz?</h3><ul class="check-list"><li>Uygulama yapılacak alan ve yaklaşık ölçüler</li><li>İşin kapsamı ve tercih edilen malzeme</li><li>Başlangıç ve teslim planı</li><li>Keşif ve teklif süreci</li></ul><h3>Hizmet bölgesi</h3><p>Bu pilot sayfa {esc(district["name"])} için oluşturulmuştur. Mahalle seviyesinde sayfa üretimi, gerçek hizmet kapsamı ve proje bilgileri doğrulandıktan sonra yapılacaktır.</p></article><aside class="info-box"><h3>{esc(district["name"])} için teklif</h3><p>İşinizin türünü ve alanını anlatarak iletişim bilgileri eklendiğinde keşif sürecini başlatabilirsiniz.</p><div class="actions">{contact_block(3)}</div><div class="mini-links"><a href="{href(city_path, 3)}">Tüm Eskişehir sayfası →</a>{other_services}</div></aside></div></section>
  </main>'''
    html_text = page(
        f'{district["name"]} {service["name"]} | {site["brand"]}',
        f'{district["name"]}, {region["name"]} {service["name"].lower()} hizmeti. İş kapsamı ve teklif süreci.',
        content,
        district_path,
        3,
    )
    out = DIST / district_path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")


def build_faq():
    content = f'''
  <main>
    <div class="container breadcrumb"><a href="{href("", 0)}">Ana sayfa</a> / SSS</div>
    <section class="page-hero"><div class="container"><div class="eyebrow">Eskişehir yapı dekorasyon</div><h1>Sıkça Sorulan Sorular</h1><p class="lead">Fayans, duvar, çatı, alçı ve boya badana hizmetleriyle ilgili en çok merak edilenleri kısa ve anlaşılır cevaplarla derledik.</p></div></section>
    <section class="section"><div class="container faq-layout"><div class="faq-list">{faq_items()}</div><aside class="info-box"><h3>İşinizi konuşalım</h3><p>İşin türünü, bulunduğunuz ilçeyi ve yaklaşık alanı paylaşarak teklif sürecini başlatabilirsiniz.</p><div class="actions">{contact_block(0)}</div><div class="mini-links"><a href="{href("fayans-ustasi/" + region["slug"], 0)}">Fayans ustası sayfası →</a><a href="{href("boya-badana-ustasi/" + region["slug"], 0)}">Boya badana sayfası →</a></div></aside></div></section>
  </main>'''
    html_text = page(
        f'SSS | {site["brand"]}',
        f'{site["brand"]} hizmetleri hakkında sıkça sorulan sorular ve cevaplar.',
        content,
        "sss",
        0,
        faq_schema(),
    )
    out = DIST / "sss" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")


def build_robots():
    if site.get("indexable"):
        content = f'User-agent: *\nAllow: /\nSitemap: {site["domain"].rstrip("/")}/sitemap.xml\n'
    else:
        content = "User-agent: *\nDisallow: /\n"
    (DIST / "robots.txt").write_text(content, encoding="utf-8")


def build_sitemap():
    if not site.get("indexable"):
        (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', encoding="utf-8")
        return
    paths = ["", "sss"]
    for service in services:
        paths.append(f'{service["slug"]}/{region["slug"]}')
        paths.extend(f'{service["slug"]}/{region["slug"]}/{d["slug"]}' for d in districts)
    body = "\n".join(
        f'  <url><loc>{esc(canonical(path))}</loc></url>'
        for path in paths
    )
    content = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    (DIST / "sitemap.xml").write_text(content, encoding="utf-8")


def build_404():
    content = '''<main><section class="section"><div class="container"><div class="content-card"><div class="section-kicker">Sayfa bulunamadı</div><h1>Aradığınız sayfa burada değil.</h1><p class="lead">Ana sayfaya dönerek Eskişehir yapı dekorasyon hizmetlerini inceleyebilirsiniz.</p><div class="actions"><a class="button primary" href="__ROOT__">Ana sayfaya dön</a></div></div></div></section></main>'''
    (DIST / "404.html").write_text(
        page("Sayfa bulunamadı | " + site["brand"], "Aradığınız sayfa bulunamadı.", content.replace("__ROOT__", ""), "404", 0),
        encoding="utf-8",
    )


def main():
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSETS / "styles.css", DIST / "styles.css")
    shutil.copy2(ASSETS / "script.js", DIST / "script.js")
    if site.get("custom_domain"):
        (DIST / "CNAME").write_text(site["custom_domain"].strip() + "\n", encoding="utf-8")
    build_home()
    build_faq()
    for service in services:
        build_service(service)
        for district in districts:
            build_district(service, district)
    build_robots()
    build_sitemap()
    build_404()
    pages = sum(1 for _ in DIST.rglob("index.html"))
    print(f"Generated {pages} HTML pages for {region['name']}.")


if __name__ == "__main__":
    main()
