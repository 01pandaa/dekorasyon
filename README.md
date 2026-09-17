# Eskişehir Yapı Dekorasyon

Canlı site: https://www.yapidekorasyon.online/
Kaynak depo: https://github.com/01pandaa/dekorasyon

Python ile üretilen statik site. GitHub Actions, main dalındaki değişiklikleri derler ve dist/ klasörünü GitHub Pages üzerinde yayınlar.

## Yerel çalışma

Python 3.10 veya üzeri yeterlidir; harici Python paketi gerekmez.

    python scripts/build.py
    python scripts/check_site.py
    node --check assets/script.js
    node scripts/check_interactions.mjs

Çıktı: 92 içerik sayfası, ayrı 404 sayfası, sitemap.xml ve robots.txt.
dist/ derleme çıktısıdır; kaynak kontrolüne eklenmez.

## İçerik dosyaları

- data/site.json: marka, alan adı, mevcut telefon/WhatsApp ve altı hizmet.
- data/service-content.json: her hizmetin kapsamı, süreç, fiyat etkenleri, hazırlık bilgisi ve özel soruları.
- data/locations.json: mevcut 14 ilçe. İlçe sayfasının bulunması, her mahallede koşulsuz hizmet garantisi anlamına gelmez; uygunluk görüşmede teyit edilir.
- data/faq.json: ana sayfa ve SSS yanıtları.
- data/projects.json: yalnızca işletmenin yayın için onayladığı gerçek projeler.
- scripts/build.py: sayfa, yapılandırılmış veri, sitemap ve varlık üretimi.
- scripts/check_site.py: bağlantılar, sayfa içi hedefler, form etiketleri, metadata ve iletişim hedefleri.
- assets/script.js: erişilebilir menü, WhatsApp teklif formu ve ölçüm olayları.

Telefon: 0543 371 99 72. Telefon bağlantılarında +905433719972, WhatsApp bağlantılarında 905433719972 kullanılır.

## 16 Eylül 2026 düzenlemesi

- Müşteriye görünen pilot/taslak ifadeleri temizlendi.
- Beş hizmetin içeriği ve 70 ilçe sayfasının teklif bilgileri yenilendi.
- SSS iç bağlantısı ve derin 404 sayfalarının kök bağlantıları düzeltildi.
- Mevcut 77 URL korundu; site haritası son anlamlı içerik güncelleme tarihiyle üretildi.
- Organization, WebSite, WebPage, Service ve BreadcrumbList verileri eklendi. Gerçek adres, çalışma saati, fiyat veya yorum uydurulmadı.
- Hizmet/ilçe seçimi ve isteğe bağlı iş açıklaması içeren WhatsApp formu eklendi.
- WhatsApp mesajlarında kaynak sayfa bilgisi yer alır. Gönderim WhatsApp'ta kullanıcı tarafından tamamlanır.
- Menü klavye kontrolü, odak görünümü ve mobil form yerleşimi düzenlendi.
- Gerçek projeler için koşullu önce/sonra galerisi hazırlandı; veri boşken yayın sayfalarında boş galeri gösterilmez.

## 17 Eylül 2026 düzenlemesi

- Karasıva ustası altıncı ana hizmet olarak eklendi.
- Eskişehir karasıva ustası ana hizmet sayfası ile 14 ilçe için ayrı karasıva sayfaları üretime alındı.
- Ana sayfa, teklif formu, ilçe bağlantıları, SSS, yapılandırılmış veri ve sitemap karasıva hizmetini kapsayacak şekilde güncellendi.

## Ölçüm ve eksik işletme bilgileri

Telefon ve WhatsApp etkileşimleri dataLayer olayları üretir. Bu, tek başına kalıcı analiz veya GA4 raporu değildir. Bu depoda GA4/GTM hesabı, ölçüm kimliği veya veri toplama uç noktası yoktur. Ayrıntılı kurulum ve Google İşletme Profili hazırlığı docs/olcum-ve-yerel-profil.md dosyasındadır.

content_updated alanını yalnızca anlamlı bir içerik değişikliği olduğunda güncelleyin. Her derlemede yeni tarih yazılmaz. Sitemap lastmod eklenmesi, Search Console uyarılarının nedeninin çözüldüğü anlamına gelmez.

## Gerçek proje ekleme

1. Yayın izni olan önce/sonra görsellerini assets/projects/ altında WebP, JPEG, PNG veya AVIF olarak saklayın.
2. data/projects.json içine aşağıdaki alanlarla bir kayıt ekleyin:
   - title, summary
   - service_slug: data/site.json içindeki mevcut hizmet
   - district_slug: data/locations.json içindeki mevcut ilçe
   - before_image, after_image: projects/dosya-adi.webp biçiminde yollar
   - before_alt, after_alt: görsellerin gerçek içeriğini açıklayan metinler
   - published: işletme yayın için onayladıktan sonra true
3. Derleyip bağlantı kontrolünü çalıştırın.

Yalnızca published değeri true olan kayıtların görselleri yayına kopyalanır. Her proje ana sayfada, ilgili hizmet sayfasında ve ilgili ilçe sayfasında görünür. Görseller ve proje bilgileri olmadan örnek bir işi yapılmış gibi yayınlamayın.
