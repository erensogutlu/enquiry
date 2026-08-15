#  ENQUIRY — Sosyal Medya OSINT İstihbarat Aracı

[Türkçe](README.md) | [English](README_EN.md)

```
    ███████╗███╗   ██╗ ██████╗ ██╗   ██╗██╗██████╗ ██╗   ██╗
    ██╔════╝████╗  ██║██╔═══██╗██║   ██║██║██╔══██╗╚██╗ ██╔╝
    █████╗  ██╔██╗ ██║██║   ██║██║   ██║██║██████╔╝ ╚████╔╝ 
    ██╔══╝  ██║╚██╗██║██║▄▄ ██║██║   ██║██║██╔══██╗  ╚██╔╝  
    ███████╗██║ ╚████║╚██████╔╝╚██████╔╝██║██║  ██║   ██║   
    ╚══════╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝   ╚═╝   
```

Sosyal medya kullanıcı adları, e-posta adresleri, telefon numaraları, IP/domain ve görsel dosyaları üzerinden açık kaynak istihbarat toplayan bir OSINT aracı. Kali Linux ve Python 3.8+ ile tam uyumludur.

---

##  Özellikler

| Özellik | Açıklama |
|---|---|
| **Kullanıcı Adı Arama** | 110+ platformda asenkron kullanıcı adı taraması |
| **E-Posta İstihbaratı** | MX kayıtları, Gravatar, GitHub, itibar kontrolü |
| **Telefon Numarası Analizi** | Ülke, operatör, hat tipi, format bilgileri |
| **IP / Domain Analizi** | WHOIS, DNS, GeoIP, port tarama |
| **Görsel Metadata (EXIF)** | GPS koordinatları, kamera bilgisi, çekim tarihi |
| **Profil Tarama** | GitHub, Reddit, Steam, Lichess, Hacker News profilleri |
| **Kapsamlı Analiz** | Tüm modülleri tek seferde çalıştırma |
| **Rapor Oluşturma** | JSON ve HTML formatında profesyonel raporlar |
| **Renkli Terminal Çıktısı** | Tablo, panel, ilerleme çubuğu |
| **İnteraktif + CLI Modu** | Menülü veya parametreli kullanım |

---

##  Kurulum

### Kali Linux (Önerilen)

```bash
git clone https://github.com/erensogutlu/enquiry.git
cd enquiry
chmod +x kurulum.sh
sudo bash kurulum.sh
```

### Diğer Linux Dağıtımları / Windows / macOS

```bash
pip3 install -r requirements.txt
```

### Python Sürüm Uyumluluğu

| Python Sürümü | Durum |
|---|---|
| Python 3.8 | [+] Desteklenir |
| Python 3.9 | [+] Desteklenir |
| Python 3.10 | [+] Desteklenir |
| Python 3.11 | [+] Desteklenir |
| Python 3.12 | [+] Desteklenir |
| Python 3.13+ | [+] Desteklenir |

---

##  Kullanım — Adım Adım Rehber

Enquiry'yi kullanmanın **2 yolu** var:

1. **İnteraktif Mod** → Menüden seçim yaparak kullanırsınız. Yeni başlayanlar için idealdir.
2. **Komut Satırı Modu** → Parametrelerle doğrudan çalıştırırsınız. Hızlı kullanım için idealdir.

>  **Hiçbir parametre vermezseniz** otomatik olarak interaktif mod açılır.

---

###  1. Kullanıcı Adı Arama (110+ Platform)

**Ne yapar?** Girdiğiniz kullanıcı adını Instagram, Twitter, GitHub, TikTok, Steam gibi 110'dan fazla platformda arar. Her platformu asenkron olarak kontrol eder, bu sayede çok hızlıdır.

**Ne zaman kullanılır?** Bir kullanıcı adının hangi platformlarda kayıtlı olduğunu öğrenmek istediğinizde.

```bash
python3 enquiry.py -k johndoe
```

**Açıklama:**
- `-k` veya `--kullanici` → aranacak kullanıcı adı
- Araç 110 platformu eşzamanlı tarar ve bulunan profillerin linklerini listeler

