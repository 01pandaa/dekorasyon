# Ölçüm ve yerel işletme görünürlüğü

## Hazır olan iletişim akışı

Site, telefon ve WhatsApp bağlantılarında 0543 371 99 72 numarasını kullanır. WhatsApp mesajına kaynak sayfa, formda ise seçilen hizmet ve ilçe bilgileri eklenir. Form alanları sunucuya kaydedilmez; mesaj WhatsApp içinde ziyaretçi tarafından gönderilir.

Bir düğmeye tıklama, gerçekleşen telefon görüşmesi veya alınan iş olarak sayılmamalıdır. İşletme, gelen görüşme ve iş sonucunu ayrıca takip etmelidir.

## GA4 / Tag Manager bağlantısına hazırlık

Henüz bir GA4 ölçüm kimliği veya Tag Manager konteyneri bağlanmadı. Mevcut olaylar tarayıcının bellek içi dataLayer listesine eklenir; bağlantı kurulmadıkça rapor oluşmaz ve bu olaylar Google'a gönderilmez.

| Olay | Ne zaman oluşur? | Parametreler |
| --- | --- | --- |
| contact_click | Telefon veya doğrudan WhatsApp bağlantısına tıklanınca | page_path, service_slug, district_slug, contact_method, contact_placement |
| quote_whatsapp_open | Geçerli teklif formundan WhatsApp açılınca | Aynı parametreler; hizmet ve ilçe form seçiminden gelir |

İsim, telefon, yaklaşık ölçü, serbest iş açıklaması ve hazırlanmış WhatsApp mesajı ölçüm olaylarına eklenmez. Sayfa yolu sorgu parametrelerini içermez.

Bağlantıyı tamamlamak için bu siteye ait GA4 web akışı ve/veya Tag Manager konteyneri gerekir. Tag Manager'da iki olay adı için özel olay tetikleyicileri ve ilgili veri katmanı değişkenleri tanımlanır. GA4 olay etiketleri doğru web akışına bağlanır; Preview ve DebugView ile tıklama/form olaylarının birer kez geldiği doğrulanır. Ziyaretçi tercihleri ve veri toplama ayarları hesabın kullanımına göre ayrıca yapılandırılır. Bu depo şu an herhangi bir analiz etiketi yüklemez.

Resmî kaynak: https://developers.google.com/tag-platform/tag-manager/datalayer

## Google İşletme Profili için gerekli bilgiler

Google İşletme Profili, GitHub üzerinden oluşturulamaz veya düzenlenemez. Var olan profilin bağlantısı ve yönetim erişimi doğrulanmadan ikinci bir profil oluşturulmamalıdır.

Tamamlanacak gerçek bilgiler:

- İşletmenin müşteriler tarafından kullanılan gerçek adı ve varsa mevcut profil bağlantısı.
- Kesin hizmet verilen ilçe/mahalleler ve fiilen yürütülen ana faaliyet.
- Gerçek çalışma ve iletişim saatleri.
- Müşteri kabul edilen bir iş yeri olup olmadığı; varsa doğru adres.
- İşletmenin kendi çalışma fotoğrafları ve yayın izni olan proje görselleri.

Sitede doğrulanmış marka, telefon ve alan adı profil ile tutarlı kullanılmalıdır. Müşterilere yerinde hizmet veriliyor ve adreste müşteri kabul edilmiyorsa profil, gerçek çalışma şekline uygun hizmet bölgesi işletmesi olarak değerlendirilir. Gerçek olmayan adres, çalışma saati, referans veya yorum eklenmez.

Resmî kaynak: https://support.google.com/business/answer/7091?hl=tr

## Search Console

Sitemap: https://www.yapidekorasyon.online/sitemap.xml

77 içerik URL'si korunur. Tarih yalnızca anlamlı içerik güncellemesini gösterir. Daha önce görülen 77 uyarının ayrıntısı bağlanan API çıktısında yer almadığı için nedeninin giderildiği iddia edilmez. Search Console site haritası ayrıntısındaki açıklama görülerek ayrıca incelenmelidir.

GSC görünürlük ve Google arama tıklamalarını; GA4/GTM ise yapılandırıldığında site içi etkileşimleri ölçer. İncelemelerde verinin tamamlandığı gün esas alınır ve aynı uzunluktaki dönemler karşılaştırılır.
