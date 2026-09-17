from datetime import date
from pathlib import Path
from urllib.parse import urlencode
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ASSETS = ROOT / "assets"


def load_data(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


site = load_data("site.json")
locations = load_data("locations.json")
faqs = load_data("faq.json")
service_content = load_data("service-content.json")
projects = load_data("projects.json")
region = locations["region"]
districts = locations["districts"]
services = site["services"]


def esc(value):
    return html.escape(str(value), quote=True)


def route_url(path=""):
    clean = path.strip("/")
    return "/" if not clean else "/" + clean + "/"


def canonical(path=""):
    return site["domain"].rstrip("/") + route_url(path)


def service_path(service, district=None):
    path = f'{service["slug"]}/{region["slug"]}'
    return path + f'/{district["slug"]}' if district else path


def asset_url(name):
    version = hashlib.sha256((ASSETS / name).read_bytes()).hexdigest()[:12]
    return f'/{name}?v={version}'


def icon_for(slug):
    return {"fayans-ustasi": "▦", "duvar-ustasi": "▤", "cati-ustasi": "⌂", "alci-ustasi": "◈", "karasiva-ustasi": "▧", "boya-badana-ustasi": "◒"}[slug]


def phone_digits(value):
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return "90" + digits[1:] if digits.startswith("0") else digits


def phone_display():
    number = site["phone"]
    return f'{number[:4]} {number[4:7]} {number[7:9]} {number[9:]}' if len(number) == 11 else number


def whatsapp_url(service=None, district=None, path=""):
    subject = service["name"] if service else "yapı dekorasyon işleri"
    place = district["name"] if district else region["name"]
    message = f'Merhaba, {place} için {subject.lower()} hakkında bilgi ve teklif almak istiyorum.\nSayfa: {canonical(path)}'
    return f'https://wa.me/{phone_digits(site["whatsapp"])}?' + urlencode({"text": message})


def contact_block(service=None, district=None, placement="content", path=""):
    return f'''<a class="button orange" href="tel:+{phone_digits(site['phone'])}" data-contact="phone" data-placement="{esc(placement)}">Telefonla ara</a>
<a class="button secondary" href="{esc(whatsapp_url(service, district, path))}" target="_blank" rel="noopener" data-contact="whatsapp" data-placement="{esc(placement)}">WhatsApp’tan yaz</a>'''


def floating_contact(service=None, district=None, path=""):
    return f'''<div class="floating-contact" aria-label="Hızlı iletişim">
<a class="floating-button floating-whatsapp" href="{esc(whatsapp_url(service, district, path))}" target="_blank" rel="noopener" aria-label="WhatsApp ile iletişim" data-contact="whatsapp" data-placement="floating">☏ <span>WhatsApp</span></a>
<a class="floating-button floating-phone" href="tel:+{phone_digits(site['phone'])}" aria-label="Telefonla ara" data-contact="phone" data-placement="floating">☎ <span>Ara</span></a></div>'''


def faq_items(items):
    return "".join(f'<details class="faq-item"><summary>{esc(item["question"])}</summary><div class="faq-answer"><p>{esc(item["answer"])}</p></div></details>' for item in items)


def json_script(value):
    data = json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")
    return '<script type="application/ld+json">' + data + '</script>'


def structured_data(title, description, path, breadcrumbs, service=None, faq=False):
    root = canonical()
    url = canonical(path)
    organization_id = root + "#isletme"
    graph = [
        {"@type": "Organization", "@id": organization_id, "name": site["brand"], "url": root, "telephone": "+" + phone_digits(site["phone"])},
        {"@type": "WebSite", "@id": root + "#website", "name": site["brand"], "url": root, "inLanguage": "tr-TR", "publisher": {"@id": organization_id}},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": description, "inLanguage": "tr-TR", "isPartOf": {"@id": root + "#website"}},
    ]
    if breadcrumbs:
        graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "item": canonical(item_path)} for i, (name, item_path) in enumerate(breadcrumbs, 1)]})
        graph[2]["breadcrumb"] = {"@id": url + "#breadcrumb"}
    if service:
        graph.append({"@type": "Service", "@id": url + "#service", "name": title.split(" | ")[0], "alternateName": service.get("aliases", []), "serviceType": service["name"], "description": description, "url": url, "provider": {"@id": organization_id}, "areaServed": {"@type": "AdministrativeArea", "name": "Eskişehir"}})
        graph[2]["mainEntity"] = {"@id": url + "#service"}
    if faq:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [{"@type": "Question", "name": item["question"], "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}} for item in faqs]})
    return json_script({"@context": "https://schema.org", "@graph": graph})


def breadcrumb(items):
    return '<nav class="container breadcrumb" aria-label="Sayfa yolu">' + ' <span aria-hidden="true">/</span> '.join(f'<a href="{esc(route_url(path))}">{esc(name)}</a>' if i < len(items) - 1 else f'<span aria-current="page">{esc(name)}</span>' for i, (name, path) in enumerate(items)) + '</nav>'


def page(title, description, content, path="", breadcrumbs=None, service=None, district=None, faq=False, not_found=False):
    robots = "index, follow" if site.get("indexable") and not not_found else "noindex, follow"
    canonical_tag = '' if not_found else f'<link rel="canonical" href="{esc(canonical(path))}">'
    schema = '' if not_found else structured_data(title, description, path, breadcrumbs, service, faq)
    return f'''<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="{robots}">
  {canonical_tag}
  <meta property="og:type" content="website">
  <meta property="og:locale" content="tr_TR">
  <meta property="og:site_name" content="{esc(site['brand'])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical(path))}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{esc(asset_url('styles.css'))}">
  {schema}
</head>
<body data-page-path="{esc(route_url(path))}" data-service="{esc(service['slug'] if service else '')}" data-district="{esc(district['slug'] if district else '')}">
  <a class="skip-link" href="#icerik">İçeriğe geç</a>
  <div class="site-top"><div class="container"><span><strong>Eskişehir</strong> yapı dekorasyon hizmetleri</span><a href="tel:+{phone_digits(site['phone'])}" data-contact="phone" data-placement="top">{esc(phone_display())}</a></div></div>
  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="/" aria-label="Eskişehir Yapı Dekorasyon ana sayfa"><span class="brand-mark" aria-hidden="true">YD</span><span class="brand-copy"><strong>{esc(site['brand'])}</strong><span>{esc(site['tagline'])}</span></span></a>
      <button class="menu-button" type="button" data-menu-button aria-label="Menüyü aç" aria-controls="site-navigation" aria-expanded="false">☰</button>
      <nav class="nav-links" id="site-navigation" data-nav-links aria-label="Ana menü">
        <a href="/#hizmetler">Hizmetler</a><a href="/sss/">SSS</a><a href="/#bolgeler">Hizmet Bölgeleri</a><a href="/#surec">Süreç</a><a class="nav-quote" href="/#teklif">Teklif iste</a>
      </nav>
    </div>
  </header>
  {content}
  <footer class="footer"><div class="container footer-inner"><span>© <span data-year>{date.today().year}</span> {esc(site['brand'])}</span><span>Fayans · Duvar · Çatı · Karasıva · Alçı · Boya</span><a href="tel:+{phone_digits(site['phone'])}" data-contact="phone" data-placement="footer">{esc(phone_display())}</a></div></footer>
  {floating_contact(service, district, path)}
  <script src="{esc(asset_url('script.js'))}" defer></script>
</body>
</html>'''


def write_page(path, output):
    destination = DIST / path / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8")


def service_cards():
    return "".join(f'''<a class="card" href="{route_url(service_path(s))}"><span class="card-icon" aria-hidden="true">{icon_for(s['slug'])}</span><div><h3>{esc(s['name'])}</h3><p>{esc(s['short'])}</p></div><span class="card-link">Hizmeti incele →</span></a>''' for s in services)


def location_cards(service):
    return "".join(f'<a class="location-link" href="{route_url(service_path(service, d))}"><span>{esc(d["name"])}</span><span aria-hidden="true">↗</span></a>' for d in districts)


def home_districts():
    cards = []
    for district in districts:
        links = "".join(f'<a href="{route_url(service_path(s, district))}">{esc(s["name"])} <span aria-hidden="true">→</span></a>' for s in services)
        cards.append(f'<details class="district-card"><summary>{esc(district["name"])}</summary><div class="district-services">{links}</div></details>')
    return "".join(cards)


def service_links_for(current_service, district=None):
    return "".join(f'<a href="{route_url(service_path(s, district))}">{esc(s["name"])} →</a>' for s in services if s["slug"] != current_service["slug"])


def list_items(items):
    return '<ul class="check-list">' + ''.join(f'<li>{esc(item)}</li>' for item in items) + '</ul>'


def quote_form(service=None, district=None, path=""):
    service_options = ''.join(f'<option value="{esc(s["slug"])}"{" selected" if service and s["slug"] == service["slug"] else ""}>{esc(s["name"])}</option>' for s in services)
    district_options = ''.join(f'<option value="{esc(d["slug"])}"{" selected" if district and d["slug"] == district["slug"] else ""}>{esc(d["name"])}</option>' for d in districts)
    return f'''<section class="quote-section" id="teklif" aria-labelledby="quote-title">
<div class="quote-intro"><div class="section-kicker">İşinizi anlatın</div><h2 id="quote-title">Teklif görüşmesini başlatalım.</h2><p>Hizmetinizi ve ilçenizi seçin. Yaklaşık ölçüyü ve yapmak istediğiniz işi ekleyerek WhatsApp mesajınızı hazırlayın.</p><p>Göndermeden önce mesajı düzenleyebilir, sohbet açılınca fotoğraf ekleyebilirsiniz. Kesin kapsam ve çalışma takvimi görüşmede netleşir.</p><a class="text-contact" href="tel:+{phone_digits(site['phone'])}" data-contact="phone" data-placement="quote">Telefon: {esc(phone_display())}</a></div>
<form class="quote-form" data-quote-form data-whatsapp="{phone_digits(site['whatsapp'])}" data-source="{esc(canonical(path))}" aria-labelledby="quote-title" hidden>
  <div class="form-field"><label for="quote-service">Hizmet</label><select id="quote-service" name="service" required><option value="">Hizmet seçin</option>{service_options}</select></div>
  <div class="form-field"><label for="quote-district">İlçe</label><select id="quote-district" name="district" required><option value="">İlçe seçin</option>{district_options}</select></div>
  <div class="form-field full-width"><label for="quote-size">Yaklaşık ölçü <span>(isteğe bağlı)</span></label><input id="quote-size" name="size" type="text" maxlength="80" placeholder="Örn. 20 m² zemin veya 3 oda" autocomplete="off"></div>
  <div class="form-field full-width"><label for="quote-details">Yapılacak iş <span>(isteğe bağlı)</span></label><textarea id="quote-details" name="details" rows="3" maxlength="600" placeholder="Mevcut durum ve istediğiniz değişikliği kısaca anlatın."></textarea></div>
  <button class="button whatsapp-submit full-width" type="submit">WhatsApp’ta devam et →</button>
  <p class="form-note full-width">Bu form mesajınızı hazırlar. Talebiniz, WhatsApp’ta mesajı gönderdiğinizde bize ulaşır.</p>
</form>
<noscript><div class="actions">{contact_block(service, district, 'quote-fallback', path)}</div></noscript>
</section>'''


def project_image_path(value):
    relative = Path(value)
    path = (ASSETS / relative).resolve()
    projects_root = (ASSETS / "projects").resolve()
    if relative.is_absolute() or not path.is_relative_to(projects_root) or not path.is_file():
        raise ValueError(f"Project image must be a real file in assets/projects: {value}")
    if path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".avif"):
        raise ValueError(f"Unsupported project image: {value}")
    return path


def published_projects():
    result = []
    for project in projects:
        if project.get("published") is not True:
            continue
        for key in ("title", "summary", "service_slug", "district_slug", "before_image", "after_image", "before_alt", "after_alt"):
            if not project.get(key):
                raise ValueError(f"Published project is missing {key}")
        if project["service_slug"] not in {s["slug"] for s in services} or project["district_slug"] not in {d["slug"] for d in districts}:
            raise ValueError("Unknown project service or district")
        project_image_path(project["before_image"])
        project_image_path(project["after_image"])
        result.append(project)
    return result


def project_gallery(service=None, district=None):
    selected = [p for p in published_projects() if (not service or p["service_slug"] == service["slug"]) and (not district or p["district_slug"] == district["slug"])]
    if not selected:
        return ""
    cards = []
    for p in selected:
        place = next(d["name"] for d in districts if d["slug"] == p["district_slug"])
        images = ''.join(f'<figure><img src="/{esc(p[key])}" alt="{esc(p[alt])}" loading="lazy" decoding="async"><figcaption>{label}</figcaption></figure>' for key, alt, label in (("before_image", "before_alt", "Önce"), ("after_image", "after_alt", "Sonra")))
        cards.append(f'<article class="project-card"><span class="section-kicker">{esc(place)}</span><h3>{esc(p["title"])}</h3><p>{esc(p["summary"])}</p><div class="project-images">{images}</div></article>')
    return '<section class="project-gallery" aria-labelledby="projects-title"><h2 id="projects-title">Tamamlanan işler</h2><div class="project-grid">' + ''.join(cards) + '</div></section>'


def build_home():
    gallery = project_gallery()
    gallery_section = f'<section class="section"><div class="container">{gallery}</div></section>' if gallery else ''
    content = f'''<main id="icerik">
<section class="hero"><div class="container hero-grid"><div><div class="eyebrow">Eskişehir Yapı Dekorasyon</div><h1>Eskişehir’de yapı ve <span>dekorasyon işleri.</span></h1><p class="lead">Fayans, duvar, çatı, karasıva, alçı ve boya işleri için yapılacak işi, bulunduğunuz ilçeyi ve yaklaşık ölçüyü paylaşın; uygulama kapsamını ve teklif sürecini birlikte netleştirelim.</p><div class="actions"><a class="button primary" href="#teklif">İşinizi anlatın, teklif isteyin</a><a class="button secondary" href="#hizmetler">Hizmetleri incele</a></div><p class="hero-contact">Telefonla görüşmek için <a href="tel:+{phone_digits(site['phone'])}" data-contact="phone" data-placement="hero">{esc(phone_display())}</a></p></div>
<div class="hero-card"><div class="blueprint" aria-hidden="true"></div><div class="hero-card-content"><div><span class="small-label">İşin başında netlik</span><h2>Önce ihtiyacı konuşalım.</h2><ol class="hero-steps"><li>Hizmet ve ilçe</li><li>Alan ve mevcut durum</li><li>Kapsam ve çalışma planı</li></ol></div><div class="hero-card-footer"><span>Fayans · Duvar · Çatı · Karasıva · Alçı · Boya</span></div></div></div></div></section>
<section class="section" id="hizmetler"><div class="container"><div class="section-head"><div><div class="section-kicker">Hizmetlerimiz</div><h2>İhtiyacınıza göre altı hizmet.</h2></div><p>Her hizmetin hazırlığı, malzemesi ve uygulama süreci farklıdır. İlgili sayfada kapsamı, teklif öncesinde gereken bilgileri ve sık sorulan soruları inceleyebilirsiniz.</p></div><div class="cards">{service_cards()}</div></div></section>
{gallery_section}
<section class="section" id="surec"><div class="container split"><div><div class="section-kicker">Çalışma yaklaşımı</div><h2>İşin kapsamı baştan belli olsun.</h2><p class="lead">Bir teklifi değerlendirirken yapılacak uygulamayı, hazırlık işlerini ve malzeme teminini birlikte konuşmak gerekir.</p></div><div class="panel"><h3>Görüşmede neleri netleştirelim?</h3>{list_items(['İlçe, mahalle ve uygulama alanının mevcut durumu', 'Hazırlık, söküm ve tamamlayıcı işlerin kapsamı', 'Malzeme seçimi ve temin sorumluluğu', 'Uygun keşif zamanı, çalışma planı ve teslim kapsamı'])}</div></div></section>
<section class="section" id="bolgeler"><div class="container"><div class="section-head"><div><div class="section-kicker">Eskişehir ilçeleri</div><h2>İlçenizi ve hizmetinizi seçin.</h2></div><p>İlçe başlığına dokunarak ilgili hizmete ulaşabilirsiniz. Mahalle, işin kapsamı ve ulaşım koşullarını paylaşarak hizmet uygunluğunu ve çalışma planını görüşmede teyit edin.</p></div><div class="district-grid">{home_districts()}</div></div></section>
<section class="section faq-teaser"><div class="container faq-teaser-grid"><div><div class="section-kicker">Sıkça sorulanlar</div><h2>İşe başlamadan önce.</h2><p class="lead">Malzeme, teklif kapsamı ve uygulama hazırlığıyla ilgili sorularınız için kısa açıklamalar.</p><div class="actions"><a class="button primary" href="/sss/">Tüm soruları incele</a></div></div><div class="faq-preview">{faq_items(faqs[:3])}</div></div></section>
<section class="section" id="iletisim"><div class="container">{quote_form()}</div></section>
</main>'''
    write_page('', page(f'{site["brand"]} | Fayans, Duvar, Çatı, Karasıva, Alçı ve Boya', site["description"], content))


def build_service(service):
    path = service_path(service)
    data = service_content[service["slug"]]
    title = f'{region["name"]} {service["name"]}'
    trail = [("Ana sayfa", ""), (title, path)]
    steps = ''.join(f'<li><h3>{esc(step["title"])}</h3><p>{esc(step["text"])}</p></li>' for step in data["process"])
    content = f'''<main id="icerik">{breadcrumb(trail)}
<section class="page-hero"><div class="container"><div class="eyebrow">Eskişehir · Hizmetler</div><h1>{esc(title)}</h1><p class="lead">{esc(data['intro'])}</p><div class="actions"><a class="button primary" href="#teklif">Bu iş için teklif iste</a><a class="button secondary" href="#kapsam">İş kapsamını incele</a></div></div></section>
<section class="section"><div class="container service-layout"><article class="content-card"><h2 id="kapsam">{esc(data['scope_title'])}</h2>{list_items(data['scope'])}<p>{esc(data['detail'])}</p>
<h2 class="content-heading">Uygulama süreci nasıl planlanır?</h2><ol class="process-list">{steps}</ol>
<h2 class="content-heading">Fiyatı hangi unsurlar etkiler?</h2><p>Teklifleri aynı iş kapsamı üzerinden karşılaştırın. İşçilik, malzeme ve ek hazırlıkların hangilerinin dahil olduğunu görüşmede netleştirin.</p>{list_items(data['pricing'])}
<h2 class="content-heading">Teklif öncesinde hazırlayabilecekleriniz</h2>{list_items(data['preparation'])}
{project_gallery(service)}
<h2 class="content-heading">{esc(service['name'])} hakkında sorular</h2><div class="faq-list service-faq">{faq_items(data['faqs'])}</div>
<h2 class="content-heading">Eskişehir ilçelerinde teklif talebi</h2><p>İlçenizi seçip işin bulunduğu mahalleyi görüşmede paylaşın. Hizmet uygunluğu ve çalışma takvimi işin kapsamına göre netleştirilir.</p><div class="location-grid">{location_cards(service)}</div></article>
<aside class="info-box"><h2>İşinizi konuşalım</h2><p>{esc(service['short'])} Yaklaşık ölçü ve mevcut durum fotoğraflarıyla ön görüşmeyi başlatabilirsiniz.</p><div class="actions">{contact_block(service, placement='sidebar', path=path)}</div><a class="inline-link" href="#teklif">Teklif formunu doldur →</a><h3>Diğer hizmetler</h3><div class="mini-links">{service_links_for(service)}</div><a class="inline-link" href="/sss/">Tüm sık sorulan sorular →</a></aside></div></section>
<section class="section quote-wrap"><div class="container">{quote_form(service, path=path)}</div></section></main>'''
    write_page(path, page(title + ' | ' + site['brand'], data['description'], content, path, trail, service))


def build_district(service, district):
    path = service_path(service, district)
    city_path = service_path(service)
    data = service_content[service['slug']]
    title = f'{district["name"]} {service["name"]}'
    trail = [("Ana sayfa", ""), (f'Eskişehir {service["name"]}', city_path), (district["name"], path)]
    description = f'{district["name"]}, Eskişehir {service["name"].lower()} talebiniz için iş kapsamı, hazırlık ve teklif bilgileri. İlçe ve işinizi paylaşarak telefon veya WhatsApp ile ulaşın.'
    content = f'''<main id="icerik">{breadcrumb(trail)}
<section class="page-hero"><div class="container"><div class="eyebrow">{esc(district['name'])} · Eskişehir</div><h1>{esc(title)}</h1><p class="lead">{esc(district['name'])} için {esc(service['name'].lower())} arıyorsanız, yapılacak işi ve bulunduğunuz mahalleyi paylaşarak teklif görüşmesini başlatabilirsiniz. İş kapsamını, hizmet uygunluğunu ve çalışma zamanını birlikte netleştirelim.</p><div class="actions"><a class="button primary" href="#teklif">{esc(district['name'])} için teklif iste</a></div></div></section>
<section class="section"><div class="container service-layout"><article class="content-card"><h2>{esc(data['scope_title'])}</h2>{list_items(data['scope'])}<p>{esc(data['district_note'])}</p>
<h2 class="content-heading">{esc(district['name'])} için görüşmeye hazırlık</h2>{list_items(data['preparation'])}<p>Mahalle, uygulama yapılacak kat ve alana erişim bilgilerini de paylaşın. Yerinde inceleme gerekip gerekmediği ve uygun çalışma planı bu bilgilerle değerlendirilir.</p>
<h2 class="content-heading">Teklifin kapsamını birlikte netleştirelim</h2><p>İşçilik ve malzemenin yanında hazırlık, taşıma ve tamamlayıcı işlerin dahil olup olmadığını konuşun. Kesin fiyat ve süre, alanın durumu ve seçilecek uygulama belirlenmeden netleşmez.</p><a class="inline-link" href="{route_url(city_path)}">Eskişehir {esc(service['name'])}: ayrıntılı uygulama ve fiyat etkenleri →</a>
{project_gallery(service, district)}
<h2 class="content-heading">Teklif öncesinde sık sorulanlar</h2><div class="faq-list service-faq">{faq_items(data['faqs'][:2])}</div></article>
<aside class="info-box"><h2>{esc(district['name'])} için iletişim</h2><p>İşinizi anlatmak için arayabilir veya WhatsApp’tan yazabilirsiniz.</p><div class="actions">{contact_block(service, district, 'sidebar', path)}</div><a class="inline-link" href="#teklif">Bu ilçe için formu doldur →</a><h3>{esc(district['name'])} için diğer hizmetler</h3><div class="mini-links">{service_links_for(service, district)}</div><a class="inline-link" href="/sss/">Sık sorulan sorular →</a></aside></div></section>
<section class="section quote-wrap"><div class="container">{quote_form(service, district, path)}</div></section></main>'''
    write_page(path, page(title + ' | ' + site['brand'], description, content, path, trail, service, district))


def build_faq():
    trail = [("Ana sayfa", ""), ("Sıkça Sorulan Sorular", "sss")]
    service_links = ''.join(f'<a href="{route_url(service_path(s))}">{esc(s["name"])} →</a>' for s in services)
    content = f'''<main id="icerik">{breadcrumb(trail)}<section class="page-hero"><div class="container"><div class="eyebrow">Eskişehir Yapı Dekorasyon</div><h1>Sıkça Sorulan Sorular</h1><p class="lead">Fayans, duvar, çatı, karasıva, alçı ve boya işleri için teklif, malzeme ve uygulama öncesi hazırlık soruları.</p></div></section><section class="section"><div class="container faq-layout"><div class="faq-list">{faq_items(faqs)}</div><aside class="info-box"><h2>İşinizi konuşalım</h2><p>İşin türünü, bulunduğunuz ilçeyi ve yaklaşık alanı paylaşarak başlayabilirsiniz.</p><div class="actions">{contact_block(placement='faq', path='sss')}</div><a class="inline-link" href="/#teklif">Teklif formuna geç →</a><div class="mini-links">{service_links}</div></aside></div></section></main>'''
    write_page('sss', page('SSS | ' + site['brand'], 'Eskişehir yapı dekorasyon, fayans, duvar, çatı, karasıva, alçı ve boya işleri: teklif, malzeme, hazırlık ve uygulama süreci hakkında sık sorulan sorular.', content, 'sss', trail, faq=True))


def build_robots_and_sitemap():
    robots = f'User-agent: *\nAllow: /\nSitemap: {canonical()}sitemap.xml\n' if site.get('indexable') else 'User-agent: *\nDisallow: /\n'
    (DIST / 'robots.txt').write_text(robots, encoding='utf-8')
    paths = ['', 'sss']
    for service in services:
        paths.append(service_path(service))
        paths.extend(service_path(service, district) for district in districts)
    if not site.get('indexable'):
        paths = []
    updated = site.get('content_updated', '')
    lastmod = f'<lastmod>{date.fromisoformat(updated).isoformat()}</lastmod>' if updated else ''
    entries = '\n'.join(f'  <url><loc>{esc(canonical(path))}</loc>{lastmod}</url>' for path in paths)
    (DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '\n</urlset>\n', encoding='utf-8')


def build_404():
    content = '<main id="icerik"><section class="section"><div class="container"><div class="content-card"><div class="section-kicker">Sayfa bulunamadı</div><h1>Aradığınız sayfa burada değil.</h1><p class="lead">Ana sayfadan hizmetlere ulaşabilir veya teklif görüşmesini başlatabilirsiniz.</p><div class="actions"><a class="button primary" href="/">Ana sayfaya dön</a><a class="button secondary" href="/#teklif">Teklif iste</a></div></div></div></section></main>'
    (DIST / '404.html').write_text(page('Sayfa bulunamadı | ' + site['brand'], 'Aradığınız sayfa bulunamadı.', content, '404', not_found=True), encoding='utf-8')


def main():
    approved = published_projects()
    if set(service_content) != {s['slug'] for s in services}:
        raise ValueError('Every configured service needs its own content')
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True, exist_ok=True)
    for name in ('styles.css', 'script.js', 'favicon.svg'):
        shutil.copy2(ASSETS / name, DIST / name)
    for project in approved:
        for key in ('before_image', 'after_image'):
            source = project_image_path(project[key])
            target = DIST / source.relative_to(ASSETS)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    (DIST / '.nojekyll').touch()
    if site.get('custom_domain'):
        (DIST / 'CNAME').write_text(site['custom_domain'].strip() + '\n', encoding='utf-8')
    build_home()
    build_faq()
    for service in services:
        build_service(service)
        for district in districts:
            build_district(service, district)
    build_robots_and_sitemap()
    build_404()
    print(f"Generated {sum(1 for _ in DIST.rglob('index.html'))} HTML pages for {region['name']}.")


if __name__ == '__main__':
    main()