**Örnek çıktı:**
```
┌──────────────────────────  Kullanıcı Adı Arama ───────────────────────────┐
│ Kullanıcı Adı: johndoe                                                      │
│ Platform Sayısı: 110                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
   110 platform taranıyor... ---------------------------------------- 100%

                             [+] Bulunan Profiller
┌─────────────────┬──────────────┬─────────────────────────────────────────┐
│ Platform        │ Kategori     │ URL                                     │
├─────────────────┼──────────────┼─────────────────────────────────────────┤
│ Instagram       │ sosyal_medya │ https://www.instagram.com/johndoe       │
│ GitHub          │ gelistirici  │ https://github.com/johndoe              │
│ Twitter/X       │ sosyal_medya │ https://x.com/johndoe                   │
│ Steam           │ oyun         │ https://steamcommunity.com/id/johndoe   │
│ ...             │ ...          │ ...                                     │
└─────────────────┴──────────────┴─────────────────────────────────────────┘

┌────────────────────────────────  Özet ─────────────────────────────────┐
│ [+] Bulunan: 53  |  [-] Bulunamayan: 57  |   Toplam: 110                 │
└──────────────────────────────────────────────────────────────────────────┘
```

---

###  2. E-Posta İstihbaratı

**Ne yapar?** E-posta adresinin hangi servislerde kayıtlı olduğunu, MX kayıtlarını, Gravatar profilini, GitHub hesaplarını ve e-posta itibarını kontrol eder.

**Ne zaman kullanılır?** Bir e-posta adresinin arkasındaki kişi/kurum hakkında bilgi toplamak istediğinizde.

```bash
python3 enquiry.py -e user@gmail.com
```

**Parçalara ayırarak açıklayalım:**

| Parametre | Ne yazılır | Anlamı |
|---|---|---|
| `-e` | `user@gmail.com` | Analiz edilecek e-posta adresi |

**Araç çalışırken ne olur?**
1. E-posta formatını doğrular
2. Alan adının MX kayıtlarını çeker (gmail sunucuları, outlook sunucuları vb.)
3. E-posta sağlayıcısını tespit eder (Gmail, Outlook, ProtonMail vb.)
4. Gravatar profil kontrolü yapar
5. GitHub'da bu e-postayla kayıtlı hesapları arar
6. E-posta itibar kontrolü yapar (şüpheli mi, referans sayısı vb.)

**Örnek çıktı:**
```
                     E-Posta Analiz Sonuçları
┌──────────────────────┬──────────────────────────────────────────┐
│ Bilgi                │ Değer                                    │
├──────────────────────┼──────────────────────────────────────────┤
│ E-Posta              │ user@gmail.com                           │
│ Kullanıcı            │ user                                     │
│ Alan Adı             │ gmail.com                                │
│ Sağlayıcı            │ Google Workspace / Gmail                 │
│ Format Geçerli       │ [+] evet                                  │
└──────────────────────┴──────────────────────────────────────────┘
                MX Kayıtları
┌─────────────────────────────────┬─────────┐
│ Sunucu                          │ Öncelik │
│ gmail-smtp-in.l.google.com      │ 5       │
│ alt1.gmail-smtp-in.l.google.com │ 10      │
└─────────────────────────────────┴─────────┘
```

---

###  3. Telefon Numarası Analizi

**Ne yapar?** Telefon numarasından ülke, operatör, hat tipi (mobil/sabit), format bilgilerini ve saat dilimini çıkarır.

**Ne zaman kullanılır?** Bilinmeyen bir numaranın hangi ülke ve operatöre ait olduğunu öğrenmek istediğinizde.

```bash
python3 enquiry.py -t +905551234567
```

**Açıklama:**
- `-t` veya `--telefon` → analiz edilecek telefon numarası
- Numarayı **uluslararası formatta** girin (başında `+` ve ülke kodu olmalı)
- Örnek: Türkiye için `+90`, ABD için `+1`, Almanya için `+49`

**Örnek çıktı:**
```
               Telefon Numarası Analiz Sonuçları
┌────────────────────────┬─────────────────────────────────────┐
│ Bilgi                  │ Değer                               │
├────────────────────────┼─────────────────────────────────────┤
│ Geçerlilik             │ [+] geçerli                          │
│ Uluslararası Format    │ +90 555 123 45 67                   │
│ Ulusal Format          │ 0555 123 45 67                      │
│ E.164 Format           │ +905551234567                       │
│ Ülke Kodu              │ +90                                 │
│ Ülke / Bölge           │ Türkiye                             │
│ Operatör               │ Turk Telekom                        │
│ Hat Tipi               │ mobil                            │
│ Saat Dilimi            │ Europe/Istanbul                     │
└────────────────────────┴─────────────────────────────────────┘
```

