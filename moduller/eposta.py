#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# e-posta istihbarat modülü
# e-posta adresi üzerinden açık kaynak istihbarat toplar

import hashlib
import json
import os
import re
import socket
from typing import Dict, List, Optional

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    # pyrefly: ignore [missing-import]
    import dns.resolver
    DNS_MEVCUT = True
except ImportError:
    DNS_MEVCUT = False

konsol = Console()


class EpostaIstihbarat:
    """e-posta adresi üzerinden istihbarat toplayan sınıf"""

    def __init__(self):
        # e-posta servislerini json dosyasından yükle
        self.servisler = self._servisleri_yukle()
        self.sonuclar: Dict = {}

    def _servisleri_yukle(self) -> dict:
        """eposta_servisleri.json dosyasından servis listesini yükler"""
        dosya_yolu = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "veriler",
            "eposta_servisleri.json"
        )
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as dosya:
                return json.load(dosya)
        except (FileNotFoundError, json.JSONDecodeError):
            konsol.print("[bold red][!] eposta_servisleri.json yüklenemedi![/]")
            return {"servisler": [], "mx_kontrol": {"populer_saglayicilar": {}}}

    def analiz_et(self, eposta: str) -> Dict:
        """e-posta adresi üzerinde kapsamlı analiz yapar"""
        konsol.print(
            Panel(
                f"[bold white]E-Posta:[/] [bold green]{eposta}[/]",
                title="[bold cyan] E-Posta İstihbaratı[/]",
                border_style="cyan",
            )
        )

        self.sonuclar = {
            "eposta": eposta,
            "gecerli_format": False,
            "alan_adi": "",
            "kullanici": "",
            "saglayici": "",
            "mx_kayitlari": [],
            "gravatar": None,
            "github_hesaplari": [],
            "sizinti_bilgisi": [],
            "servis_kontrolleri": [],
        }

        # 1. format doğrulama
        if not self._format_dogrula(eposta):
            konsol.print("[bold red][-] Geçersiz e-posta formatı![/]")
            return self.sonuclar

        self.sonuclar["gecerli_format"] = True
        parcalar = eposta.split("@")
        self.sonuclar["kullanici"] = parcalar[0]
        self.sonuclar["alan_adi"] = parcalar[1]

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            console=konsol,
        ) as ilerleme:
            # 2. mx kayıt kontrolü
            gorev = ilerleme.add_task(" mx kayıtları kontrol ediliyor...", total=None)
            self._mx_kontrol(parcalar[1])
            ilerleme.update(gorev, description="[green][+] mx kayıtları kontrol edildi[/]")

            # 3. e-posta sağlayıcı tespiti
            gorev2 = ilerleme.add_task(" e-posta sağlayıcı tespit ediliyor...", total=None)
            self._saglayici_tespit(parcalar[1])
            ilerleme.update(gorev2, description="[green][+] sağlayıcı tespit edildi[/]")

            # 4. gravatar kontrolü
            gorev3 = ilerleme.add_task("  gravatar kontrol ediliyor...", total=None)
            self._gravatar_kontrol(eposta)
            ilerleme.update(gorev3, description="[green][+] gravatar kontrol edildi[/]")

            # 5. github e-posta araması
            gorev4 = ilerleme.add_task(" github'da aranıyor...", total=None)
            self._github_ara(eposta)
            ilerleme.update(gorev4, description="[green][+] github araması tamamlandı[/]")

            # 6. emailrep.io kontrolü
            gorev5 = ilerleme.add_task(" e-posta itibar kontrolü yapılıyor...", total=None)
            self._emailrep_kontrol(eposta)
            ilerleme.update(gorev5, description="[green][+] itibar kontrolü tamamlandı[/]")

        self._sonuclari_goster()
        return self.sonuclar

    @staticmethod
    def _format_dogrula(eposta: str) -> bool:
        """e-posta formatını doğrular"""
        desen = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(desen, eposta))

    def _mx_kontrol(self, alan_adi: str):
        """alan adının mx kayıtlarını kontrol eder"""
        if not DNS_MEVCUT:
            self.sonuclar["mx_kayitlari"] = ["dns kütüphanesi bulunamadı"]
            return

        try:
            mx_kayitlari = dns.resolver.resolve(alan_adi, "MX")
            for kayit in mx_kayitlari:
                self.sonuclar["mx_kayitlari"].append({
                    "sunucu": str(kayit.exchange).rstrip("."),
                    "oncelik": kayit.preference
                })
        except dns.resolver.NoAnswer:
            self.sonuclar["mx_kayitlari"] = [{"sunucu": "mx kaydı bulunamadı", "oncelik": 0}]
        except dns.resolver.NXDOMAIN:
            self.sonuclar["mx_kayitlari"] = [{"sunucu": "alan adı mevcut değil", "oncelik": 0}]
        except Exception:
            self.sonuclar["mx_kayitlari"] = [{"sunucu": "sorgu başarısız", "oncelik": 0}]

    def _saglayici_tespit(self, alan_adi: str):
        """e-posta sağlayıcısını tespit eder"""
        populer = self.servisler.get("mx_kontrol", {}).get("populer_saglayicilar", {})

        # önce doğrudan alan adı eşleşmesi kontrol et
        if alan_adi.lower() in populer:
            self.sonuclar["saglayici"] = populer[alan_adi.lower()]
            return

        # mx kayıtlarından tespit et
        for mx in self.sonuclar.get("mx_kayitlari", []):
            if isinstance(mx, dict):
                sunucu = mx.get("sunucu", "").lower()
                if "google" in sunucu or "gmail" in sunucu:
                    self.sonuclar["saglayici"] = "Google Workspace / Gmail"
                    return
                elif "outlook" in sunucu or "microsoft" in sunucu:
                    self.sonuclar["saglayici"] = "Microsoft 365 / Outlook"
                    return
                elif "yahoo" in sunucu:
                    self.sonuclar["saglayici"] = "Yahoo Mail"
                    return
                elif "yandex" in sunucu:
                    self.sonuclar["saglayici"] = "Yandex Mail"
                    return
                elif "protonmail" in sunucu or "proton" in sunucu:
                    self.sonuclar["saglayici"] = "ProtonMail"
                    return

        self.sonuclar["saglayici"] = "bilinmiyor / özel sunucu"

    def _gravatar_kontrol(self, eposta: str):
        """gravatar profilini kontrol eder"""
        # gravatar md5 hash kullanır
        eposta_hash = hashlib.md5(eposta.strip().lower().encode()).hexdigest()
        url = f"https://www.gravatar.com/avatar/{eposta_hash}?d=404"

        try:
            yanit = requests.get(url, timeout=10)
            if yanit.status_code == 200:
                self.sonuclar["gravatar"] = {
                    "bulundu": True,
                    "profil_url": f"https://gravatar.com/{eposta_hash}",
                    "avatar_url": f"https://www.gravatar.com/avatar/{eposta_hash}"
                }
            else:
                self.sonuclar["gravatar"] = {"bulundu": False}
        except requests.RequestException:
            self.sonuclar["gravatar"] = {"bulundu": False, "hata": "bağlantı hatası"}

    def _github_ara(self, eposta: str):
        """github'da e-posta ile kullanıcı arar"""
        url = f"https://api.github.com/search/users?q={eposta}+in:email"
        basliklar = {
            "User-Agent": "enquiry-osint",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            yanit = requests.get(url, headers=basliklar, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                for kullanici in veri.get("items", []):
                    self.sonuclar["github_hesaplari"].append({
                        "kullanici_adi": kullanici.get("login"),
                        "profil_url": kullanici.get("html_url"),
                        "avatar_url": kullanici.get("avatar_url"),
                    })
        except requests.RequestException:
            pass

    def _emailrep_kontrol(self, eposta: str):
        """emailrep.io ile e-posta itibarını kontrol eder"""
        url = f"https://emailrep.io/{eposta}"
        basliklar = {
            "User-Agent": "enquiry-osint",
            "Accept": "application/json"
        }

        try:
            yanit = requests.get(url, headers=basliklar, timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                self.sonuclar["itibar"] = {
                    "itibar": veri.get("reputation", "bilinmiyor"),
                    "supheli": veri.get("suspicious", False),
                    "referanslar": veri.get("references", 0),
                    "detaylar": veri.get("details", {}),
                }
        except requests.RequestException:
            self.sonuclar["itibar"] = {"itibar": "kontrol edilemedi"}

    def _sonuclari_goster(self):
        """sonuçları terminal ekranında gösterir"""
        # temel bilgiler
        tablo = Table(
            title=" E-Posta Analiz Sonuçları",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
            title_style="bold cyan",
        )
        tablo.add_column("Bilgi", style="bold white", min_width=20)
        tablo.add_column("Değer", style="green", min_width=40)

        tablo.add_row("E-Posta", self.sonuclar["eposta"])
        tablo.add_row("Kullanıcı", self.sonuclar["kullanici"])
        tablo.add_row("Alan Adı", self.sonuclar["alan_adi"])
        tablo.add_row("Sağlayıcı", self.sonuclar.get("saglayici", "bilinmiyor"))
        tablo.add_row("Format Geçerli", "[+] evet" if self.sonuclar["gecerli_format"] else "[-] hayır")

        konsol.print()
        konsol.print(tablo)

        # mx kayıtları
        if self.sonuclar.get("mx_kayitlari"):
            mx_tablo = Table(
                title=" MX Kayıtları",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow",
            )
            mx_tablo.add_column("Sunucu", style="white")
            mx_tablo.add_column("Öncelik", style="cyan")

            for kayit in self.sonuclar["mx_kayitlari"]:
                if isinstance(kayit, dict):
                    mx_tablo.add_row(
                        kayit.get("sunucu", "-"),
                        str(kayit.get("oncelik", "-"))
                    )

            konsol.print(mx_tablo)

        # gravatar
        gravatar = self.sonuclar.get("gravatar", {})
        if gravatar and gravatar.get("bulundu"):
            konsol.print(
                Panel(
                    f"[bold green][+] Gravatar profili bulundu![/]\n"
                    f"[white]Profil:[/] {gravatar.get('profil_url', '-')}",
                    title=" Gravatar",
                    border_style="green",
                )
            )

        # github hesapları
        github = self.sonuclar.get("github_hesaplari", [])
        if github:
            konsol.print(
                Panel(
                    "\n".join(
                        f"[bold cyan]@{h['kullanici_adi']}[/] → {h['profil_url']}"
                        for h in github
                    ),
                    title=" GitHub Hesapları",
                    border_style="green",
                )
            )

        # itibar bilgisi
        itibar = self.sonuclar.get("itibar", {})
        if itibar and itibar.get("itibar") != "kontrol edilemedi":
            renk = "green" if itibar.get("itibar") == "high" else "yellow" if itibar.get("itibar") == "medium" else "red"
            konsol.print(
                Panel(
                    f"[bold {renk}]İtibar: {itibar.get('itibar', 'bilinmiyor')}[/]\n"
                    f"[white]Şüpheli: {'[!] evet' if itibar.get('supheli') else '[+] hayır'}[/]\n"
                    f"[white]Referans Sayısı: {itibar.get('referanslar', 0)}[/]",
                    title=" E-Posta İtibarı",
                    border_style=renk,
                )
            )
