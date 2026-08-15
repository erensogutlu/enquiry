#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# telefon numarası analiz modülü
# telefon numarasından ülke, operatör ve hat tipi bilgilerini çıkarır

from typing import Dict, Optional

try:
    # pyrefly: ignore [missing-import]
    import phonenumbers
    # pyrefly: ignore [missing-import]
    from phonenumbers import carrier, geocoder, timezone
    PHONENUMBERS_MEVCUT = True
except ImportError:
    PHONENUMBERS_MEVCUT = False

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

konsol = Console()


class TelefonAnaliz:
    """telefon numarası üzerinde analiz yapan sınıf"""

    def __init__(self):
        self.sonuclar: Dict = {}

    def analiz_et(self, numara: str) -> Dict:
        """telefon numarasını analiz eder"""
        konsol.print(
            Panel(
                f"[bold white]Telefon Numarası:[/] [bold green]{numara}[/]",
                title="[bold cyan] Telefon Numarası Analizi[/]",
                border_style="cyan",
            )
        )

        if not PHONENUMBERS_MEVCUT:
            konsol.print("[bold red][!] phonenumbers kütüphanesi yüklü değil![/]")
            konsol.print("[yellow]Kurulum: pip install phonenumbers[/]")
            return {"hata": "phonenumbers kütüphanesi bulunamadı"}

        self.sonuclar = {
            "girdi": numara,
            "gecerli": False,
            "uluslararasi_format": "",
            "ulusal_format": "",
            "e164_format": "",
            "ulke_kodu": "",
            "ulke": "",
            "operator": "",
            "hat_tipi": "",
            "saat_dilimi": [],
            "olasi_format": True,
        }

        try:
            # numarayı ayrıştır
            ayristirilmis = phonenumbers.parse(numara, None)

            # geçerlilik kontrolü
            self.sonuclar["gecerli"] = phonenumbers.is_valid_number(ayristirilmis)
            self.sonuclar["olasi_format"] = phonenumbers.is_possible_number(ayristirilmis)

            # formatlar
            self.sonuclar["uluslararasi_format"] = phonenumbers.format_number(
                ayristirilmis, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            self.sonuclar["ulusal_format"] = phonenumbers.format_number(
                ayristirilmis, phonenumbers.PhoneNumberFormat.NATIONAL
            )
            self.sonuclar["e164_format"] = phonenumbers.format_number(
                ayristirilmis, phonenumbers.PhoneNumberFormat.E164
            )

            # ülke bilgisi
            self.sonuclar["ulke_kodu"] = f"+{ayristirilmis.country_code}"
            self.sonuclar["ulke"] = geocoder.description_for_number(
                ayristirilmis, "tr"
            ) or geocoder.description_for_number(ayristirilmis, "en") or "bilinmiyor"

            # operatör bilgisi
            self.sonuclar["operator"] = carrier.name_for_number(
                ayristirilmis, "tr"
            ) or carrier.name_for_number(ayristirilmis, "en") or "bilinmiyor"

            # hat tipi
            numara_tipi = phonenumbers.number_type(ayristirilmis)
            tip_esleme = {
                phonenumbers.PhoneNumberType.MOBILE: "mobil",
                phonenumbers.PhoneNumberType.FIXED_LINE: "sabit hat",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: " sabit hat veya mobil",
                phonenumbers.PhoneNumberType.TOLL_FREE: " ücretsiz hat",
                phonenumbers.PhoneNumberType.PREMIUM_RATE: " özel tarife",
                phonenumbers.PhoneNumberType.VOIP: " voip",
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: " kişisel numara",
                phonenumbers.PhoneNumberType.PAGER: " çağrı cihazı",
                phonenumbers.PhoneNumberType.UAN: " evrensel erişim numarası",
                phonenumbers.PhoneNumberType.SHARED_COST: " paylaşımlı maliyet",
            }
            self.sonuclar["hat_tipi"] = tip_esleme.get(numara_tipi, " bilinmiyor")

            # saat dilimi
            try:
                saat_dilimleri = timezone.time_zones_for_number(ayristirilmis)
                self.sonuclar["saat_dilimi"] = list(saat_dilimleri) if saat_dilimleri else ["bilinmiyor"]
            except Exception:
                self.sonuclar["saat_dilimi"] = ["tespit edilemedi"]

        except phonenumbers.NumberParseException as hata:
            self.sonuclar["hata"] = f"numara ayrıştırılamadı: {str(hata)}"
            konsol.print(f"[bold red][-] Hata: {str(hata)}[/]")
            konsol.print("[yellow] İpucu: numarayı uluslararası formatta girin (örn: +905551234567)[/]")
            return self.sonuclar

        self._sonuclari_goster()
        return self.sonuclar

    def _sonuclari_goster(self):
        """sonuçları terminal ekranında gösterir"""
        tablo = Table(
            title=" Telefon Numarası Analiz Sonuçları",
            show_header=True,
            header_style="bold cyan",
            border_style="cyan",
            title_style="bold cyan",
        )
        tablo.add_column("Bilgi", style="bold white", min_width=22)
        tablo.add_column("Değer", style="green", min_width=35)

        # geçerlilik durumu
        gecerli_ikon = "[+] geçerli" if self.sonuclar["gecerli"] else "[-] geçersiz"
        tablo.add_row("Geçerlilik", gecerli_ikon)

        tablo.add_row("Uluslararası Format", self.sonuclar.get("uluslararasi_format", "-"))
        tablo.add_row("Ulusal Format", self.sonuclar.get("ulusal_format", "-"))
        tablo.add_row("E.164 Format", self.sonuclar.get("e164_format", "-"))
        tablo.add_row("Ülke Kodu", self.sonuclar.get("ulke_kodu", "-"))
        tablo.add_row("Ülke / Bölge", self.sonuclar.get("ulke", "-"))
        tablo.add_row("Operatör", self.sonuclar.get("operator", "-"))
        tablo.add_row("Hat Tipi", self.sonuclar.get("hat_tipi", "-"))
        tablo.add_row("Saat Dilimi", ", ".join(self.sonuclar.get("saat_dilimi", ["-"])))

        konsol.print()
        konsol.print(tablo)

        # ek bilgi paneli
        if self.sonuclar.get("gecerli"):
            konsol.print(
                Panel(
                    "[bold green][+] Numara geçerli ve aktif bir formatta.[/]\n"
                    "[dim]not: operatör bilgisi numara taşınabilirliği nedeniyle farklı olabilir.[/]",
                    border_style="green",
                )
            )
        else:
            konsol.print(
                Panel(
                    "[bold red][-] Numara geçersiz veya tanınmayan bir formatta.[/]\n"
                    "[dim]ipucu: numarayı + ile başlayan uluslararası formatta girin.[/]",
                    border_style="red",
                )
            )
