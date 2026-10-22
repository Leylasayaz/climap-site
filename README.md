# Clim-Map

**Bul. Yönlendir. Ölç.** Diyarbakır'da aşırı sıcaktan en çok etkilenen ama resmi verilerde görünmeyen çocukları ve açık havada çalışanları bulan, yardımı onlara yönlendiren ve sonucu ölçen iklim adaleti haritası.

Tech4Climate Ideathon · Diyarbakır 2026 · Sultan Ayaz

Bu depo, fikrin 3D (Three.js) tanıtım sitesidir: Diyarbakır dioraması, canlı sıcak simülasyonu, Bul–Yönlendir–Ölç sahneleri, örnek senaryo ve jüri soruları.

## Kendi bilgisayarında çalıştır

Gerekenler: [Git](https://git-scm.com) ve Python 3 (macOS'ta ikisi de hazır gelir).

```bash
git clone https://github.com/Leylasayaz/climap-site.git
cd climap-site
python3 -m http.server 8765
```

Sonra tarayıcıda aç: <http://localhost:8765>

Durdurmak için terminalde `Ctrl + C`.

> İnternet bağlantısı gerekir: Three.js ve yazı tipleri CDN'den yüklenir.

## Dosyalar

- `index.html` — sitenin tamamı (HTML, CSS ve Three.js sahnesi tek dosyada)

## Not

3D şehir, risk hücreleri, sensör değerleri ve arayüz maketlerindeki sayılar temsilidir; pilotta gerçek uydu ve saha verisiyle değişir.