>  **Numara formatı yanlışsa?** Araç size hata mesajı gösterir ve doğru formatı önerir. Numaranın başına ülke kodunu (`+90`, `+1` vb.) eklediğinizden emin olun.

---

###  4. IP / Domain Analizi

**Ne yapar?** Bir IP adresi veya domain üzerinde WHOIS sorgusu, DNS kayıt analizi, GeoIP konum tespiti ve temel port taraması yapar.

**Ne zaman kullanılır?** Bir web sitesinin veya IP adresinin arkasındaki bilgileri (sahip, konum, açık portlar, DNS kayıtları) öğrenmek istediğinizde.

**a) Domain analizi:**
```bash
python3 enquiry.py -i example.com
```

**b) IP adresi analizi:**
```bash
python3 enquiry.py -i 8.8.8.8
```

**Parçalara ayırarak açıklayalım:**

| Parametre | Ne yazılır | Anlamı |
|---|---|---|
| `-i` | `example.com` veya `8.8.8.8` | Analiz edilecek domain veya IP adresi |

**Araç çalışırken ne olur?**
1. Domain ise → IP adresini çözer
2. IP ise → ters DNS sorgusu yapar
3. WHOIS sorgusu ile domain/IP kayıt bilgilerini çeker
4. DNS kayıtlarını çeker (A, AAAA, MX, NS, TXT, CNAME, SOA)
5. GeoIP ile coğrafi konumu tespit eder (ülke, şehir, ISP, koordinatlar)
6. 17 temel portu tarar (HTTP, HTTPS, SSH, FTP, MySQL, RDP vb.)

**Örnek çıktı:**
```
                    GeoIP Konum Bilgisi
┌────────────────────┬─────────────────────────────────────┐
│  Ülke            │ United States                       │
│  Bölge           │ California                          │
│  Şehir           │ Mountain View                       │
│  ISP             │ Google LLC                          │
│  Koordinatlar    │ 37.4225, -122.085                   │
└────────────────────┴─────────────────────────────────────┘
               Açık Portlar
┌──────────┬─────────────────┬────────────┐
│ Port     │ Servis          │ Durum      │
│ 80       │ HTTP            │ açık       │
│ 443      │ HTTPS           │ açık       │
└──────────┴─────────────────┴────────────┘
```

---

###  5. Görsel Metadata Analizi (EXIF)

**Ne yapar?** Bir fotoğraf dosyasındaki gizli metadata bilgilerini çıkarır. GPS koordinatları, kamera/cihaz bilgisi, çekim tarihi, yazılım bilgisi gibi verileri gösterir.

**Ne zaman kullanılır?** Bir fotoğrafın nerede, ne zaman, hangi cihazla çekildiğini öğrenmek istediğinizde.

```bash
python3 enquiry.py -g /yol/fotograf.jpg
```

**Açıklama:**
- `-g` veya `--gorsel` → analiz edilecek görsel dosyasının tam yolu
- JPG, PNG, TIFF gibi formatları destekler
- GPS verisi varsa Google Maps linki oluşturur

**Örnek çıktı:**
```
                 Dosya Bilgileri
┌──────────────────────┬─────────────────────────────────────┐
│ Dosya Adı            │ fotograf.jpg                        │
│ Format               │ JPEG                                │
│ Boyutlar             │ 4032x3024                           │
│ Dosya Boyutu         │ 3.45 MB                             │
└──────────────────────┴─────────────────────────────────────┘
┌──────────────────────────── [!] GPS Konumu ─────────────────────────────┐
│  GPS Koordinatları Bulundu!                                          │
│                                                                        │
│ Enlem: 41.008238                                                       │
│ Boylam: 28.978359                                                      │
│  Google Maps: https://www.google.com/maps?q=41.008238,28.978359     │
└────────────────────────────────────────────────────────────────────────┘
```

> [!] **Dikkat:** GPS verisi, fotoğrafın tam olarak nerede çekildiğini gösterir. Bu kişisel güvenlik açısından hassas bir bilgidir.

---

###  6. Sosyal Medya Profil Tarama

**Ne yapar?** Bir kullanıcı adını GitHub, Reddit, Steam, Lichess ve Hacker News API'leri üzerinden tarar. Sadece kullanıcı adı aramasından farklı olarak, **profil detaylarını** (bio, takipçi, repo sayısı, karma vb.) çeker.

**Ne zaman kullanılır?** Bir kullanıcının detaylı profil bilgilerini (istatistikler, hesap geçmişi vb.) öğrenmek istediğinizde.

