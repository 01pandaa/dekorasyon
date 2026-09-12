# Eskişehir Yapı Dekorasyon

Eskişehir merkezli yapı ve dekorasyon hizmetleri için programmatic SEO pilot sitesi.

## Mimari

- Kaynak veriler: data/site.json ve data/locations.json
- Sayfa üretimi: scripts/build.py
- Statik çıktı: dist/
- Yayın: GitHub Actions + GitHub Pages
- İlk aşama: Eskişehir, 14 ilçe ve 5 ana hizmet
- İndeksleme: alan adı ve işletme bilgileri kesinleşene kadar kapalı

## Yayına almadan önce

1. data/site.json içindeki telefon, WhatsApp, e-posta ve adres alanlarını gerçek bilgilerle doldur.
2. Alan adı DNS ayarlarını yap.
3. Alan adı GitHub Pages'e bağlandıktan sonra site.json içindeki indexable değerini true yap.
4. scripts/build.py çalıştırarak sitemap ve tüm sayfaları üret.
5. Google Search Console property'sini ekle.

İlçe sayfaları tek bir şablondan üretilir; ancak ilerleyen aşamada gerçek proje fotoğrafları, hizmet kapsamı ve ilçe bazlı bilgiler eklenmelidir.