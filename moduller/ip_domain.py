#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ip / domain analiz modülü
# ip adresi veya domain üzerinden whois, dns, geoip ve port bilgilerini toplar

import io
import json
import os
import re
import socket
import sys
from typing import Dict, List, Optional

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    # pyrefly: ignore [missing-import]
    import whois
    WHOIS_MEVCUT = True
except ImportError:
    WHOIS_MEVCUT = False

try:
    # pyrefly: ignore [missing-import]
    import dns.resolver
    DNS_MEVCUT = True
except ImportError:
    DNS_MEVCUT = False

konsol = Console()


class IpDomainAnaliz:
    """ip adresi veya domain üzerinde analiz yapan sınıf"""

    def __init__(self):
        self.sonuclar: Dict = {}

    def analiz_et(self, hedef: str) -> Dict:
        """ip adresi veya domain analizi yapar"""
        konsol.print(
            Panel(
                f"[bold white]Hedef:[/] [bold green]{hedef}[/]",
                title="[bold cyan] IP / Domain Analizi[/]",
                border_style="cyan",
            )
        )

        # hedefin ip mi domain mi olduğunu belirle
        ip_mi = self._ip_mi(hedef)
        hedef_tipi = "ip" if ip_mi else "domain"

        self.sonuclar = {
            "hedef": hedef,
            "tip": hedef_tipi,
            "ip_adresi": hedef if ip_mi else "",
            "domain": hedef if not ip_mi else "",
            "whois": {},
            "dns_kayitlari": {},
            "geoip": {},
            "acik_portlar": [],
            "alt_domainler": [],
            "ters_dns": "",
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            console=konsol,
        ) as ilerleme:
            # 1. domain ise ip adresini çöz
            if not ip_mi:
                gorev = ilerleme.add_task(" ip adresi çözümleniyor...", total=None)
                self._ip_coz(hedef)
                ilerleme.update(gorev, description="[green][+] ip adresi çözümlendi[/]")

            # 2. ip ise ters dns sorgusu
            if ip_mi:
                gorev_ters = ilerleme.add_task(" ters dns sorgusu yapılıyor...", total=None)
                self._ters_dns(hedef)
                ilerleme.update(gorev_ters, description="[green][+] ters dns sorgusu tamamlandı[/]")

            # 3. whois sorgusu
            gorev2 = ilerleme.add_task(" whois sorgusu yapılıyor...", total=None)
            self._whois_sorgula(hedef)
            ilerleme.update(gorev2, description="[green][+] whois sorgusu tamamlandı[/]")

            # 4. dns kayıtları (domain için)
            if not ip_mi:
                gorev3 = ilerleme.add_task(" dns kayıtları sorgulanıyor...", total=None)
                self._dns_sorgula(hedef)
                ilerleme.update(gorev3, description="[green][+] dns kayıtları sorgulandı[/]")

            # 5. geoip bilgisi
            gorev4 = ilerleme.add_task("  geoip bilgisi alınıyor...", total=None)
            ip_hedef = self.sonuclar.get("ip_adresi") or hedef
            self._geoip_sorgula(ip_hedef)
            ilerleme.update(gorev4, description="[green][+] geoip bilgisi alındı[/]")

            # 6. temel port tarama
            gorev5 = ilerleme.add_task(" temel portlar taranıyor...", total=None)
            ip_hedef = self.sonuclar.get("ip_adresi") or hedef
            self._port_tara(ip_hedef)
            ilerleme.update(gorev5, description="[green][+] port taraması tamamlandı[/]")

        self._sonuclari_goster()
        return self.sonuclar

    @staticmethod
    def _ip_mi(hedef: str) -> bool:
        """hedefin ip adresi olup olmadığını kontrol eder"""
        # ipv4 deseni
        ipv4_deseni = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_deseni, hedef):
            parcalar = hedef.split(".")
            return all(0 <= int(p) <= 255 for p in parcalar)
        return False

    def _ip_coz(self, domain: str):
        """domain adresini ip adresine çözer"""
        try:
            ip = socket.gethostbyname(domain)
            self.sonuclar["ip_adresi"] = ip
        except socket.gaierror:
            self.sonuclar["ip_adresi"] = "çözümlenemedi"

    def _ters_dns(self, ip: str):
        """ip adresinden domain adına ters dns sorgusu yapar"""
        try:
            sonuc = socket.gethostbyaddr(ip)
            self.sonuclar["ters_dns"] = sonuc[0]
        except (socket.herror, socket.gaierror):
            self.sonuclar["ters_dns"] = "bulunamadı"

    def _whois_sorgula(self, hedef: str):
        """whois sorgusu yapar"""
        if not WHOIS_MEVCUT:
            self.sonuclar["whois"] = {"hata": "python-whois kütüphanesi yüklü değil"}
            return

        try:
            # whois kütüphanesinin stderr'e yazdığı hata mesajlarını bastır
            eski_stderr = sys.stderr
            sys.stderr = io.StringIO()
            try:
                w = whois.whois(hedef)
            finally:
                sys.stderr = eski_stderr

            self.sonuclar["whois"] = {
                "domain_adi": str(w.domain_name) if w.domain_name else "-",
                "kayit_kurumu": str(w.registrar) if w.registrar else "-",
                "olusturulma_tarihi": str(w.creation_date) if w.creation_date else "-",
                "guncelleme_tarihi": str(w.updated_date) if w.updated_date else "-",
                "bitis_tarihi": str(w.expiration_date) if w.expiration_date else "-",
                "isim_sunuculari": [str(ns) for ns in w.name_servers] if w.name_servers else [],
                "durum": str(w.status) if w.status else "-",
                "ulke": str(w.country) if w.country else "-",
                "organizasyon": str(w.org) if w.org else "-",
            }
        except Exception as hata:
            self.sonuclar["whois"] = {"hata": f"sorgu başarısız: {str(hata)[:50]}"}

    def _dns_sorgula(self, domain: str):
        """dns kayıtlarını sorgular"""
        if not DNS_MEVCUT:
            self.sonuclar["dns_kayitlari"] = {"hata": "dnspython kütüphanesi yüklü değil"}
            return

        kayit_turleri = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
        dns_sonuclari = {}

        for tur in kayit_turleri:
            try:
                yanitlar = dns.resolver.resolve(domain, tur)
                kayitlar = []
                for yanit in yanitlar:
                    kayitlar.append(str(yanit).rstrip("."))
                dns_sonuclari[tur] = kayitlar
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                dns_sonuclari[tur] = []
            except Exception:
                dns_sonuclari[tur] = []

        self.sonuclar["dns_kayitlari"] = dns_sonuclari

    def _geoip_sorgula(self, ip: str):
        """ücretsiz geoip api ile konum bilgisi alır"""
        if ip == "çözümlenemedi":
            self.sonuclar["geoip"] = {"hata": "ip adresi çözümlenemedi"}
            return

        try:
            yanit = requests.get(f"http://ip-api.com/json/{ip}?lang=tr", timeout=10)
            if yanit.status_code == 200:
                veri = yanit.json()
                if veri.get("status") == "success":
                    self.sonuclar["geoip"] = {
                        "ulke": veri.get("country", "-"),
                        "ulke_kodu": veri.get("countryCode", "-"),
                        "bolge": veri.get("regionName", "-"),
                        "sehir": veri.get("city", "-"),
                        "posta_kodu": veri.get("zip", "-"),
                        "enlem": veri.get("lat", 0),
                        "boylam": veri.get("lon", 0),
                        "saat_dilimi": veri.get("timezone", "-"),
                        "isp": veri.get("isp", "-"),
                        "organizasyon": veri.get("org", "-"),
                        "as_bilgisi": veri.get("as", "-"),
                    }
                else:
                    self.sonuclar["geoip"] = {"hata": "sorgu başarısız"}
        except requests.RequestException:
            self.sonuclar["geoip"] = {"hata": "bağlantı hatası"}

    def _port_tara(self, ip: str, zaman_asimi: float = 1.0):
        """temel portları tarar"""
        if ip == "çözümlenemedi":
            return

        # en yaygın portlar
        portlar = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
        }

        for port, servis in portlar.items():
            try:
                soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soket.settimeout(zaman_asimi)
                sonuc = soket.connect_ex((ip, port))
                if sonuc == 0:
                    self.sonuclar["acik_portlar"].append({
                        "port": port,
                        "servis": servis,
                        "durum": "açık"
                    })
                soket.close()
            except (socket.timeout, socket.error):
                pass

    def _sonuclari_goster(self):
        """sonuçları terminal ekranında gösterir"""
        # temel bilgiler
        temel_tablo = Table(
            title=" Hedef Bilgileri",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
        )
        temel_tablo.add_column("Bilgi", style="bold white", min_width=18)
        temel_tablo.add_column("Değer", style="green", min_width=40)

        temel_tablo.add_row("Hedef", self.sonuclar["hedef"])
        temel_tablo.add_row("Tip", self.sonuclar["tip"].upper())
        temel_tablo.add_row("IP Adresi", self.sonuclar.get("ip_adresi", "-"))
        if self.sonuclar.get("ters_dns"):
            temel_tablo.add_row("Ters DNS", self.sonuclar["ters_dns"])

        konsol.print()
        konsol.print(temel_tablo)

        # whois bilgileri
        whois_bilgi = self.sonuclar.get("whois", {})
        if whois_bilgi and "hata" not in whois_bilgi:
            # whois satırlarını topla, boşsa tabloyu gösterme
            whois_satirlari = []
            alan_isimleri = {
                "domain_adi": "Domain Adı",
                "kayit_kurumu": "Kayıt Kurumu",
                "olusturulma_tarihi": "Oluşturulma Tarihi",
                "guncelleme_tarihi": "Güncelleme Tarihi",
                "bitis_tarihi": "Bitiş Tarihi",
                "ulke": "Ülke",
                "organizasyon": "Organizasyon",
                "durum": "Durum",
            }

            for anahtar, baslik in alan_isimleri.items():
                deger = whois_bilgi.get(anahtar, "-")
                if deger and deger != "-":
                    whois_satirlari.append((baslik, str(deger)))

            # isim sunucuları
            isim_sunuculari = whois_bilgi.get("isim_sunuculari", [])
            if isim_sunuculari:
                whois_satirlari.append(("İsim Sunucuları", "\n".join(isim_sunuculari)))

            # sadece veri varsa tabloyu göster
            if whois_satirlari:
                whois_tablo = Table(
                    title=" WHOIS Bilgileri",
                    show_header=True,
                    header_style="bold yellow",
                    border_style="yellow",
                )
                whois_tablo.add_column("Alan", style="bold white", min_width=18)
                whois_tablo.add_column("Değer", style="green", min_width=40)

                for baslik, deger in whois_satirlari:
                    whois_tablo.add_row(baslik, deger)

                konsol.print(whois_tablo)
            else:
                konsol.print(
                    Panel(
                        "[dim]whois bilgisi bu hedef için mevcut değil.[/]",
                        title=" WHOIS",
                        border_style="dim",
                    )
                )

        # dns kayıtları
        dns_kayitlari = self.sonuclar.get("dns_kayitlari", {})
        if dns_kayitlari and "hata" not in dns_kayitlari:
            bos_olmayan = {k: v for k, v in dns_kayitlari.items() if v}
            if bos_olmayan:
                dns_tablo = Table(
                    title=" DNS Kayıtları",
                    show_header=True,
                    header_style="bold magenta",
                    border_style="magenta",
                )
                dns_tablo.add_column("Tür", style="bold cyan", min_width=8)
                dns_tablo.add_column("Değer", style="white", min_width=40)

                for tur, kayitlar in bos_olmayan.items():
                    for kayit in kayitlar:
                        dns_tablo.add_row(tur, kayit)

                konsol.print(dns_tablo)

        # geoip bilgisi
        geoip = self.sonuclar.get("geoip", {})
        if geoip and "hata" not in geoip:
            geoip_tablo = Table(
                title="  GeoIP Konum Bilgisi",
                show_header=True,
                header_style="bold green",
                border_style="green",
            )
            geoip_tablo.add_column("Bilgi", style="bold white", min_width=18)
            geoip_tablo.add_column("Değer", style="green", min_width=35)

            alan_isimleri = {
                "ulke": " Ülke",
                "bolge": " Bölge",
                "sehir": " Şehir",
                "posta_kodu": " Posta Kodu",
                "saat_dilimi": " Saat Dilimi",
                "isp": " ISP",
                "organizasyon": " Organizasyon",
                "as_bilgisi": " AS Bilgisi",
            }

            for anahtar, baslik in alan_isimleri.items():
                deger = geoip.get(anahtar, "-")
                if deger and str(deger) != "-":
                    geoip_tablo.add_row(baslik, str(deger))

            # koordinatlar
            enlem = geoip.get("enlem", 0)
            boylam = geoip.get("boylam", 0)
            if enlem and boylam:
                geoip_tablo.add_row(
                    " Koordinatlar",
                    f"{enlem}, {boylam}"
                )

            konsol.print(geoip_tablo)

        # açık portlar
        acik_portlar = self.sonuclar.get("acik_portlar", [])
        if acik_portlar:
            port_tablo = Table(
                title=" Açık Portlar",
                show_header=True,
                header_style="bold red",
                border_style="red",
            )
            port_tablo.add_column("Port", style="bold cyan", min_width=8)
            port_tablo.add_column("Servis", style="yellow", min_width=15)
            port_tablo.add_column("Durum", style="green", min_width=10)

            for port in acik_portlar:
                port_tablo.add_row(
                    str(port["port"]),
                    port["servis"],
                    f"[green]{port['durum']}[/]"
                )

            konsol.print(port_tablo)
        else:
            konsol.print(
                Panel(
                    "[dim]taranan portlarda açık port bulunamadı veya hedef yanıt vermedi.[/]",
                    title=" Port Tarama",
                    border_style="dim",
                )
            )