```bash
python3 enquiry.py -p torvalds
```

**Açıklama:**
- `-p` veya `--profil` → taranacak kullanıcı adı
- GitHub API ile: isim, bio, konum, şirket, repo sayısı, takipçi, son repolar
- Reddit API ile: karma, premium durumu, moderatörlük
- Steam: görünen isim, çevrimiçi durumu
- Lichess: oyun istatistikleri, dereceler
- Hacker News: karma, hakkında bilgisi

**Örnek çıktı:**
```
                            GitHub Profili
┌────────────────────┬─────────────────────────────────────────────────┐
│  İsim            │ Linus Torvalds                                  │
│  Konum           │ Portland, OR                                    │
│  Şirket          │ Linux Foundation                                │
│  İstatistikler   │  12 repo  |   310495 takipçi  |   0 takip │
│  Hesap Oluşturma │ 2011-09-03                                      │
└────────────────────┴─────────────────────────────────────────────────┘
                              Son Güncel Repolar
┌──────────────────────┬────────────┬────────┬──────────────────────────┐
│ Repo                 │ Dil        │      │ Açıklama                 │
│ linux                │ C          │ 238567 │ Linux kernel source tree │
│ AudioNoise           │ C          │ 4425   │ Random digital audio...  │
└──────────────────────┴────────────┴────────┴──────────────────────────┘
```

---

###  7. Kapsamlı Analiz (Tüm Modüller)

**Ne yapar?** Bir kullanıcı adı üzerinden uygulanabilir tüm modülleri tek seferde çalıştırır: 110+ platform taraması + profil tarama.

**Ne zaman kullanılır?** Bir kullanıcı hakkında mümkün olan en fazla bilgiyi toplamak istediğinizde.

```bash
python3 enquiry.py --kapsamli johndoe
```

>  Bu mod birkaç dakika sürebilir çünkü 110+ platform + 5 API aynı anda taranır.

---

###  8. Rapor Oluşturma (Sonuçları Kaydetme)

Herhangi bir analiz sonucunu **JSON** veya **HTML** formatında otomatik kaydedebilirsiniz:

**a) JSON rapor kaydetme:**
```bash
python3 enquiry.py -k johndoe -r json
```

**b) HTML rapor kaydetme (tarayıcıda açılabilir):**
```bash
python3 enquiry.py -k johndoe -r html
```

**c) Hem JSON hem HTML kaydetme:**
```bash
python3 enquiry.py -k johndoe -r ikisi
```

**d) İnteraktif modda kaydetme:**
Herhangi bir analiz tamamlandıktan sonra araç size sorar:
```
 Sonuçları rapor olarak kaydetmek ister misiniz? [e/h/json/html/ikisi]:
```

Raporlar `raporlar/` klasörüne `enquiry_rapor_20260706_153000.json` gibi tarih damgalı isimlerle kaydedilir.

---

###  9. Yardım Menüsü

Parametre listesini ve kısa açıklamalarını görmek için:

```bash
python3 enquiry.py -h
```

---

##  Hızlı Başlangıç — Sıfırdan Kullanım Senaryosu

Hiç bilmiyorsanız, bu adımları sırayla takip edin:

```bash
# Adım 1: Bağımlılıkları kurun.
pip3 install -r requirements.txt

# Adım 2: İnteraktif modu açın (menüden seçim yapabilirsiniz).
python3 enquiry.py

# Adım 3: Veya doğrudan bir kullanıcı adı arayın.
python3 enquiry.py -k hedef_kullanici_adi

# Adım 4: Daha fazla bilgi için profil tarama yapın.
python3 enquiry.py -p hedef_kullanici_adi

# Adım 5: E-posta adresini analiz edin.
python3 enquiry.py -e hedef@gmail.com

# Adım 6: Tüm sonuçları rapor olarak kaydedin.
python3 enquiry.py --kapsamli hedef_kullanici_adi -r ikisi
```

---

##  Tüm Parametreler (Referans Tablosu)

