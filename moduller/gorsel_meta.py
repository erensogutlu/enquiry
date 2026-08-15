#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# görsel metadata analiz modülü
# görsellerdeki exif/metadata bilgilerini çıkarır

import os
from datetime import datetime
from typing import Dict, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

try:
    # pyrefly: ignore [missing-import]
    from PIL import Image
    # pyrefly: ignore [missing-import]
    from PIL.ExifTags import TAGS, GPSTAGS
    PILLOW_MEVCUT = True
except ImportError:
    PILLOW_MEVCUT = False

konsol = Console()


class GorselMetaAnaliz:
    """görsellerdeki metadata bilgilerini çıkaran sınıf"""

    def __init__(self):
        self.sonuclar: Dict = {}

    def analiz_et(self, dosya_yolu: str) -> Dict:
        """görsel dosyasındaki metadata bilgilerini çıkarır"""
        konsol.print(
            Panel(
                f"[bold white]Dosya:[/] [bold green]{dosya_yolu}[/]",
                title="[bold cyan] Görsel Metadata Analizi[/]",
                border_style="cyan",
            )
        )

        if not PILLOW_MEVCUT:
            konsol.print("[bold red][!] pillow kütüphanesi yüklü değil![/]")
            konsol.print("[yellow]Kurulum: pip install Pillow[/]")
            return {"hata": "pillow kütüphanesi bulunamadı"}

        # dosya kontrolü
        if not os.path.isfile(dosya_yolu):
            konsol.print(f"[bold red][-] Dosya bulunamadı: {dosya_yolu}[/]")
            return {"hata": "dosya bulunamadı"}

        self.sonuclar = {
            "dosya_yolu": dosya_yolu,
            "dosya_adi": os.path.basename(dosya_yolu),
            "dosya_boyutu": 0,
            "format": "",
            "boyutlar": "",
            "mod": "",
            "exif": {},
            "gps": {},
            "kamera": {},
        }

        try:
            # dosya boyutu
            self.sonuclar["dosya_boyutu"] = os.path.getsize(dosya_yolu)

            # görseli aç
            gorsel = Image.open(dosya_yolu)
            self.sonuclar["format"] = gorsel.format or "bilinmiyor"
            self.sonuclar["boyutlar"] = f"{gorsel.width}x{gorsel.height}"
            self.sonuclar["mod"] = gorsel.mode

            # exif verilerini çıkar
            exif_veri = gorsel._getexif()
            if exif_veri:
                self._exif_ayristir(exif_veri)
            else:
                konsol.print("[yellow][i] bu görselde exif verisi bulunamadı.[/]")

        except Exception as hata:
            self.sonuclar["hata"] = f"görsel işlenemedi: {str(hata)}"
            konsol.print(f"[bold red][-] Hata: {str(hata)}[/]")
            return self.sonuclar

        self._sonuclari_goster()
        return self.sonuclar

    def _exif_ayristir(self, exif_veri: dict):
        """exif verilerini okunabilir formata dönüştürür"""
        for etiket_id, deger in exif_veri.items():
            etiket = TAGS.get(etiket_id, etiket_id)

            # gps verileri
            if etiket == "GPSInfo":
                self._gps_ayristir(deger)
                continue

            # kamera bilgileri
            if etiket in ("Make", "Model", "LensModel", "LensMake"):
                kamera_alan = {
                    "Make": "marka",
                    "Model": "model",
                    "LensModel": "lens_modeli",
                    "LensMake": "lens_markasi",
                }
                self.sonuclar["kamera"][kamera_alan.get(etiket, etiket)] = str(deger)
                continue

            # tarih bilgileri
            if etiket in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                tarih_alan = {
                    "DateTime": "degistirilme_tarihi",
                    "DateTimeOriginal": "cekim_tarihi",
                    "DateTimeDigitized": "dijitallestirme_tarihi",
                }
                self.sonuclar["exif"][tarih_alan.get(etiket, etiket)] = str(deger)
                continue

            # diğer exif verileri
            try:
                # bazı değerler byte olabilir, string'e dönüştür
                if isinstance(deger, bytes):
                    deger = deger.decode("utf-8", errors="ignore")
                self.sonuclar["exif"][str(etiket)] = str(deger)
            except Exception:
                pass

    def _gps_ayristir(self, gps_veri):
        """gps verilerini koordinatlara dönüştürür"""
        gps_bilgi = {}

        for anahtar, deger in gps_veri.items():
            etiket = GPSTAGS.get(anahtar, anahtar)
            gps_bilgi[etiket] = deger

        # koordinatları derece/dakika/saniye'den ondalık formata dönüştür
        try:
            enlem = self._dms_den_ondaliga(
                gps_bilgi.get("GPSLatitude"),
                gps_bilgi.get("GPSLatitudeRef", "N")
            )
            boylam = self._dms_den_ondaliga(
                gps_bilgi.get("GPSLongitude"),
                gps_bilgi.get("GPSLongitudeRef", "E")
            )

            if enlem is not None and boylam is not None:
                self.sonuclar["gps"] = {
                    "enlem": round(enlem, 6),
                    "boylam": round(boylam, 6),
                    "google_maps": f"https://www.google.com/maps?q={enlem},{boylam}",
                    "yukseklik": str(gps_bilgi.get("GPSAltitude", "-")),
                }
            else:
                self.sonuclar["gps"] = {"hata": "koordinatlar çözümlenemedi"}

        except Exception:
            self.sonuclar["gps"] = {"hata": "gps verisi işlenemedi"}

    @staticmethod
    def _dms_den_ondaliga(dms, yonelim) -> Optional[float]:
        """derece/dakika/saniye formatını ondalık formata dönüştürür"""
        if dms is None:
            return None

        try:
            # ifd rational değerleri
            derece = float(dms[0])
            dakika = float(dms[1])
            saniye = float(dms[2])

            ondalik = derece + (dakika / 60.0) + (saniye / 3600.0)

            if yonelim in ("S", "W"):
                ondalik = -ondalik

            return ondalik
        except (IndexError, TypeError, ValueError):
            return None

    def _sonuclari_goster(self):
        """sonuçları terminal ekranında gösterir"""
        # dosya bilgileri
        dosya_tablo = Table(
            title=" Dosya Bilgileri",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
        )
        dosya_tablo.add_column("Bilgi", style="bold white", min_width=20)
        dosya_tablo.add_column("Değer", style="green", min_width=35)

        dosya_tablo.add_row("Dosya Adı", self.sonuclar["dosya_adi"])
        dosya_tablo.add_row("Format", self.sonuclar["format"])
        dosya_tablo.add_row("Boyutlar", self.sonuclar["boyutlar"])
        dosya_tablo.add_row("Renk Modu", self.sonuclar["mod"])

        # dosya boyutunu okunabilir formata dönüştür
        boyut = self.sonuclar["dosya_boyutu"]
        if boyut > 1024 * 1024:
            boyut_str = f"{boyut / (1024 * 1024):.2f} MB"
        elif boyut > 1024:
            boyut_str = f"{boyut / 1024:.2f} KB"
        else:
            boyut_str = f"{boyut} B"
        dosya_tablo.add_row("Dosya Boyutu", boyut_str)

        konsol.print()
        konsol.print(dosya_tablo)

        # kamera bilgileri
        kamera = self.sonuclar.get("kamera", {})
        if kamera:
            kamera_tablo = Table(
                title=" Kamera / Cihaz Bilgileri",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow",
            )
            kamera_tablo.add_column("Bilgi", style="bold white", min_width=20)
            kamera_tablo.add_column("Değer", style="green", min_width=35)

            alan_isimleri = {
                "marka": "Marka",
                "model": "Model",
                "lens_modeli": "Lens Modeli",
                "lens_markasi": "Lens Markası",
            }
            for anahtar, baslik in alan_isimleri.items():
                if anahtar in kamera:
                    kamera_tablo.add_row(baslik, kamera[anahtar])

            konsol.print(kamera_tablo)

        # gps bilgileri
        gps = self.sonuclar.get("gps", {})
        if gps and "hata" not in gps:
            konsol.print(
                Panel(
                    f"[bold green] GPS Koordinatları Bulundu![/]\n\n"
                    f"[bold white]Enlem:[/] {gps.get('enlem', '-')}\n"
                    f"[bold white]Boylam:[/] {gps.get('boylam', '-')}\n"
                    f"[bold white]Yükseklik:[/] {gps.get('yukseklik', '-')}\n\n"
                    f"[bold cyan] Google Maps:[/] {gps.get('google_maps', '-')}",
                    title="[bold red][!] GPS Konumu[/]",
                    border_style="red",
                )
            )

        # exif verileri
        exif = self.sonuclar.get("exif", {})
        if exif:
            # önemli exif alanlarını göster
            onemli_alanlar = {
                "cekim_tarihi": " Çekim Tarihi",
                "degistirilme_tarihi": " Değiştirilme Tarihi",
                "dijitallestirme_tarihi": " Dijitalleştirme Tarihi",
                "Software": " Yazılım",
                "ImageDescription": " Açıklama",
                "Copyright": "© Telif Hakkı",
                "Artist": " Sanatçı",
                "XResolution": " X Çözünürlük",
                "YResolution": " Y Çözünürlük",
                "ExposureTime": "⏱ Poz Süresi",
                "FNumber": " F Sayısı",
                "ISOSpeedRatings": " ISO",
                "FocalLength": " Odak Uzaklığı",
                "Flash": " Flaş",
            }

            exif_tablo = Table(
                title=" EXIF Verileri",
                show_header=True,
                header_style="bold magenta",
                border_style="magenta",
            )
            exif_tablo.add_column("Alan", style="bold white", min_width=22)
            exif_tablo.add_column("Değer", style="green", min_width=35)

            # önce önemli alanları göster
            for anahtar, baslik in onemli_alanlar.items():
                if anahtar in exif:
                    exif_tablo.add_row(baslik, str(exif[anahtar])[:60])

            # diğer alanları göster
            diger_sayisi = 0
            for anahtar, deger in exif.items():
                if anahtar not in onemli_alanlar and diger_sayisi < 10:
                    exif_tablo.add_row(str(anahtar)[:25], str(deger)[:60])
                    diger_sayisi += 1

            konsol.print(exif_tablo)

            toplam = len(exif)
            if toplam > len(onemli_alanlar) + 10:
                konsol.print(f"[dim]... ve {toplam - len(onemli_alanlar) - 10} ek alan (raporda görüntülenebilir)[/]")
