# Clim-Map

**Bul. Yönlendir. Ölç.** Diyarbakır'da aşırı sıcaktan en çok etkilenen ama resmi verilerde görünmeyen çocukları ve açık havada çalışanları bulan, yardımı onlara yönlendiren ve sonucu ölçen iklim adaleti haritası.

Tech4Climate Ideathon · Diyarbakır 2026 · Sultan Ayaz

Bu depo, Clim-Map'in etkileşimli harita sitesidir. Site gerçek bir Diyarbakır haritasıyla açılır ve 8 duraklı rehberli bir turla başlar: harita sırayla şehir geneline, bir okul çatısına, bir pazar yerine, bir şantiyeye, yaşlıların yoğun yaşadığı bir mahalleye, bir meydana ("Neden her eve değil?") uçar; ardından destekçi ve belediye görünümüyle biter. Turdan sonra serbest keşif modunda katmanlar, Belediye / Destekçi / Vatandaş görünümleri, "Yarın 41°C ise ne olur?" uyarısı ve tıklanabilir sıcak noktalar kullanılabilir. Altında kısa bir anlatım var.

Tasarım koyu yeşil bir harita panosu: solda katman ve filtre anahtarları (risk eşiği, mikro-konum tipi, müdahale önerileri), ortada arama ve araç çubuklu harita, sağda pilot bölge mini haritası, göstergeler, öncelik listesi ve grafikler.

Altlık: Esri Dark Gray Canvas (anahtar gerektirmez). Karolar yüklenemezse harita sade zeminde OSM verisiyle çizilir.

**Veri:** İlçe sınırları, okullar, pazar ve inşaat alanları, Dicle, surlar, yollar ve bina yoğunluğu © OpenStreetMap katkıda bulunanlar (ODbL), Ekim 2026'da alındı ve `index.html` içine gömüldü. Yüzey sıcaklığı, risk puanı, sıcak noktalar, Serin Durak ve yaşlı yoğunluğu **temsilidir**. `tools/build_data.py` ham OSM dosyalarından bu gömülü veriyi üretir.

## Kendi bilgisayarında çalıştır

Gerekenler: [Git](https://git-scm.com) ve Python 3 (macOS'ta ikisi de hazır gelir).

```bash
git clone https://github.com/Leylasayaz/climap-site.git
cd climap-site
python3 -m http.server 8765
```

Sonra tarayıcıda aç: <http://localhost:8765>

Durdurmak için terminalde `Ctrl + C`.

> İnternet bağlantısı gerekir: Leaflet, harita karoları ve yazı tipleri internetten yüklenir. Karolar yüklenemezse harita sade zeminde OSM verisiyle çizilir.

## Dosyalar

- `index.html`: sitenin tamamı (HTML, CSS, JS ve gömülü harita verisi tek dosyada)
- `tools/build_data.py`: OSM ham verisinden gömülü veriyi üreten betik

## Not

Sıcaklık, risk ve sensör değerleri temsilidir; pilotta gerçek uydu ve saha verisiyle değişir.