| Parametre | Kısa Hali | Zorunlu mu? | Açıklama |
|---|---|---|---|
| `--kullanici` | `-k` | Hayır | Kullanıcı adını 110+ platformda ara |
| `--eposta` | `-e` | Hayır | E-posta adresi üzerinde istihbarat topla |
| `--telefon` | `-t` | Hayır | Telefon numarasını analiz et |
| `--ip` | `-i` | Hayır | IP adresi veya domain analizi yap |
| `--gorsel` | `-g` | Hayır | Görsel dosyasının EXIF bilgilerini çıkar |
| `--profil` | `-p` | Hayır | Sosyal medya profillerini detaylı tara |
| `--kapsamli` | — | Hayır | Tüm modüllerle kapsamlı analiz yap |
| `--rapor` | `-r` | Hayır | Rapor formatı: `json`, `html` veya `ikisi` |
| `--surum` | — | Hayır | Sürüm bilgisini göster |
| `-h` | — | Hayır | Yardım menüsü |

>  **Hiçbir parametre vermezseniz** interaktif mod açılır — menüden istediğiniz modülü seçebilirsiniz.

---

##  Proje Yapısı

```
enquiry/
├── enquiry.py              ← Ana giriş noktası (CLI + İnteraktif Menü)
├── moduller/
│   ├── __init__.py         ← Paket init
│   ├── kullanici_adi.py    ← 110+ platform asenkron kullanıcı adı arama
│   ├── eposta.py           ← E-posta istihbarat modülü
│   ├── telefon.py          ← Telefon numarası analiz modülü
│   ├── ip_domain.py        ← IP/Domain analiz modülü (WHOIS, DNS, GeoIP)
│   ├── gorsel_meta.py      ← Görsel EXIF/metadata modülü
│   ├── profil_tarama.py    ← Sosyal medya profil tarama modülü
│   └── rapor.py            ← JSON/HTML rapor oluşturma modülü
├── veriler/
│   ├── platformlar.json    ← 110 platform URL şablonları ve kategorileri
│   └── eposta_servisleri.json ← E-posta servis API bilgileri
├── raporlar/               ← Oluşturulan raporlar (otomatik oluşur)
├── requirements.txt        ← Python bağımlılıkları
├── kurulum.sh              ← Kali Linux otomatik kurulum betiği
├── README.md               ← Türkçe dokümantasyon
└── README_EN.md            ← İngilizce dokümantasyon
```

---

##  Sık Sorulan Sorular

**S: Telefon numarasını girdim ama hata alıyorum?**
Numarayı uluslararası formatta girin: başında `+` ve ülke kodu olmalı. Örnek: `+905551234567` (Türkiye), `+12125551234` (ABD). Sadece `05551234567` yazarsanız çalışmaz.

**S: Kullanıcı adı araması çok uzun sürüyor?**
110 platform asenkron olarak taranır, normalde 15-30 saniye sürer. İnternet hızınıza bağlı olarak değişebilir. Bazı platformlar zaman aşımına uğrayabilir — bu normaldir.

**S: "Bulunan" profiller gerçekten doğru mu?**
Araç HTTP 200 durum koduna bakarak karar verir. Bazı platformlar her kullanıcı adı için 200 döndürebilir (false positive). Sonuçları profil linkine tıklayarak doğrulayın.

**S: E-posta analizi API anahtarı istiyor mu?**
Temel özellikler (MX, Gravatar, GitHub) anahtarsız çalışır. Have I Been Pwned gibi bazı gelişmiş servisler API anahtarı gerektirebilir.

**S: Raporlar nereye kaydedilir?**
`raporlar/` klasörüne kaydedilir. Dosya isimleri tarih damgalıdır: `enquiry_rapor_20260706_153000.json`.

**S: HTTPS trafiğini veya şifreli verileri çözebilir mi?**
Hayır. Bu araç yalnızca herkese açık (public) veriler üzerinde çalışır. Hiçbir şifreleme kırma veya yetkisiz erişim işlemi yapmaz.

**S: Windows'ta çalışır mı?**
Evet. `python enquiry.py` komutuyla doğrudan çalışır. PowerShell veya CMD kullanabilirsiniz.

---

## [!] Yasal Uyarı

Bu araç **yalnızca eğitim ve yasal amaçlarla** tasarlanmıştır.
Yalnızca herkese açık (public) veriler toplanır — hiçbir sisteme yetkisiz erişim sağlanmaz.
Aracı kullanırken tüm yerel ve uluslararası yasalara uymak **kullanıcının sorumluluğundadır**.
Geliştiriciler, aracın kötüye kullanımından sorumlu tutulamaz.

---

##  Lisans

Bu proje eğitim amaçlıdır.

---

**Geliştirici:** Eren
**Sürüm:** 1.0.0
**Platform:** Kali Linux / Python 3.8+
