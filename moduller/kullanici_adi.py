#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# kullanıcı adı arama modülü
# birden fazla sosyal medya platformunda kullanıcı adını asenkron olarak arar

import asyncio
import json
import os
import ssl
from typing import Dict, List, Optional

# pyrefly: ignore [missing-import]
import aiohttp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel

konsol = Console()


class KullaniciAdiArama:
    """kullanıcı adını birden fazla platformda arar"""

    def __init__(self):
        # platform verilerini json dosyasından yükle
        self.platformlar = self._platformlari_yukle()
        self.sonuclar: List[Dict] = []
        self.bulunan_sayisi = 0
        self.taranan_sayisi = 0

    def _platformlari_yukle(self) -> list:
        """platformlar.json dosyasından platform listesini yükler"""
        dosya_yolu = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "veriler",
            "platformlar.json"
        )
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                veri = json.load(dosya)
                return veri.get("platformlar", [])
        except FileNotFoundError:
            konsol.print("[bold red][!] platformlar.json dosyası bulunamadı![/]")
            return []
        except json.JSONDecodeError:
            konsol.print("[bold red][!] platformlar.json dosyası bozuk![/]")
            return []

    async def _platformu_kontrol_et(
        self,
        oturum: aiohttp.ClientSession,
        platform: dict,
        kullanici_adi: str,
        ilerleme: Progress,
        gorev_id
    ) -> Optional[Dict]:
        """tek bir platformu kontrol eder"""
        url = platform["url"].format(kullanici_adi)
        sonuc = {
            "platform": platform["isim"],
            "url": url,
            "kategori": platform.get("kategori", "bilinmiyor"),
            "durum": "bilinmiyor",
            "bulundu": False
        }

        try:
            # ssl doğrulamasını esnek tut (bazı siteler sertifika sorunu yaşayabilir)
            ssl_baglam = ssl.create_default_context()
            ssl_baglam.check_hostname = False
            ssl_baglam.verify_mode = ssl.CERT_NONE

            basliklar = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            async with oturum.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                headers=basliklar,
                ssl=ssl_baglam,
                allow_redirects=True
            ) as yanit:
                durum_kodu = yanit.status

                if durum_kodu == 200:
                    sonuc["durum"] = "bulundu"
                    sonuc["bulundu"] = True
                    self.bulunan_sayisi += 1
                elif durum_kodu == 404:
                    sonuc["durum"] = "bulunamadı"
                elif durum_kodu == 301 or durum_kodu == 302:
                    sonuc["durum"] = "yönlendirme"
                elif durum_kodu == 403:
                    sonuc["durum"] = "erişim engellendi"
                elif durum_kodu == 429:
                    sonuc["durum"] = "hız sınırı"
                else:
                    sonuc["durum"] = f"durum kodu: {durum_kodu}"

        except asyncio.TimeoutError:
            sonuc["durum"] = "zaman aşımı"
        except aiohttp.ClientError:
            sonuc["durum"] = "bağlantı hatası"
        except Exception as hata:
            sonuc["durum"] = f"hata: {str(hata)[:30]}"

        self.taranan_sayisi += 1
        ilerleme.update(gorev_id, advance=1)
        return sonuc

    async def _asenkron_ara(self, kullanici_adi: str) -> List[Dict]:
        """tüm platformlarda asenkron olarak arar"""
        self.sonuclar = []
        self.bulunan_sayisi = 0
        self.taranan_sayisi = 0

        # bağlantı havuzu sınırlaması (sunuculara aşırı yük bindirmemek için)
        baglanti_siniri = aiohttp.TCPConnector(limit=30, limit_per_host=2)

        async with aiohttp.ClientSession(connector=baglanti_siniri) as oturum:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                console=konsol,
            ) as ilerleme:
                toplam = len(self.platformlar)
                gorev_id = ilerleme.add_task(
                    f" {toplam} platform taranıyor...",
                    total=toplam
                )

                gorevler = [
                    self._platformu_kontrol_et(oturum, platform, kullanici_adi, ilerleme, gorev_id)
                    for platform in self.platformlar
                ]

                self.sonuclar = await asyncio.gather(*gorevler)

        return self.sonuclar

    def ara(self, kullanici_adi: str) -> List[Dict]:
        """kullanıcı adını tüm platformlarda arar (senkron sarmalayıcı)"""
        konsol.print(
            Panel(
                f"[bold white]Kullanıcı Adı:[/] [bold green]{kullanici_adi}[/]\n"
                f"[bold white]Platform Sayısı:[/] [bold yellow]{len(self.platformlar)}[/]",
                title="[bold cyan] Kullanıcı Adı Arama[/]",
                border_style="cyan",
            )
        )

        # asyncio event loop'u çalıştır
        try:
            donus = asyncio.get_event_loop()
            if donus.is_running():
                # jupyter notebook gibi ortamlar için
                # pyrefly: ignore [missing-import]
                import nest_asyncio
                nest_asyncio.apply()
                sonuclar = donus.run_until_complete(self._asenkron_ara(kullanici_adi))
            else:
                sonuclar = donus.run_until_complete(self._asenkron_ara(kullanici_adi))
        except RuntimeError:
            sonuclar = asyncio.run(self._asenkron_ara(kullanici_adi))

        self._sonuclari_goster(sonuclar)
        return sonuclar

    def _sonuclari_goster(self, sonuclar: List[Dict]):
        """sonuçları tablo formatında gösterir"""
        # bulunanlar tablosu
        bulunanlar = [s for s in sonuclar if s and s.get("bulundu")]
        bulunamayanlar = [s for s in sonuclar if s and not s.get("bulundu")]

        if bulunanlar:
            tablo = Table(
                title="[+] Bulunan Profiller",
                show_header=True,
                header_style="bold green",
                border_style="green",
                title_style="bold green",
            )
            tablo.add_column("Platform", style="cyan", min_width=15)
            tablo.add_column("Kategori", style="yellow", min_width=12)
            tablo.add_column("URL", style="white", min_width=40)

            for sonuc in bulunanlar:
                kategori_renk = self._kategori_rengi(sonuc["kategori"])
                tablo.add_row(
                    f"[bold]{sonuc['platform']}[/]",
                    f"[{kategori_renk}]{sonuc['kategori']}[/]",
                    sonuc["url"]
                )

            konsol.print()
            konsol.print(tablo)

        # özet
        konsol.print()
        konsol.print(
            Panel(
                f"[bold green][+] Bulunan:[/] {len(bulunanlar)}  |  "
                f"[bold red][-] Bulunamayan:[/] {len(bulunamayanlar)}  |  "
                f"[bold white] Toplam:[/] {len(sonuclar)}",
                title="[bold white] Özet[/]",
                border_style="white",
            )
        )

    @staticmethod
    def _kategori_rengi(kategori: str) -> str:
        """kategoriye göre renk döndürür"""
        renkler = {
            "sosyal_medya": "bright_magenta",
            "gelistirici": "bright_green",
            "blog": "bright_yellow",
            "oyun": "bright_red",
            "medya": "bright_cyan",
            "tasarim": "bright_blue",
            "guvenlik": "red",
            "mesajlasma": "green",
            "forum": "yellow",
            "is": "blue",
            "diger": "white",
        }
        return renkler.get(kategori, "white")
