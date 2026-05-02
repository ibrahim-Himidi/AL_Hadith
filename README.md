# 📖 HadithSearch — Hadis Arama Platformu

**HadithSearch**, Sahih Bukhari külliyatındaki **7.277 hadisi** Arapça ve İngilizce olarak arayabileceğiniz, modern bir web arama platformudur. Türkçe, Arapça ve İngilizce arayüz desteği ile hem masaüstü hem de mobil cihazlarda sorunsuz çalışır.

> 🎓 Bu proje, Ostim Teknik Üniversitesi öğrencileri tarafından geliştirilmiştir.  
> 📬 İletişim: [230205913@ostimteknik.edu.tr](mailto:230205913@ostimteknik.edu.tr) · [230205928@ostimteknik.edu.tr](mailto:230205928@ostimteknik.edu.tr)

---

## 🌟 Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🔍 **Çift Dil Arama** | Arapça veya İngilizce sorgular otomatik algılanır |
| 🕌 **7.277 Hadis** | Sahih Bukhari'nin tamamı indekslenmiştir |
| 🌐 **RTL / LTR Desteği** | Arapça için sağdan sola (RTL) arayüz |
| 📚 **Kitap & Ravi Filtresi** | Sonuçları kitaba veya raviye göre daraltın |
| ✨ **Arama Vurgulama** | Eşleşen kelimeler hadis kartında renkle işaretlenir |
| 📱 **Mobil Uyumlu** | Tüm ekran boyutlarında düzgün görünür |
| 🤖 **HadithAI** | Yapay zeka destekli hadis analizi *(yakında)* |

---

## 🏗️ Proje Yapısı

```
AL_Hadith-master/
├── backend/                   # FastAPI (Python) API sunucusu
│   ├── app/
│   │   ├── main.py            # API giriş noktası
│   │   ├── config.py          # Ayarlar (.env dosyasını okur)
│   │   ├── database/          # Veritabanı modelleri ve bağlantı
│   │   ├── routers/           # API endpoint'leri (arama, auth, favoriler)
│   │   └── services/          # İş mantığı (BM25, hibrit arama)
│   ├── scripts/
│   │   ├── init.sql           # Veritabanı şeması
│   │   └── import_data.py     # CSV → MySQL veri aktarımı
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Vue.js 3 + Vite arayüzü
│   ├── src/
│   │   ├── App.vue            # Ana uygulama bileşeni
│   │   ├── components/
│   │   │   └── HadithCard.vue # Hadis kartı
│   │   └── services/
│   │       └── api.js         # Backend API bağlantısı
│   ├── index.html
│   └── package.json
├── veriler csv/
│   ├── bukhari_arabic.csv     # 7.277 Arapça hadis
│   └── bukhari_english.csv    # 7.277 İngilizce hadis
├── docker-compose.yml         # MySQL + Qdrant + Backend
├── .env.example               # Ortam değişkeni şablonu
└── README.md
```

---

## ⚙️ Gereksinimler

Kuruluma başlamadan önce aşağıdaki yazılımların bilgisayarınızda kurulu olduğundan emin olun:

| Yazılım | Minimum Sürüm | İndirme |
|---------|---------------|---------|
| **Docker Desktop** | 24.0+ | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Node.js** | 18.0+ | [nodejs.org](https://nodejs.org/) |
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) |
| **Git** | herhangi | [git-scm.com](https://git-scm.com/) |

> 💡 **Windows kullanıcıları:** Docker Desktop'ı yükledikten sonra bilgisayarı yeniden başlatmanız gerekebilir.

---

## 🚀 Kurulum Adımları

### Adım 1 — Projeyi İndirin

```bash
git clone https://github.com/kullanici-adi/AL_Hadith.git
cd AL_Hadith-master
```

ya da ZIP olarak indirdiyseniz, klasörü açıp terminal ile içine girin.

---

### Adım 2 — Ortam Değişkenlerini Ayarlayın

Proje kök dizinindeki `.env.example` dosyasını kopyalayın:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Mac / Linux
cp .env.example .env
```

`.env` dosyasını bir metin editörüyle açın ve `SECRET_KEY` satırını güncelleyin:

```env
SECRET_KEY=buraya_guclu_bir_sifre_yazin_en_az_32_karakter
```

> ⚠️ `.env` dosyasını **asla** GitHub'a yüklemeyiniz. Zaten `.gitignore` ile korunmaktadır.

---

### Adım 3 — Docker ile Veritabanını Başlatın

```bash
# MySQL ve Qdrant container'larını başlat
docker compose up -d db qdrant

# Container'ların çalıştığını doğrula
docker compose ps
```

Beklenen çıktı:
```
NAME              STATUS
hadis_mysql       running
hadis_qdrant      running
```

> ⏳ İlk başlatmada Docker image'ları indirilir. Bu birkaç dakika sürebilir.

---

### Adım 4 — Veritabanına Veri Aktarın

Bu adım 7.277 hadisi MySQL'e yükler.

```bash
# Backend klasörüne girin
cd backend

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt

# Veri aktarımını başlat (yaklaşık 2-4 dakika sürer)
python scripts/import_data.py
```

Başarılı çıktı örneği:
```
[3/5] Mevcut veriler temizleniyor...
[4/5] Hadisler import ediliyor...
Import: 100%|████████████| 7277/7277 [03:12<00:00, 37.8 hadis/s]
[5/5] Tamamlandı! 7277 hadis yüklendi.
```

> 💡 Sadece ilk 100 hadisi test etmek için: `python scripts/import_data.py --limit 100`

---

### Adım 5 — Backend API'yi Çalıştırın

```bash
# backend/ klasöründeyken:
uvicorn app.main:app --reload
```

API hazır olduğunda terminalde şunu görürsünüz:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

API belgelerini görüntülemek için tarayıcınızda açın: **http://localhost:8000/docs**

---

### Adım 6 — Frontend'i Çalıştırın

Yeni bir terminal penceresi açın:

```bash
# Proje kök dizinine geri dönün
cd frontend

# Bağımlılıkları yükleyin (ilk seferinde)
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```

Başarılı çıktı:
```
  VITE v8.0.x  ready in 480 ms

  ➜  Local:   http://localhost:5173/
```

Tarayıcınızda açın: **http://localhost:5173**

---

## 📋 Hızlı Başlangıç (Kurulum Sonrası)

Projeyi daha önce kurduysanız her seferinde sadece şu adımları uygulayın:

```bash
# 1. Veritabanı container'larını başlat
docker compose up -d db qdrant

# 2. API'yi başlat (yeni terminal)
cd backend
uvicorn app.main:app --reload

# 3. Frontend'i başlat (yeni terminal)
cd frontend
npm run dev
```

| Servis | Adres |
|--------|-------|
| 🌐 Web Arayüzü | http://localhost:5173 |
| 🔌 API | http://localhost:8000 |
| 📄 API Belgeleri | http://localhost:8000/docs |

---

## 🔌 API Endpoint'leri

| Metod | URL | Açıklama |
|-------|-----|----------|
| `GET` | `/` | Sağlık kontrolü |
| `GET` | `/docs` | Swagger arayüzü |
| `GET` | `/ara?q=prayer&dil=en` | İngilizce arama |
| `GET` | `/ara?q=الصلاة&dil=ar` | Arapça arama |
| `GET` | `/hadis/{id}` | Tekil hadis detayı |
| `POST` | `/auth/register` | Kullanıcı kaydı |
| `POST` | `/auth/login` | Giriş ve token alma |

---

## 🧪 Test Etme

API'nin çalıştığını doğrulamak için:

```bash
# Sağlık kontrolü
curl http://localhost:8000/

# İngilizce arama
curl "http://localhost:8000/ara?q=prayer&dil=en"

# Arapça arama
curl "http://localhost:8000/ara?q=الصلاة&dil=ar"
```

---

## 🐛 Sık Karşılaşılan Sorunlar

### ❌ Docker container başlamıyor
```bash
# Docker'ın çalıştığını kontrol edin
docker info

# Container loglarını inceleyin
docker compose logs db
```

### ❌ `pip install` hatası veriyor
```bash
# pip'i güncelleyin
python -m pip install --upgrade pip

# Tekrar deneyin
pip install -r requirements.txt
```

### ❌ `npm install` hatası veriyor
```bash
# Node.js versiyonunu kontrol edin (18+ olmalı)
node --version

# node_modules'u temizleyip yeniden deneyin
rm -rf node_modules
npm install
```

### ❌ Veri aktarımında "Connection refused" hatası
Docker container'ların tamamen başlaması için 30 saniye bekleyip tekrar deneyin:
```bash
docker compose ps   # STATUS: running olduğunu doğrulayın
python scripts/import_data.py
```

### ❌ Port zaten kullanımda
```bash
# 5173 portunu kullanan uygulamayı bulun
# Windows:
netstat -ano | findstr :5173

# Frontend için farklı port kullanın
npm run dev -- --port 5174
```

---

## 📦 Kullanılan Teknolojiler

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| **Frontend** | Vue.js 3 + Vite | 3.x / 8.x |
| **Stil** | Tailwind CSS | 3.x |
| **Backend API** | FastAPI + Uvicorn | 0.115 |
| **Veritabanı** | MySQL 8.0 | 8.0 |
| **ORM** | SQLAlchemy (async) | 2.0 |
| **Vektör DB** | Qdrant | 1.12 |
| **Auth** | JWT + bcrypt | — |
| **Container** | Docker + Compose | 24+ |

---

## 👥 Geliştirici Ekibi

Bu proje, **Ostim Teknik Üniversitesi** öğrencileri tarafından geliştirilmiştir.

📬 Bize ulaşmak için:
- [230205913@ostimteknik.edu.tr](mailto:230205913@ostimteknik.edu.tr,230205928@ostimteknik.edu.tr)
- [230205928@ostimteknik.edu.tr](mailto:230205913@ostimteknik.edu.tr,230205928@ostimteknik.edu.tr)

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Hadis içerikleri kamuya açık kaynaklara dayanmaktadır.
